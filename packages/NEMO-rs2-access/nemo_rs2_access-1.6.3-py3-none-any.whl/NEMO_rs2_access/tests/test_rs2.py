from copy import copy
from datetime import timedelta
from typing import Dict, List
from unittest import mock

from NEMO.models import Account, Area, AreaAccessRecord, Customization, Project, Tool, UsageEvent, User
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from requests import Response

from NEMO_rs2_access.models import ErrorLog, Reader, UserPreferencesDefaultProject
from NEMO_rs2_access.rs2 import (
    LAST_EVENTS_PROCESSED,
    NEXT_EVENTS_BEGIN_DATE,
    READERS_HISTORY_URL,
    get_project_ids_to_charge_for_user,
    get_rs2_settings,
    login,
    sync_access,
)

READER_ONE_ID = "123-456-789"
READER_TWO_ID = "456-789-101"

BADGE_NUMBER = "123"


# This method will be used by the mock to replace requests.get
# In the web relay case, it will return a xml file with the relay statuses
def mocked_requests_get(*args, **kwargs):
    rs2_settings = get_rs2_settings()

    class MockResponse(Response):
        def __init__(self, json_data, status_code):
            super().__init__()
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    reader_id = settings.RS2_READER_ID
    if args[0].startswith(rs2_settings.url + READERS_HISTORY_URL.format(reader_id, "")):
        badge = settings.RS2_BADGE_NUMBER
        return MockResponse(mock_event_access_granted(badge, reader_id), 200)
    elif args[0].startswith(rs2_settings.url):
        return MockResponse([], 200)

    return MockResponse(None, 404)


def mock_event_access_granted(badge_number, reader_id) -> List[Dict]:
    rs2_settings = get_rs2_settings()
    event = {
        "SiteId": "123123123123123",
        "SiteName": "Site 1",
        "EventDate": "2023-05-15T14:09:46",
        "SourceType": 6,
        "SourceId": reader_id,
        "EventType": 601,
        "Description": "Access Granted",
        "EventLocation": "Cleanroom entrance",
        "EventLocationId": None,
        "Cardholder": "Testy McTester",
        "CardNumber": None,
        "FacilityCode": 507,
        "CardholderId": 123456,
        "CardId": None,
        rs2_settings.user_sync_field: badge_number,
    }
    return [event]


