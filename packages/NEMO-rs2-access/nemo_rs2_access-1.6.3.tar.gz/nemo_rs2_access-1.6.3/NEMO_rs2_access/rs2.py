import datetime
import json
from logging import getLogger
from typing import Dict, List, Optional, Set, Type, Union

import requests
from NEMO.exceptions import NEMOException
from NEMO.models import Area, AreaAccessRecord, Customization, EmailNotificationType, Project, UsageEvent, User
from NEMO.utilities import beginning_of_the_day, distinct_qs_value_list, get_full_url, new_model_copy, send_mail
from NEMO.views.calendar import shorten_reservation
from NEMO.views.customization import EmailsCustomization
from django.db.models import Model
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from requests.auth import HTTPBasicAuth

from NEMO_rs2_access.models import Cardholder, ErrorLog, Reader
from NEMO_rs2_access.sync import sync_model_rest_data
from NEMO_rs2_access.utilities import find_in_json, find_user, get_event_id, get_rs2_settings

rs2_logger = getLogger(__name__)

NEXT_EVENTS_BEGIN_DATE = "rs2_event_begin_date"
LAST_EVENTS_PROCESSED = "rs2_event_last_processed"

READERS_URL = "/Readers"
READERS_HISTORY_URL = READERS_URL + "/{}/EventHistory?beginDate={}"
CARDHOLDERS_URL = "/Cardholders/{}"

reader_mapping = {
    "reader_name": "ReaderName",
    "site_id": "SiteID",
    "installed": "DeviceInstalled",
}


def sync_access():
    rs2_settings = get_rs2_settings()
    buffer_in_seconds = rs2_settings.buffer_in_seconds
    try:
        # default date is beginning of the day today if not set in Customization
        default_date = beginning_of_the_day(datetime.datetime.now(), in_local_timezone=False).isoformat()
        last_event_date_read, created = Customization.objects.get_or_create(
            name=NEXT_EVENTS_BEGIN_DATE, defaults={"value": default_date}
        )
        last_event_processed, created = Customization.objects.get_or_create(
            name=LAST_EVENTS_PROCESSED, defaults={"value": ""}
        )
        last_event_ids_processed = [item.strip() for item in last_event_processed.value.split(",") if item]
        next_event_date: str = last_event_date_read.value
        events, readers, cardholders = get_sorted_reader_events(next_event_date, last_event_ids_processed)
        last_processed_event_index = None
        try:
            for i, event in enumerate(events):
                cardholder_id = event["CardholderId"]
                reader_id = event["SourceId"]
                event_time = event["EventDateObject"]
                reader = readers.get(reader_id)
                cardholder_sync_value = cardholders.get(cardholder_id, None)
                area = reader.area
                if area:
                    event_user = event.get("Cardholder")
                    user = find_user(cardholder_sync_value)
                    if user:
                        login_logout(user, reader, event_time, event)
                    else:
                        message = f"No NEMO matching user found for {rs2_settings.user_sync_field} {cardholder_sync_value} - {event_user} (event at location {reader.reader_name})"
                        add_error_log(
                            message,
                            ErrorLog.ErrorType.NO_MATCHING_USER,
                            cardholder_value=cardholder_sync_value,
                            event_data=event,
                        )
                # Only set next sequence number when we are done with the current event
                next_event_date = event["EventDate"]
                last_processed_event_index = i
        finally:
            if last_processed_event_index is not None:
                # Save the last processed event date and include the buffer
                next_event_date_time_end = datetime.datetime.fromisoformat(next_event_date).astimezone()
                next_event_date_time_start = next_event_date_time_end - datetime.timedelta(seconds=buffer_in_seconds)
                last_event_date_read.value = next_event_date_time_start.replace(tzinfo=None).isoformat(
                    sep="T", timespec="seconds"
                )
                last_event_date_read.save()
                # Use the buffer to find the last events between buffer and next_event_date
                new_last_event_ids_processed = []
                while (
                    last_processed_event_index >= 0
                    and next_event_date_time_start
                    <= events[last_processed_event_index]["EventDateObject"]
                    <= next_event_date_time_end
                ):
                    new_last_event_ids_processed.append(get_event_id(events[last_processed_event_index]))
                    last_processed_event_index -= 1
                last_event_processed.value = ",".join(new_last_event_ids_processed)
                last_event_processed.save()

    except Customization.DoesNotExist:
        message = (
            f"No last sequence number was set in Customization. Please add one with the name '{NEXT_EVENTS_BEGIN_DATE}'"
        )
        add_error_log(message)
        raise NEMOException(msg=message)
    except Exception as e:
        add_error_log(e)


