def make_gps_input(config_id, batch):
    return {
        "input": {
            "configurationId": config_id,
            "data": [item.model_dump() for item in batch],
        }
    }
