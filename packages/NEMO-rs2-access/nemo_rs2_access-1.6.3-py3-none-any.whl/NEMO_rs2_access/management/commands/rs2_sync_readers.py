from django.core.management import BaseCommand

from NEMO_rs2_access import rs2


class Command(BaseCommand):
    help = "Run every day to sync up rs2 readers."

    def handle(self, *args, **options):
        rs2.sync_readers()
