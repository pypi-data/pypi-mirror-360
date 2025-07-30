import unittest
from copy import deepcopy

from analytics_ingest.ingest_client import AnalyticsIngestClient
from factories import configuration_factory, gps_factory


class TestAnalyticsGPSIntegeration(unittest.TestCase):
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

    def test_add_gps_signal_with_factories(self):
        test_variables = gps_factory(num_entries=10)
        config_id = self.client.configuration_id
        self.assertIsInstance(config_id, int)
        self.client.add_gps(test_variables)

    def test_add_gps_with_valid_manual_data(self):
        valid_entry = gps_factory(num_entries=1)["data"][0]
        test_variables = {"data": [valid_entry for _ in range(5)]}
        try:
            self.client.add_gps(test_variables)
        except Exception as e:
            self.fail(f"Valid input raised exception: {e}")

    def test_add_gps_missing_time(self):
        bad_entry = deepcopy(gps_factory(num_entries=1)["data"][0])
        del bad_entry["time"]
        test_variables = {"data": [bad_entry]}
        with self.assertRaises(Exception) as context:
            self.client.add_gps(test_variables)
        self.assertIn("time", str(context.exception).lower())

    def test_add_gps_invalid_latitude_type(self):
        bad_entry = deepcopy(gps_factory(num_entries=1)["data"][0])
        bad_entry["latitude"] = "not-a-float"
        test_variables = {"data": [bad_entry]}
        with self.assertRaises(Exception) as context:
            self.client.add_gps(test_variables)
        self.assertIn("latitude", str(context.exception).lower())

    def test_add_gps_with_extra_field_in_available(self):
        bad_entry = deepcopy(gps_factory(num_entries=1)["data"][0])
        bad_entry.setdefault("available", {})["unexpected"] = True
        test_variables = {"data": [bad_entry]}
        with self.assertRaises(Exception) as context:
            self.client.add_gps(test_variables)
        self.assertIn("unexpected", str(context.exception).lower())

    def test_add_gps_empty_data_list(self):
        test_variables = {"data": []}
        with self.assertRaises(RuntimeError) as context:
            self.client.add_gps(test_variables)
        self.assertIn("missing required field", str(context.exception).lower())

    def test_add_gps_missing_data_key(self):
        test_variables = {}
        with self.assertRaises(ValueError) as context:
            self.client.add_gps(test_variables)
        self.assertIn("missing 'variables'", str(context.exception).lower())
