from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext, MessageFactory
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus
from botbuilder.schema import ChannelAccount
from typing import List


class DialogBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, user_state: UserState, dialog: Dialog):    
        if conversation_state is None:
            raise Exception("[DialogBot]: Missing parameter. conversation_state is required")
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        
        self.state_property = self.conversation_state.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_property)
        self.dialog_set.add(self.dialog)


    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)


    async def on_message_activity(self, turn_context: TurnContext):        
        dialog_context = await self.dialog_set.create_context(turn_context)
        
        results = await dialog_context.continue_dialog()
        if results.status == DialogTurnStatus.Empty:            
            await dialog_context.begin_dialog(self.dialog.id)
    
    
    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:            
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(
                        f"Hi, How can I help you?"
                    )
                )