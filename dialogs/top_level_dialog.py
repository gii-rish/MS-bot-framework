
from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import PromptOptions, TextPrompt, NumberPrompt, ConfirmPrompt, PromptValidatorContext

# from data_models import UserProfile
from dialogs.more_details_dialog import MoreDetailsDialog
from . import Constants
from db_connector import create_connection
from data_model.user_details import UserDetails


class TopLevelDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(TopLevelDialog, self).__init__(dialog_id or TopLevelDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__, self.custom_validator))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(MoreDetailsDialog(MoreDetailsDialog.__name__))
        self.USER_INFO = "userInfo"

        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.get_customerID,
                    self.acknowledgement_step,
                    self.get_confirmation,
                ],
            )
        )

        self.initial_dialog_id = "WFDialog"
                            
    
    async def get_customerID(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values[self.USER_INFO] = UserDetails()
        
        prompt_options = PromptOptions(
            prompt=MessageFactory.text("Please enter the your customerID")
            )
        return await step_context.prompt(NumberPrompt.__name__, prompt_options)
    
    
    async def custom_validator(self, prompt_validator: PromptValidatorContext) -> bool:
        if not prompt_validator.recognized.succeeded:
            await prompt_validator.context.send_activity("Please enter the ID in numerals.")
            return False
        else:
            id = int(prompt_validator.recognized.value)            
            if id not in range(10000, 9999999):
                await prompt_validator.context.send_activity("Please enter a valid CustomerID.")
                return False
        return True


    async def acknowledgement_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        customerId = step_context.result
        
        user_details = step_context.values[self.USER_INFO]
        user_details.customerId = customerId

        result = create_connection(customer_id = customerId)

        if result is not None:
            response = ''
            for key, value in zip(Constants.COLUMNS[1:], result[1:]):
                if key == "FirstName":
                    user_details.name = value
                response = ''.join([response, ' ', str(key),': ',"Not Updated" if value is None else str(value), ','])
                
            await step_context.context.send_activity("Thank you for providing the same.")
            await step_context.context.send_activity(MessageFactory.text(response))
        else:
            await step_context.context.send_activity(f"No details found for id {customerId}.")

        prompt_options = PromptOptions(prompt=MessageFactory.text("Would you like to continue further?"))
        return await step_context.prompt(ConfirmPrompt.__name__, prompt_options)


    async def get_confirmation(self, step_context: WaterfallStepContext) -> DialogTurnResult:        
        user_details = step_context.values[self.USER_INFO]
        choice = step_context.result        
        if choice:
            return await step_context.begin_dialog(MoreDetailsDialog.__name__, user_details.customerId)

        if user_details.name:
            await step_context.context.send_activity(MessageFactory.text(f"Thank you, {user_details.name}!"))        
        return await step_context.end_dialog()
        