from botbuilder.core import (
    TurnContext,
    ActivityHandler,
    ConversationState,
    MessageFactory
)
from botbuilder.dialogs import (
    DialogSet,
    WaterfallDialog,
    WaterfallStepContext,
    ComponentDialog
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    PromptOptions,
    ConfirmPrompt,
    PromptValidatorContext
)

from db_connector import create_connection
from . import Constants
from botdialog.more_details_dialog import MoreDetailsDialog


class BotDialog(ComponentDialog):
    def __init__(self, conversation: ConversationState):
        super(BotDialog, self).__init__(BotDialog.__name__)
        
        self.conversation_state = conversation
        self.state_property = self.conversation_state.create_property("dialog_set")
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))

        self.dialog_set = DialogSet(self.state_property)
        self.dialog_set.add(TextPrompt("text_prompt"))
        self.dialog_set.add(NumberPrompt("number_prompt", self.custom_validator))
        self.dialog_set.add(ConfirmPrompt("confirm_prompt"))
        # self.dialog_set.add(MoreDetailsDialog("custom_dialog"))
        self.add_dialog(WaterfallDialog("main_dialog", \
                                            [self.greeting, self.get_customerID, self.send_profile_details, self.get_confirmation]))            
        self.initial_dialog_id = "WFDialog"


    async def greeting(self, step_context: WaterfallStepContext):
        prompt_options = PromptOptions(prompt=MessageFactory.text("Hi, How can I help you?"))
        return await step_context.prompt("TextPrompt.__name__", prompt_options)
    

    async def get_customerID(self, step_context: WaterfallStepContext):
        data = step_context.result
        prompt_options = PromptOptions(prompt=MessageFactory.text("Please enter the your customerID"))
        return await step_context.prompt("number_prompt", prompt_options)
    
    
    async def custom_validator(self, prompt_validator: PromptValidatorContext):
        if not prompt_validator.recognized.succeeded:
            await prompt_validator.context.send_activity("Please enter the ID in numerals.")
            return False
        else:
            id = int(prompt_validator.recognized.value)            
            if id not in range(10000, 9999999):
                await prompt_validator.context.send_activity("Please enter a valid CustomerID.")
                return False
        return True


    async def send_profile_details(self, step_context: WaterfallStepContext):
        customerId = step_context.result
        step_context.values["customerId"] = customerId        
        result = create_connection(customer_id = customerId)
        
        if result is not None:                            
            response = ''
            for key, value in zip(Constants.COLUMNS[1:], result[1:]):
                response = ''.join([response, ' ', str(key),': ',"Not Updated" if value is None else str(value), ','])
                
            await step_context.context.send_activity("Thank you for providing the same.")
            await step_context.context.send_activity(MessageFactory.text(response))
        else:
            await step_context.context.send_activity(f"No details found for id {customerId}.")
        
        prompt_options = PromptOptions(prompt=MessageFactory.text("Would you like to continue further?"))
        return await step_context.prompt("confirm_prompt", prompt_options)
        
        # return await step_context.end_dialog()
    
        
    async def get_confirmation(self, step_context: WaterfallStepContext):
        choice = step_context.result
        if choice:
            return await step_context.begin_dialog("custom_dialog")


    async def on_turn(self, turn_context: TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if(dialog_context.active_dialog is not None):
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")        
        
        await self.conversation_state.save_changes(turn_context)