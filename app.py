import sys
import traceback
from datetime import datetime
from bots.dialog_bot import DialogBot
from dialogs.main_dialog import MainDialog

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
    ConversationState,
    UserState,
    MemoryStorage
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

SETTINGS = BotFrameworkAdapterSettings('','')
ADAPTER = BotFrameworkAdapter(SETTINGS)


MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

DIALOG = MainDialog(USER_STATE)
botdialog = DialogBot(CONVERSATION_STATE, USER_STATE, DIALOG)


async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()    
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )        
        await context.send_activity(trace_activity)
    await CONVERSATION_STATE.delete(context)


ADAPTER.on_turn_error = on_error

async def messages(req: Request) -> Response:    
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    try:
        response = await ADAPTER.process_activity(activity, auth_header, botdialog.on_turn)
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=201)
    except Exception as exception:
        raise exception


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="0.0.0.0", port=3978)
    except Exception as error:
        raise error
