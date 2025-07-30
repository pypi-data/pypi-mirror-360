import json
from datetime import datetime
from typing import Optional

from NEMO.models import Area, Project, User, UserPreferences
from NEMO.utilities import format_datetime
from NEMO.views.constants import CHAR_FIELD_MAXIMUM_LENGTH
from django.db import models


class UserPreferencesDefaultProject(models.Model):
    user_preferences = models.OneToOneField(UserPreferences, on_delete=models.CASCADE, related_name="default_project")
    default_project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_preferences.user) + " - " + str(self.default_project or "")

    class Meta:
        verbose_name = "Default project"


class Reader(models.Model):
    class ReaderType(object):
        ENTRANCE = 1
        EXIT = 2
        Choices = (
            (ENTRANCE, "Entrance"),
            (EXIT, "Exit"),
        )

    reader_id = models.CharField(max_length=250, unique=True)
    site_id = models.CharField(max_length=250)
    reader_name = models.CharField(max_length=250)
    installed = models.BooleanField()
    data = models.JSONField()
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.CASCADE)
    reader_type = models.PositiveIntegerField(null=True, choices=ReaderType.Choices)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reader_name


class Cardholder(models.Model):
    cardholder_id = models.CharField(max_length=250, unique=True)
    cardholder_name = models.CharField(max_length=250, blank=True, null=True)
    key_name = models.CharField(max_length=250)
    key_value = models.CharField(max_length=250)
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cardholder_id


class ErrorLog(models.Model):
    class ErrorType(object):
        GENERAL = 1
        NO_ACTIVE_PROJECTS = 2
        NO_MATCHING_USER = 3
        LOGOUT_WITHOUT_RECORD = 4
        ALREADY_LOGGED_IN = 5
        Choices = (
            (GENERAL, "General"),
            (NO_ACTIVE_PROJECTS, "No active projects"),
            (NO_MATCHING_USER, "No matching user"),
            (LOGOUT_WITHOUT_RECORD, "Logout without record"),
            (ALREADY_LOGGED_IN, "Login attempt while already logged in"),
        )

    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    error_type = models.PositiveIntegerField(default=ErrorType.GENERAL, choices=ErrorType.Choices)
    cardholder_value = models.CharField(null=True, blank=True, max_length=CHAR_FIELD_MAXIMUM_LENGTH)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    event_data = models.TextField(null=True, blank=True)

    def fixed(self):
        if self.error_type == ErrorLog.ErrorType.NO_ACTIVE_PROJECTS:
            try:
                if self.user:
                    return self.user.active_projects().exists()
            except User.DoesNotExist:
                pass
        elif self.error_type == ErrorLog.ErrorType.NO_MATCHING_USER:
            try:
                from NEMO_rs2_access.rs2 import find_user

                return find_user(self.cardholder_value) is not None
            except:
                pass

    def get_reader(self) -> Optional[Reader]:
        if self.event_data:
            try:
                data = json.loads(self.event_data)
                return Reader.objects.get(reader_id=data["SourceId"])
            except:
                pass

    def get_cardholder_name(self) -> Optional[str]:
        if self.event_data:
            try:
                data = json.loads(self.event_data)
                return data["Cardholder"]
            except:
                pass

    def get_event_time(self) -> Optional[datetime]:
        if self.event_data:
            try:
                data = json.loads(self.event_data)
                return datetime.fromisoformat(data["EventDate"]).astimezone()
            except:
                pass

    def __str__(self):
        return f"{self.get_error_type_display()} error on {format_datetime(self.created)}"

    class Meta:
        ordering = ["-created"]
