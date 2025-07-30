import json

from NEMO.typing import QuerySetType
from NEMO.utilities import BasicDisplayTable, export_format_datetime
from django import forms
from django.contrib import admin
from django.template.defaultfilters import yesno
from django.utils.safestring import mark_safe

from NEMO_rs2_access.models import Cardholder, ErrorLog, Reader, UserPreferencesDefaultProject
from NEMO_rs2_access.rs2 import sync_access, sync_readers


@admin.action(description="Sync all readers with RS2")
def admin_sync_readers(modeladmin, request, queryset):
    sync_readers()


@admin.action(description="Sync user access RS2")
def admin_sync_access(modeladmin, request, queryset):
    sync_access()


@admin.action(description="Export selected error logs")
def admin_export_error_logs(modeladmin, request, queryset: QuerySetType[ErrorLog]):
    table_result = BasicDisplayTable()
    table_result.add_header(("type", "Type"))
    table_result.add_header(("created", "Created"))
    table_result.add_header(("description", "Description"))
    table_result.add_header(("cardholder_value", "Cardholder value"))
    table_result.add_header(("cardholder_name", "Cardholder name"))
    table_result.add_header(("event_time", "Event time"))
    table_result.add_header(("reader", "Reader"))
    table_result.add_header(("fixed", "Fixed"))
    for error_log in queryset:
        table_result.add_row(
            {
                "type": error_log.get_error_type_display(),
                "created": error_log.created,
                "description": error_log.description,
                "cardholder_value": error_log.cardholder_value,
                "cardholder_name": error_log.get_cardholder_name(),
                "event_time": error_log.get_event_time(),
                "reader": error_log.get_reader(),
                "fixed": error_log.fixed(),
            }
        )

    filename = f"error_logs_{export_format_datetime()}.csv"
    response = table_result.to_csv()
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


class UserPreferencesDefaultProjectAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_preferences_id:
            self.fields["user_preferences"].disabled = True
            self.fields["default_project"].queryset = self.instance.user_preferences.user.active_projects()

    class Meta:
        model = UserPreferencesDefaultProject
        fields = "__all__"


@admin.register(UserPreferencesDefaultProject)
class UserPreferencesDefaultProjectAdmin(admin.ModelAdmin):
    list_display = ["get_user", "default_project"]
    list_filter = (("default_project", admin.RelatedOnlyFieldListFilter),)
    search_fields = [
        "user_preferences__user__first_name",
        "user_preferences__user__last_name",
        "user_preferences__user__username",
    ]
    form = UserPreferencesDefaultProjectAdminForm

    @admin.display(description="User", ordering="user_preferences__user")
    def get_user(self, obj: UserPreferencesDefaultProject):
        return obj.user_preferences.user


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ["reader_id", "reader_name", "site_id", "area", "reader_type", "installed", "last_updated"]
    list_filter = [
        ("area", admin.RelatedOnlyFieldListFilter),
        "reader_type",
        "installed",
        "site_id",
    ]
    readonly_fields = ["reader_id", "reader_name", "site_id", "installed", "get_data", "created", "last_updated"]
    exclude = ["data"]
    search_fields = ["reader_name", "area__name"]
    actions = [admin_sync_readers, admin_sync_access]

    @admin.display(description="Data", ordering="data")
    def get_data(self, obj: Reader):
        result = json.dumps(obj.data, indent=4, sort_keys=True)
        result_str = f"<pre>{result}</pre>"
        return mark_safe(result_str)


@admin.register(Cardholder)
class CardholderAdmin(admin.ModelAdmin):
    list_display = ["cardholder_id", "cardholder_name", "key_name", "key_value", "created", "last_updated"]
    readonly_fields = ["created", "last_updated"]


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = [
        "created",
        "get_error_type_display",
        "get_event_time",
        "get_reader",
        "cardholder_value",
        "get_cardholder_name",
        "user",
        "appears_fixed",
    ]
    readonly_fields = ["event_data"]
    list_filter = ["error_type"]
    date_hierarchy = "created"
    actions = [admin_export_error_logs]

    @admin.display(description="Appears fixed")
    def appears_fixed(self, error_log: ErrorLog) -> str:
        return yesno(error_log.fixed(), "Yes,No,")