class RS2Test(TestCase):
    def test_get_correct_project(self):
        account: Account = Account.objects.create(name="Test account")
        project: Project = Project.objects.create(name="Test project", account=account)
        project2: Project = Project.objects.create(name="Test project 2", account=account)
        project3: Project = Project.objects.create(
            name="Test project 3", account=Account.objects.create(name="Test account 2")
        )
        user, created = User.objects.get_or_create(
            username="testy", first_name="McTester", last_name="testy", badge_number=1
        )
        random_user, created = User.objects.get_or_create(
            username="randy", first_name="McRander", last_name="randy", badge_number=11
        )
        random_user.projects.add(project, project2)
        start = timezone.now() - timedelta(minutes=30)
        end = timezone.now()
        # no project, return the given project id
        self.assertEqual([1], get_project_ids_to_charge_for_user(user, start, end, 1))
        # one project, should be the one
        user.projects.add(project)
        self.assertEqual([project.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        user.projects.add(project2)
        project.active = False
        project.save()
        # two projects, first active one returned
        self.assertEqual([project2.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        project.active = True
        project.save()
        # default project set, should be the one returned
        UserPreferencesDefaultProject.objects.create(user_preferences=user.get_preferences(), default_project=project2)
        self.assertEqual([project2.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # create one Usage event that is remote, no change
        tool = Tool.objects.create(name="test tool")
        UsageEvent.objects.create(
            user=user,
            project=project,
            remote_work=True,
            tool=tool,
            operator=user,
            start=(start - timedelta(hours=1)),
            end=timezone.now(),
        )
        self.assertEqual([project2.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # create another, non-remote, which ended before
        UsageEvent.objects.create(
            user=user,
            project=project,
            tool=tool,
            operator=user,
            start=(start - timedelta(hours=1)),
            end=(start - timedelta(seconds=1)),
        )
        self.assertEqual([project2.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # create another, non-remote, which started after
        UsageEvent.objects.create(
            user=user, project=project, tool=tool, operator=user, start=(end + timedelta(seconds=1)), end=timezone.now()
        )
        self.assertEqual([project2.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # ongoing event starting later
        usage = UsageEvent.objects.create(
            user=user, project=project, tool=tool, operator=user, start=(end + timedelta(seconds=1))
        )
        usage.delete()
        self.assertEqual([project2.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # ongoing event, should work
        UsageEvent.objects.create(user=user, project=project, tool=tool, operator=user, start=start)
        self.assertEqual([project.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # create another qualifying, no duplicates
        UsageEvent.objects.create(
            user=user, project=project, tool=tool, operator=user, start=(start - timedelta(hours=1)), end=timezone.now()
        )
        self.assertEqual([project.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # create a third qualifying event on different project but same account, only the first one should come back
        UsageEvent.objects.create(
            user=user,
            project=project2,
            tool=tool,
            operator=user,
            start=(start - timedelta(hours=1)),
            end=timezone.now(),
        )
        self.assertEqual([project.id], get_project_ids_to_charge_for_user(user, start, end, 0))
        # create another third qualifying event on different project and different account, both should come back
        UsageEvent.objects.create(
            user=user,
            project=project3,
            tool=tool,
            operator=user,
            start=(start - timedelta(hours=1)),
            end=timezone.now(),
        )
        self.assertEqual([project.id, project3.id], get_project_ids_to_charge_for_user(user, start, end, None))

    def test_login(self):
        account: Account = Account.objects.create(name="Test account")
        project: Project = Project.objects.create(name="Test project", account=account)
        project2: Project = Project.objects.create(name="Test project 2", account=account)
        user, created = User.objects.get_or_create(
            username="testy", first_name="McTester", last_name="testy", badge_number=1
        )
        area = Area.objects.create(name="Area 1")
        start = timezone.now()
        login(user, area, start)
        records = AreaAccessRecord.objects.filter(customer=user, area=area)
        # No projects found for user, no log in
        self.assertFalse(records.exists())
        user.projects.add(project)
        login(user, area, start)
        # Now we should be ok
        self.assertTrue(records.exists())
        self.assertEqual(records.first().area, area)
        self.assertEqual(records.first().start, start)
        self.assertEqual(records.first().end, None)
        # login again, nothing should have changed since it's in the same area
        login(user, area, timezone.now())
        records = AreaAccessRecord.objects.filter(customer=user, area=area)
        self.assertTrue(records.exists())
        self.assertEqual(len(records), 1)
        self.assertEqual(records.first().start, start)
        self.assertEqual(records.first().end, None)
        # Login to different area, should log out of first one and log in second one
        new_area = Area.objects.create(name="Area 2")
        new_start = timezone.now()
        login(user, new_area, new_start)
        previous_records = AreaAccessRecord.objects.filter(customer=user, end__isnull=False)
        self.assertTrue(previous_records.exists())
        self.assertEqual(previous_records.first().end, new_start)
        self.assertEqual(previous_records.first().area, area)
        new_records = AreaAccessRecord.objects.filter(customer=user, area=new_area)
        self.assertTrue(new_records.exists())

    @mock.patch("NEMO_rs2_access.rs2.requests.get", side_effect=mocked_requests_get)
    def test_login_logout_event(self, mock_args):
        # Creating user, area and in/out readers
        account: Account = Account.objects.create(name="Test account")
        project: Project = Project.objects.create(name="Test project", account=account)
        user, created = User.objects.get_or_create(
            username="testy", first_name="McTester", last_name="testy", badge_number=BADGE_NUMBER
        )
        user.projects.add(project)
        cleanroom = Area.objects.create(name="Cleanroom")
        reader_enter = Reader.objects.create(
            reader_id=READER_ONE_ID,
            reader_name="Cleanroom entrance",
            area=cleanroom,
            reader_type=Reader.ReaderType.ENTRANCE,
            installed=True,
            data="",
        )
        reader_exit = Reader.objects.create(
            reader_id=READER_TWO_ID,
            reader_name="Cleanroom exit",
            area=cleanroom,
            reader_type=Reader.ReaderType.EXIT,
            installed=True,
            data="",
        )

        # Login
        with self.settings(RS2_BADGE_NUMBER=user.badge_number, RS2_READER_ID=READER_ONE_ID):
            sync_access()
        self.assertTrue(user.in_area())
        area_record = user.area_access_record()
        self.assertEqual(area_record.area, cleanroom)

        # Logout
        with self.settings(RS2_BADGE_NUMBER=user.badge_number, RS2_READER_ID=READER_TWO_ID):
            sync_access()
        self.assertFalse(user.in_area())
        area_record = AreaAccessRecord.objects.get(id=area_record.id)
        self.assertTrue(area_record.end)

    @mock.patch("NEMO_rs2_access.rs2.requests.get", side_effect=mocked_requests_get)
    def test_double_login_event(self, mock_args):
        # Creating user, area and in/out readers
        account: Account = Account.objects.create(name="Test account")
        project: Project = Project.objects.create(name="Test project", account=account)
        user, created = User.objects.get_or_create(
            username="testy", first_name="McTester", last_name="testy", badge_number=BADGE_NUMBER
        )
        user.projects.add(project)
        cleanroom = Area.objects.create(name="Cleanroom")
        reader_enter = Reader.objects.create(
            reader_id=READER_ONE_ID,
            reader_name="Cleanroom entrance",
            area=cleanroom,
            reader_type=Reader.ReaderType.ENTRANCE,
            installed=True,
            data="",
        )

        # Login
        area_record = AreaAccessRecord.objects.create(
            customer=user, area=cleanroom, start=timezone.now(), project=project
        )
        self.assertTrue(user.in_area())
        self.assertEqual(area_record.area, cleanroom)

        rs2_access_no_error_on_already_logged_in = copy(settings.RS2_ACCESS)
        rs2_access_no_error_on_already_logged_in["record_already_logged_in_as_error"] = False

        # Login again, flag off so no log
        with self.settings(
            RS2_BADGE_NUMBER=user.badge_number,
            RS2_READER_ID=READER_ONE_ID,
            RS2_ACCESS=rs2_access_no_error_on_already_logged_in,
        ):
            sync_access()
        self.assertFalse(ErrorLog.objects.exists())

        # Reset
        Customization.objects.filter(name=NEXT_EVENTS_BEGIN_DATE).delete()
        Customization.objects.filter(name=LAST_EVENTS_PROCESSED).delete()

        # Login again, flag on so it should be logged
        with self.settings(RS2_BADGE_NUMBER=user.badge_number, RS2_READER_ID=READER_ONE_ID):
            sync_access()
        self.assertTrue(ErrorLog.objects.exists())
        self.assertEqual(ErrorLog.objects.first().user, user)
        self.assertEqual(ErrorLog.objects.first().error_type, ErrorLog.ErrorType.ALREADY_LOGGED_IN)
