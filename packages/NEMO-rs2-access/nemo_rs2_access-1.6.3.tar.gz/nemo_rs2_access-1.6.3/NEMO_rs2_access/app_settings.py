DEFAULT = {
    "cardholder_sync": False,
    "user_sync_field": "CardNumber",
    "nemo_user_sync_field": "badge_number",
    # 601 is access granted, 607 Access Granted Door Unlocked
    "relevant_event_types": [601, 607],
    # we will store the date to restart as the last processed event minus this buffer
    # this allows us to make sure we are not missing events between calls to all the separate readers
    "buffer_in_seconds": 7,
    # whether to record someone attempting to log into an area they are already logged in as error in logs
    "record_already_logged_in_as_error": True,
}

RS2_ACCESS = {}