def get_sorted_reader_events(
    begin_date: str, last_event_ids_processed: List[str]
) -> (List[Dict], Dict[int, Reader], Dict[int, str]):
    rs2_settings = get_rs2_settings()
    """
    Get events for all relevant readers
    Then merge them all (since login-logout happen in different readers)
    Finally we need to sort them all to recreate the chronological order of things
    """
    reader_ids = Reader.objects.filter(area__isnull=False).values_list("reader_id", flat=True)
    readers = Reader.objects.in_bulk(id_list=reader_ids, field_name="reader_id")
    cardholder_ids = set()
    cardholder_keys = dict()
    events = []
    for reader_id in readers:
        response = request_get(READERS_HISTORY_URL.format(reader_id, begin_date))
        response.raise_for_status()
        reader_events = response.json()
        for reader_event in reader_events:
            # Skip events that are not relevant
            if reader_event["EventType"] in rs2_settings.relevant_event_types:
                reader_event["SourceId"] = reader_id
                # Skip events we already processed
                if get_event_id(reader_event) not in last_event_ids_processed:
                    reader_event["EventDateObject"] = datetime.datetime.fromisoformat(
                        reader_event["EventDate"]
                    ).astimezone()
                    events.append(reader_event)
                    cardholder_id = reader_event.get("CardholderId", None)
                    if cardholder_id:
                        # If we need to sync cardholder objects, store the id for later use
                        if rs2_settings.cardholder_sync:
                            cardholder_ids.add(cardholder_id)
                        # Otherwise we can just grab the field from the event
                        else:
                            cardholder_keys[cardholder_id] = reader_event.get(rs2_settings.user_sync_field)
    events.sort(key=lambda x: x["EventDateObject"])
    # Now we can deal with cardholders in bulk
    if cardholder_ids:
        key_name = rs2_settings.user_sync_field
        # Grab the ones we already synced before
        for cardholder in Cardholder.objects.filter(cardholder_id__in=cardholder_ids, key_name=key_name):
            cardholder_keys[cardholder.cardholder_id] = cardholder.key_value
        # Fetch the missing ones
        for missing_cardholder_id in cardholder_ids.difference(cardholder_keys.keys()):
            cardholder_keys[missing_cardholder_id] = get_cardholder_property(missing_cardholder_id, key_name)
    return events, readers, cardholder_keys


def get_cardholder_property(cardholder_id: str, key_name, save=True) -> Optional[str]:
    # Request cardholder data from the API and save it, returning the value
    response = request_get(CARDHOLDERS_URL.format(cardholder_id))
    response.raise_for_status()
    rs2_cardholder = response.json()[0]
    value: str = find_in_json(key_name, rs2_cardholder)
    cardholder_name = rs2_cardholder.get("FirstName") + " " + rs2_cardholder.get("LastName")
    if value:
        value = value.strip()
        if save:
            Cardholder.objects.update_or_create(
                cardholder_id=cardholder_id,
                defaults={"cardholder_name": cardholder_name, "key_name": key_name, "key_value": value},
            )
        return value


def sync_readers():
    sync_model_rest(READERS_URL, Reader, "ReaderID", reader_mapping)


def sync_model_rest(url, model_class: Type[Model], remote_id_field_name: str, mapping: Dict):
    sync_model_rest_data(request_get(url).json(), model_class, remote_id_field_name, mapping)


def request_get(url_suffix: str):
    rs2_settings = get_rs2_settings()
    if rs2_settings:
        auth = (
            HTTPBasicAuth(rs2_settings.auth.get("user_id"), rs2_settings.auth.get("password"))
            if getattr(rs2_settings, "auth")
            else None
        )
        headers = {"PublicKey": rs2_settings.public_key}
        timeout = getattr(rs2_settings, "timeout", 30)
        return requests.get(rs2_settings.url + url_suffix, auth=auth, headers=headers, timeout=timeout)
    else:
        return HttpResponseBadRequest("no RS2_ACCESS settings found, please add them to your settings.py")


def login_logout(user: User, reader: Reader, event_time: datetime.datetime = None, event=None):
    if reader.reader_type == Reader.ReaderType.ENTRANCE:
        login(user, reader.area, event_time, event)
    elif reader.reader_type == Reader.ReaderType.EXIT:
        logout(user, event_time, event)


def login(user: User, area: Area, start: datetime.datetime = None, event=None):
    project = user.active_projects().first()
    if project:
        area_access: AreaAccessRecord = user.area_access_record()
        # if user is already logged in the same area, record it in error log
        if area_access and area_access.area == area:
            if get_rs2_settings().record_already_logged_in_as_error:
                message = f"user {user} attempted to login but was already logged in to the {area}"
                add_error_log(message, ErrorLog.ErrorType.ALREADY_LOGGED_IN, user=user, event_data=event)
        # If user is logged in a different area, automatically log him out
        if area_access and area_access.area != area:
            logout(user, start, event)
        # Only log in if not already in the area
        if not area_access or area_access.area != area:
            AreaAccessRecord.objects.create(area=area, customer=user, start=start, project=project)
    else:
        message = f"no active projects found for user {user}, skipping log in to {area}"
        add_error_log(message, ErrorLog.ErrorType.NO_ACTIVE_PROJECTS, user=user, event_data=event)


