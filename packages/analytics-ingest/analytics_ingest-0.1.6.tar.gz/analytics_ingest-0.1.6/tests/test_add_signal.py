import unittest

from graphql.error import GraphQLSyntaxError

from analytics_ingest.ingest_client import AnalyticsIngestClient
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from factories import configuration_factory, message_factory, signal_factory


class TestAnalyticsIngestClientIntegration(unittest.TestCase):
    def setUp(self):
        self.config_data = configuration_factory()
        self.client = AnalyticsIngestClient(
            device_id=self.config_data['device_id'],
            vehicle_id=self.config_data['vehicle_id'],
            fleet_id=self.config_data['fleet_id'],
            org_id=self.config_data['organization_id'],
            batch_size=10,
            graphql_endpoint="http://0.0.0.0:8092/graphql",
        )

    def test_add_signal_with_factories(self):
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        signal_data = signal_factory()[0]

        test_variables = {
            **message_data,
            **signal_data,
            "name": signal_data["name"],
            "messageName": message_data["name"],
            "networkName": message_data["networkName"],
            "ecuName": message_data["ecuName"],
        }

        self.client.add_signal(test_variables)
        self.assertIsInstance(self.client.configuration_id, int)

    def test_create_batches_valid(self):
        data = list(range(10))
        batches = Batcher.create_batches(data, 3)
        self.assertEqual(len(batches), 4)
        self.assertEqual(batches[0], [0, 1, 2])

    def test_create_batches_invalid_type(self):
        with self.assertRaises(TypeError) as ctx:
            Batcher.create_batches("not_a_list", 2)
        self.assertIn("data", str(ctx.exception))

    def test_create_batches_invalid_batch_size(self):
        with self.assertRaises(ValueError) as ctx:
            Batcher.create_batches([1, 2, 3], 0)
        self.assertIn("batch_size", str(ctx.exception))

    def test_create_configuration_success(self):
        config_data = configuration_factory()
        variables = {
            "input": {
                "deviceId": config_data['device_id'],
                "fleetId": config_data['fleet_id'],
                "organizationId": config_data['organization_id'],
                "vehicleId": config_data['vehicle_id'],
            }
        }
        response = self.client.executor.execute(
            GraphQLMutations.create_configuration(), variables
        )
        self.assertIn("data", response)
        self.assertIn("createConfiguration", response["data"])

    def test_create_configuration_failure(self):
        config_data = configuration_factory()
        variables = {
            "input": {
                "deviceId": 999999,  # non-existent
                "fleetId": 999999,  # non-existent
                # missing fields on purpose
            }
        }
        with self.assertRaises(RuntimeError) as context:
            self.client.executor.execute(
                GraphQLMutations.create_configuration(), variables
            )
        self.assertIn("GraphQL request failed with errors", str(context.exception))

    def test_create_configuration_failure_invalid_endpoint(self):
        with self.assertRaises(RuntimeError):
            _ = AnalyticsIngestClient(
                device_id=1,
                vehicle_id=2,
                fleet_id=3,
                org_id=4,
                batch_size=2,
                graphql_endpoint="http://invalid-endpoint",
            )

    def test_execute_failure_malformed_query(self):
        bad_query = "this is not a valid graphql query"
        with self.assertRaises(RuntimeError) as ctx:
            self.client.executor.execute(bad_query)
        self.assertIn("Invalid GraphQL syntax", str(ctx.exception))

    def test_add_signal_missing_data_key(self):
        variables = {
            "name": "Speed",
            "unit": "km/h",
            "messageName": "SpeedMessage",
            "networkName": "CAN",
            "ecuName": "ecuName",
            "ecuId": "ecuId",
        }
        with self.assertRaises(RuntimeError) as context:
            self.client.add_signal(variables)
        self.assertIn("Missing required field: 'data'", str(context.exception))


if __name__ == "__main__":
    unittest.main()
