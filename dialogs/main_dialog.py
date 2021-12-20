from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    PromptOptions,
)
from botbuilder.dialogs.prompts import OAuthPrompt, OAuthPromptSettings, ConfirmPrompt
from botbuilder.core import MessageFactory, UserState
from dialogs.top_level_dialog import TopLevelDialog
from data_model.user_details import UserDetails

from dialogs.logout_dialog import LogoutDialog


class MainDialog(LogoutDialog):
    def __init__(self, user_state: UserState, connection_name):
        super(MainDialog, self).__init__(MainDialog.__name__, connection_name)
        
        self.add_dialog(
            OAuthPrompt(
                OAuthPrompt.__name__,
                OAuthPromptSettings(
                    connection_name=connection_name,
                    text="Please Sign In",
                    title="Sign In",
                    timeout=300000,
                ),
            )
        )

        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.user_state = user_state    

        self.add_dialog(TopLevelDialog(TopLevelDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", 
                [
                    self.prompt_step,
                    self.initial_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = "WFDialog"
        
        
    async def prompt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.begin_dialog(OAuthPrompt.__name__)
    

    async def initial_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            await step_context.context.send_activity(
                "You are now logged in."
                )
            return await step_context.begin_dialog(TopLevelDialog.__name__)
        
        await step_context.context.send_activity(
            "Login was not successful please try again."
        )
        return await step_context.end_dialog()


    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        message = "Thank you! Hope that I helped you!"
        await step_context.context.send_activity(MessageFactory.text(message))
        return await step_context.end_dialog()