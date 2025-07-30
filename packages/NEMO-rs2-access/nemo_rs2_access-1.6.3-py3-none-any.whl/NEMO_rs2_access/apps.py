from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NemoRs2AccessConfig(AppConfig):
    name = "NEMO_rs2_access"
    verbose_name = "RS2 Access"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        """
        This code will be run when Django starts.
        """
        # Import the place where @replace_function is used otherwise it won't work for management commands
        from NEMO_rs2_access import views

        pass
