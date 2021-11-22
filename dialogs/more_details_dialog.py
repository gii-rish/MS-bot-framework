from typing import List

from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice, FoundChoice
from botbuilder.core import MessageFactory
from . import Constants
from data_model.user_details import UserDetails


class MoreDetailsDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None, customerId = 0):
        super(MoreDetailsDialog, self).__init__(dialog_id or MoreDetailsDialog.__name__)
        self.customerId = customerId
        self.DONE = "DONE"
        self.options = list([self.DONE, *Constants.COLUMNS])
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [self.selection_step, self.loop_step]
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__


    async def selection_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # step_context.values['userInfo'] = UserDetails()
        # user_details = step_context.result
        print("----->>", self.customerId)
        message = "Please choose an option other than DONE to continue."        
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(message),
            choices=self.options,
        )
        return await step_context.prompt(ChoicePrompt.__name__, prompt_options)


    async def loop_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        selected = step_context._turn_context.activity.text
        done = True if selected == self.DONE else False

        if done:
            return await step_context.end_dialog()
        
        # user_details: UserDetails = step_context.values['userInfo']
        return await step_context.replace_dialog(MoreDetailsDialog.__name__)