from analytics_ingest.internal.schemas.gps_schema import GPSSchema
from analytics_ingest.internal.schemas.inputs.gps_input import make_gps_input
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations


def create_gps(
    executor: GraphQLExecutor, config_id: str, variables: dict, batch_size: int
):
    inputs = build_batched_gps_inputs(config_id, variables, batch_size)
    for payload in inputs:
        executor.execute(GraphQLMutations.upsert_gps_data(), payload)


def build_batched_gps_inputs(config_id, variables, batch_size):
    gps_items = GPSSchema.from_variables(variables)
    batches = Batcher.create_batches(gps_items, batch_size)
    return [make_gps_input(config_id, batch) for batch in batches]
