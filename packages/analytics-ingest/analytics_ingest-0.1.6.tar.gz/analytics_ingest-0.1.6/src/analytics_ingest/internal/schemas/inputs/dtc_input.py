def make_dtc_input(config_id, batch, message_id, file_id="", message_date=None):
    return {
        "input": {
            "signals": {
                "configurationId": config_id,
                "data": [item.model_dump() for item in batch],
                "fileId": file_id,
                "messageDate": message_date,
                "messageId": message_id,
            }
        }
    }
