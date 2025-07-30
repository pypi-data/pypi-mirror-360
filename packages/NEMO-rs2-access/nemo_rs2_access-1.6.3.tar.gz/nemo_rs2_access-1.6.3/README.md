# NEMO RS2 Access plugin

This plugin for NEMO allows to sync up area access with the RS2 Access system.

# Installation

1. `pip install NEMO-rs2-access`
2. in `settings.py` add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
  '...',
  'NEMO_rs2_access',
  '...'
]
```
3. add the RS2 access information:
```python
RS2_ACCESS = {
  "url": "",
  "timeout": 30, # timeout in seconds
  "public_key": "",
  "auth": {
    "user_id": "",
    "password": ""
  },
   # Uncomment to change the default CardHolder sync field 
   # Choices are "CardholderId", "CardNumber", "CardId", or cardholder attribute like "UserColumns.UserText1"
   # "user_sync_field": "CardNumber",
   # Uncomment to use the sync field as an attribute of Cardholder (default is False, meaning it is an attribute of the Event)
   # "cardholder_sync": False,
   # Uncomment to change the default NEMO sync field, for example `details__employee_id`
   # "nemo_user_sync_field": "badge_number",
   # Uncomment to change the default buffer in seconds, used to prevent potential duplicates and potential missing events between calls to readers
   # "buffer_in_seconds": "7",
   # Uncomment to change whether to record someone attempting to log into an area they are already logged in as error in logs (default is True)
   # "record_already_logged_in_as_error": True,
}

```
4. enable and start systemd tasks (examples in this [systemd folder](https://gitlab.com/nemo-community/atlantis-labs/nemo-rs2-access/-/tree/main/resources/systemd)):
   * nemo_rs2_sync_readers (every hour or every day)
   * nemo_rs2_sync_access (every minute)

Notes:
1. In Detailed administration -> Customization, a customization with key `rs2_event_begin_date` and date value for example `2023-05-18T19:30:16` can be set prior to the first run to grab data starting at that date.
2. If not set, the system will start syncing from the beginning of the current day
3. The systemd tasks can also be run manually from Detailed admin -> RS2 Access -> Reader -> select any reader (doesn't matter which one) and use the action dropdown to run the sync.

## Usage
1. Run the `sync reader` action via systemd or Detailed administration
2. Edit the relevant readers and associate them with an Area and a type (Entrance or Exit)
3. Set Badge numbers in NEMO users
4. Run the `sync access` action via systemd or Detailed administration

## Project selection rules
Upon login, the first active project is selected since all that matters is that we have a placeholder.

When updating the record on logout, the project is set using the following rules:
 1. If the user has only one active project, use it
 2. Check tool usage for this user since login time (non-remote) and create one record for each distinct account
 3. If there is no tool usage, use the default project (set in user preferences)
 4. If there is no default project, use the first active project by relation id (first added)