def make_create_message_input(message):
    return {"input": {"messages": [message.model_dump()]}}
