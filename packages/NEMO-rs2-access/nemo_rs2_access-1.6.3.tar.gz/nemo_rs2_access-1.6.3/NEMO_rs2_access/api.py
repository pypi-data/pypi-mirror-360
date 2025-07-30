from argparse import Namespace
from datetime import datetime, timedelta
from typing import Dict, List

from NEMO.models import Area
from NEMO.utilities import export_format_datetime, quiet_int
from django.utils import timezone
from drf_excel.mixins import XLSXFileMixin
from rest_framework import status
from rest_framework.fields import CharField, DateTimeField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from NEMO_rs2_access.models import Reader
from NEMO_rs2_access.rs2 import get_cardholder_property, get_sorted_reader_events


class LastEntriesSerializer(Serializer):
    cardholder_name = CharField(read_only=True)
    cardholder_id = CharField(read_only=True)
    cardholder_user_text1 = CharField(read_only=True)
    card_number = CharField(read_only=True)
    card_id = CharField(read_only=True)
    login_time = DateTimeField(read_only=True)
    reader_id = CharField(read_only=True)
    reader_location = CharField(read_only=True)
    area_name = CharField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        fields = "__all__"


class LastEntriesViewSet(XLSXFileMixin, GenericViewSet):
    serializer_class = LastEntriesSerializer
    since_minutes = None

    def check_permissions(self, request):
        pass

    def list(self, request, *args, **kwargs):
        self.since_minutes = quiet_int(self.request.GET.get("last", None), None)
        if self.since_minutes is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "last": "This field is required. Please specify the number of minutes to check last users entries for"
                },
            )
        try:
            queryset = self.get_queryset()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        since = timezone.now() - timedelta(minutes=self.since_minutes)

        last_entries = get_last_entries(since)
        last_entries.sort(key=lambda x: x.login_time, reverse=True)
        return last_entries

    def get_filename(self, *args, **kwargs):
        return f"last_entries-{self.since_minutes}.xlsx"


def get_last_entries(since: datetime) -> List:
    last_entries = []
    formatted_since = since.astimezone().replace(tzinfo=None).isoformat(sep="T", timespec="seconds")
    events, readers, cardholders = get_sorted_reader_events(formatted_since, [])
    # cache the text1 value for cardholders
    cardholder_text1_cache = {}
    events_dict: Dict[str, Dict] = {}
    # Put event into a dict by area id, this way the latest event for that area will
    # override the previous one, and we only care about the last entry/exit per area
    for event in events:
        area: Area = readers.get(event["SourceId"]).area
        if area:
            event_date = event["EventDateObject"]
            auto_logout = getattr(area, "auto_logout_time", None)
            # remove events that should have been auto logged out
            if not auto_logout or (event_date + timedelta(minutes=auto_logout) > timezone.now()):
                cardholder_id = event["CardholderId"]
                event["area_name"] = area.name
                text1 = cardholder_text1_cache.get(cardholder_id) or cardholder_text1_cache.setdefault(
                    cardholder_id, get_cardholder_property(cardholder_id, "UserColumns.UserText1", save=False)
                )
                event["user_columns_user_text1"] = text1
                user_location_id = f"{area.id}-{cardholder_id}"
                events_dict[user_location_id] = event
    for event in events_dict.values():
        # Only keep entrance reader types
        if readers.get(event["SourceId"]).reader_type == Reader.ReaderType.ENTRANCE:
            last_entries.append(
                Namespace(
                    **{
                        "cardholder_name": event["Cardholder"].strip(),
                        "cardholder_id": event["CardholderId"],
                        "cardholder_user_text1": event["user_columns_user_text1"],
                        "card_number": event["CardNumber"],
                        "card_id": event["CardId"],
                        "login_time": event["EventDate"],
                        "reader_id": event["SourceId"],
                        "reader_location": event["EventLocation"],
                        "area_name": event["area_name"],
                    }
                )
            )
    return last_entries
