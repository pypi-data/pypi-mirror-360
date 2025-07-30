import unittest

from analytics_ingest.ingest_client import AnalyticsIngestClient
from factories import configuration_factory, dtc_factory, message_factory


class TestAnalyticsDTCIntegration(unittest.TestCase):
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

    def test_add_dtc_valid(self):
        dtc_data = dtc_factory(num_entries=5)
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        test_variables = {
            **dtc_data,
            **message_data,
            "messageName": message_data["name"],
        }
        try:
            self.client.add_dtc(test_variables)
        except Exception as e:
            self.fail(f"Valid DTC input raised an exception: {e}")

    def test_add_dtc_missing_description(self):
        dtc_data = dtc_factory(num_entries=5)
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        test_variables = {
            **dtc_data,
            **message_data,
            "messageName": message_data["name"],
        }
        del test_variables["data"][0]["description"]
        with self.assertRaises(Exception) as context:
            self.client.add_dtc(test_variables)
        self.assertIn("description", str(context.exception).lower())

    def test_add_dtc_invalid_time_format(self):
        dtc_data = dtc_factory(num_entries=1)
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        test_variables = {
            **dtc_data,
            **message_data,
            "messageName": message_data["name"],
        }
        test_variables["data"][0]["time"] = "invalid-time"
        with self.assertRaises(Exception) as context:
            self.client.add_dtc(test_variables)
        self.assertIn("time", str(context.exception).lower())

    def test_add_dtc_with_extra_field(self):
        dtc_data = dtc_factory(num_entries=1)
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        test_variables = {
            **dtc_data,
            **message_data,
            "messageName": message_data["name"],
        }
        test_variables["data"][0]["unexpected"] = "extra"
        with self.assertRaises(Exception) as context:
            self.client.add_dtc(test_variables)
        self.assertIn("unexpected", str(context.exception).lower())

    def test_add_dtc_empty_data_list(self):
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        test_variables = {
            **message_data,
            "messageName": message_data["name"],
            "data": []
            }
        try:
            self.client.add_dtc(test_variables)
        except Exception as e:
            self.fail(f"Empty DTC data list should not raise an exception, but got: {e}")

    def test_add_dtc_missing_data_key(self):
        message_data = message_factory(self.config_data['vehicle_id'])[0]
        test_variables = {
            **message_data,
            "messageName": message_data["name"],
        }

        try:
            self.client.add_dtc(test_variables)
        except Exception as e:
            self.fail(f"Missing 'data' key should not raise exception, but got: {e}")