def logout(user: User, end: datetime.datetime, event=None):
    area_access: AreaAccessRecord = user.area_access_record()
    if area_access:
        for project_id in get_project_ids_to_charge_for_user(user, area_access.start, end, area_access.project_id):
            refresh_access: AreaAccessRecord = AreaAccessRecord.objects.get(pk=area_access.id)
            refresh_access.project_id = project_id
            if not refresh_access.end:
                # update current record
                refresh_access.end = end
                refresh_access.save()
            else:
                # We are creating a copy for each project the user worked on
                new_access = new_model_copy(refresh_access)
                new_access.save()

        # Dealing with reservation and staff charges, to be consistent with NEMO
        shorten_reservation(user, area_access.area, end)
        # Stop charging area access if staff is leaving the area
        staff_charge = user.get_staff_charge()
        if staff_charge:
            try:
                staff_area_access = AreaAccessRecord.objects.get(staff_charge=staff_charge, end=None)
                staff_area_access.end = timezone.now()
                staff_area_access.save()
            except AreaAccessRecord.DoesNotExist:
                pass
    else:
        message = f"user {user} logged out but was not previously logged in to any areas"
        add_error_log(message, ErrorLog.ErrorType.LOGOUT_WITHOUT_RECORD, user=user, event_data=event)


def get_project_ids_to_charge_for_user(
    user: User, start: datetime.datetime, end: datetime.datetime, original_project_id: int
) -> Union[List, Set]:
    """
    Figure out which project to charge for the user, given a datetime
    1. If the user has no active projects, use the same project as for login (unlikely, but possible)
    2. If the user has only one active project, use it
    3. Be smart and check tool usage for this user (non-remote) charge once per account
    4. No tool usage, use default project
    5. No default project, use the first active project by relation id (== first one added)
    """
    # We are using the through relation to get order by relation id, which means ordered by added time (lower id)
    active_through_projects = user.projects.through.objects.filter(
        user_id=user.id, project__active=True, project__account__active=True
    )
    active_through_projects_count = active_through_projects.count()
    # Case #1
    if active_through_projects_count == 0:
        message = (
            f"no active projects found for user {user}, using original project id {original_project_id} for logout"
        )
        add_error_log(message, ErrorLog.ErrorType.NO_ACTIVE_PROJECTS, user=user)
        return [original_project_id]
    # Case #2
    if active_through_projects_count == 1:
        return list(active_through_projects.values_list("project_id", flat=True))
    # Case #3
    ongoing_events = (
        UsageEvent.objects.filter(user=user, end__isnull=True)
        .exclude(remote_work=True)
        .exclude(start__lt=start)
        .exclude(start__gt=end)
    )
    other_events = (
        UsageEvent.objects.filter(user=user, end__isnull=False)
        .exclude(remote_work=True)
        .exclude(start__lt=start, end__lt=start)
        .exclude(start__gt=end, end__gt=end)
    )
    project_ids = list(
        distinct_qs_value_list(ongoing_events, "project_id") | distinct_qs_value_list(other_events, "project_id")
    )
    if project_ids:
        unique_account_project_ids = []
        projects = Project.objects.in_bulk(project_ids)
        already_checked_account_ids = set()
        for project_id, project in projects.items():
            if project.account_id not in already_checked_account_ids:
                unique_account_project_ids.append(project_id)
                already_checked_account_ids.add(project.account_id)
        return unique_account_project_ids
    else:
        # Case #4
        try:
            default_project_id = user.get_preferences().default_project.default_project_id
            if default_project_id:
                if default_project_id in user.active_projects().values_list("id", flat=True):
                    return [default_project_id]
                else:
                    user.get_preferences().default_project.delete()
                    user_office_email = EmailsCustomization.get("user_office_email_address")
                    content = f"Dear {user.get_name()},<br><br>"
                    content += f"You default project was reset because you are not a member of it anymore.<br><br>"
                    content += f'Please go to <a href="{get_full_url(reverse("user_preferences"))}">you preferences page</a> and select a new one.'
                    send_mail(
                        subject=f"Default project reset",
                        content=content,
                        from_email=None,
                        to=user.get_emails(EmailNotificationType.BOTH_EMAILS),
                        cc=[user_office_email],
                    )
        except:
            pass
        # Case #5
        return [active_through_projects.first().project_id]


def add_error_log(
    description: Union[str, Exception],
    error_type: ErrorLog.ErrorType = ErrorLog.ErrorType.GENERAL,
    user=None,
    cardholder_value=None,
    event_data: Dict = None,
):
    if event_data:
        # remove datetime object which is not serializable
        event_data = {key: value for key, value in event_data.items() if key != "EventDateObject"}
    # Force description to str
    ErrorLog.objects.create(
        description=str(description),
        error_type=error_type,
        cardholder_value=cardholder_value,
        user=user,
        event_data=json.dumps(event_data) if event_data else None,
    )
    if isinstance(description, Exception):
        rs2_logger.exception(str(description))
    else:
        rs2_logger.error(description)
