from analytics_ingest.internal.schemas.inputs.message_input import (
    make_create_message_input,
)
from analytics_ingest.internal.schemas.message_schema import MessageSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations

_message_cache = {}


def create_message(executor: GraphQLExecutor, variables: dict) -> str:
    message = MessageSchema.from_variables(variables)
    key = message.cache_key()

    if key in _message_cache:
        return _message_cache[key]

    response = executor.execute(
        GraphQLMutations.create_message(), make_create_message_input(message)
    )

    messages = response["data"].get("createMessage", [])
    if not messages:
        raise RuntimeError("No messages created")

    message_id = messages[0]["id"]
    _message_cache[key] = message_id

    return message_id
