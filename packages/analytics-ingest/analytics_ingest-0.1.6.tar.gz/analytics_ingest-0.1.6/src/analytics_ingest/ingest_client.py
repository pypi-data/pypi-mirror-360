from typing import Optional

from analytics_ingest.internal.schemas.ingest_config_schema import IngestConfigSchema
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.configuration import ConfigurationService
from analytics_ingest.internal.utils.dtc import create_dtc
from analytics_ingest.internal.utils.gps import create_gps
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.message import create_message
from analytics_ingest.internal.utils.network import create_network
from analytics_ingest.internal.utils.signal import create_signal


class AnalyticsIngestClient:
    def __init__(self, **kwargs):
        try:
            self.config = IngestConfigSchema(**kwargs)
        except Exception as e:
            raise ValueError(f"Invalid config: {e}")

        self.executor = GraphQLExecutor(
            self.config.graphql_endpoint, self.config.jwt_token
        )

        self.configuration_id = ConfigurationService(self.executor).create(
            self.config.model_dump()
        )["data"]["createConfiguration"]["id"]

    def add_signal(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            message_id = create_message(self.executor, variables)
            create_signal(
                executor=self.executor,
                config_id=self.configuration_id,
                variables=variables,
                message_id=message_id,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add signal: {e}")

    def add_dtc(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            message_id = create_message(self.executor, variables)
            create_dtc(
                executor=self.executor,
                config_id=self.configuration_id,
                variables=variables,
                message_id=message_id,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add DTC: {e}")

    def add_gps(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            create_gps(
                executor=self.executor,
                config_id=self.configuration_id,
                variables=variables,
                batch_size=self.config.batch_size,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add GPS data: {e}")

    def add_network_stats(self, variables: Optional[dict] = None):
        if not variables:
            raise ValueError("Missing 'variables' dictionary")

        try:
            create_network(
                executor=self.executor,
                config=self.config,
                variables=variables,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to add network stats: {e}")

    def flush(self):
        pass

    def close(self):
        pass
