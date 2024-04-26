from fastapi import FastAPI
from hypertune_util import ht_wrapper
app = FastAPI()


@app.get("/")
async def root():
    (
        priority_order,
        response_types_in_priority,
        event,
    ) = ht_wrapper.get_event_details(command_type="help")

    text_or_embed, response = ht_wrapper.get_text_or_embed_response(
        response_type=response_types_in_priority[0],
        response_node=event
    )
    print("response", response)
    return {"message": response}