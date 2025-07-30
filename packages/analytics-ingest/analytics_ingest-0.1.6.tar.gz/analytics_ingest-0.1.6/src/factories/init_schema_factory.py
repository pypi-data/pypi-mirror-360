from analytics_ingest.internal.schemas.ingest_config_schema import IngestConfigSchema


def init_schema_factory(**overrides):
    base = {
        "device_id": 1,
        "vehicle_id": 2,
        "fleet_id": 3,
        "org_id": 4,
        "graphql_endpoint": "http://0.0.0.0:8092/graphql",
        "jwt_token": "sample-jwt-token",
        "batch_size": 50,
        "batch_interval_seconds": 5,
    }
    base.update(overrides)
    return base
