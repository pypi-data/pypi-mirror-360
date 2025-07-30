from analytics_ingest.internal.schemas.dtc_schema import DTCSchema
from analytics_ingest.internal.schemas.inputs.dtc_input import make_dtc_input
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations


def create_dtc(
    executor: GraphQLExecutor,
    config_id: str,
    variables: dict,
    message_id: str,
    batch_size: int,
):
    inputs = build_batched_dtc_inputs(config_id, variables, message_id, batch_size)
    for payload in inputs:
        executor.execute(GraphQLMutations.upsert_dtc_mutation(), payload)


def build_batched_dtc_inputs(config_id, variables, message_id, batch_size):
    dtc_items = DTCSchema.from_variables(variables)
    batches = Batcher.create_batches(dtc_items, batch_size)
    return [
        make_dtc_input(config_id, batch, message_id, variables) for batch in batches
    ]
