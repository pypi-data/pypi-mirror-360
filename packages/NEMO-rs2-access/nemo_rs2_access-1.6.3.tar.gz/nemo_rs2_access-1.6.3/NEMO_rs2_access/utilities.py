from argparse import Namespace
from copy import copy

from django.conf import settings

from NEMO_rs2_access import app_settings


def get_rs2_settings():
    rs2_settings = copy(app_settings.DEFAULT)
    rs2_settings.update(settings.RS2_ACCESS)
    return Namespace(**rs2_settings)


def get_event_id(event: dict):
    # Create our own, hopefully unique id: date_readerId_userId
    return f"{event['EventDate']}_{event['SourceId']}_{event['CardholderId']}"


def find_user(cardholder_sync_value):
    from NEMO.models import User

    rs2_settings = get_rs2_settings()
    return User.objects.filter(**{rs2_settings.nemo_user_sync_field: cardholder_sync_value}).first()


def find_in_json(element, json):
    keys = element.split(".")
    rv = json
    for key in keys:
        rv = rv[key]
    return rv
