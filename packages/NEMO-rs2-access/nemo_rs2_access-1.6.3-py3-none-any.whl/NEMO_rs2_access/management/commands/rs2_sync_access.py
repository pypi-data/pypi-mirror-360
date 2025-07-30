from django.core.management import BaseCommand

from NEMO_rs2_access import rs2


class Command(BaseCommand):
    help = "Run every few minutes to sync up with rs2 access."

    def handle(self, *args, **options):
        rs2.sync_access()
