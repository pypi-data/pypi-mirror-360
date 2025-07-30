from NEMO.decorators import replace_function
from NEMO.forms import UserPreferencesForm
from NEMO.models import User
from NEMO.utilities import render_combine_responses
from NEMO.views.customization import StatusDashboardCustomization
from NEMO.views.status_dashboard import show_staff_status
from NEMO.views.users import user_preferences
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from NEMO_rs2_access.models import UserPreferencesDefaultProject
from NEMO_rs2_access.rs2 import logout, sync_access, sync_readers


@login_required
@require_http_methods(["GET", "POST"])
def custom_user_preferences(request):
    original_response = user_preferences(request)
    user: User = User.objects.get(pk=request.user.id)
    if request.method == "POST":
        if original_form_is_valid(request, user):
            default_project = request.POST.get("default_project", "")
            UserPreferencesDefaultProject.objects.update_or_create(
                user_preferences=user.preferences, defaults={"default_project_id": default_project or None}
            )
            messages.success(request, "Your preferences have been saved")
            return redirect("user_preferences")
    user_default_project = ""
    try:
        user_default_project = user.preferences.default_project.default_project
    except UserPreferencesDefaultProject.DoesNotExist:
        pass
    dictionary = {"user_default_project": user_default_project, "projects": user.active_projects()}
    return render_combine_responses(
        request, original_response, "NEMO_rs2_access/preferences_default_project.html", dictionary
    )


def original_form_is_valid(request, user) -> bool:
    user_view_options = StatusDashboardCustomization.get("dashboard_staff_status_user_view")
    staff_view_options = StatusDashboardCustomization.get("dashboard_staff_status_staff_view")
    user_view = user_view_options if not user.is_staff else staff_view_options if not user.is_facility_manager else ""
    pref_form = UserPreferencesForm(data=request.POST or None, instance=user.preferences)
    if not show_staff_status(request) or user_view == "day":
        pref_form.fields["staff_status_view"].disabled = True
    return pref_form.is_valid()


# Replace NEMO's logout function by our own, so if someone logs out from the dashboard or calendar,
# it will proceed with the rs2 flow, figuring out which project to charge etc.
@replace_function("NEMO.views.area_access.log_out_user")
def new_logout(old_function, user: User):
    logout(user, timezone.now())


@login_required
@require_GET
@permission_required("NEMO.trigger_timed_services", raise_exception=True)
def rs2_sync_reader(request):
    sync_readers()
    return HttpResponse()


@login_required
@require_GET
@permission_required("NEMO.trigger_timed_services", raise_exception=True)
def rs2_sync_access(request):
    sync_access()
    return HttpResponse()
