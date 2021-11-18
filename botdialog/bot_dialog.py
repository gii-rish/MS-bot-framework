from botbuilder.core import (
    TurnContext,
    ActivityHandler,
    ConversationState,
    MessageFactory
)
from botbuilder.dialogs import (
    DialogSet,
    WaterfallDialog,
    WaterfallStepContext
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    PromptOptions,
    PromptValidatorContext
)

from db_connector import create_connection
from . import Constants

class BotDialog(ActivityHandler):
    def __init__(self, conversation: ConversationState):
        self.conversation_state = conversation
        self.state_property = self.conversation_state.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_property)
        self.dialog_set.add(TextPrompt("text_prompt"))
        self.dialog_set.add(NumberPrompt("number_prompt", self.custom_validator))
        self.dialog_set.add(WaterfallDialog("main_dialog", \
                                            [self.greeting, self.getCustomerID, self.Completed]))


    async def greeting(self, waterfall_step: WaterfallStepContext):
        return await waterfall_step.prompt("text_prompt", PromptOptions(prompt=MessageFactory.text("Hi, How can I help you?")))
    

    async def getCustomerID(self, waterfall_step: WaterfallStepContext):
        data = waterfall_step._turn_context.activity.text        
        return await waterfall_step.prompt("number_prompt", PromptOptions(prompt=MessageFactory.text("Please enter the your customerID")))
    
    
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


    async def Completed(self, waterfall_step: WaterfallStepContext):
        customerId = waterfall_step._turn_context.activity.text
        waterfall_step.values["customerId"] = customerId        
        result = create_connection(customer_id = customerId)        
                
        response = ''
        for key, value in zip(Constants.COLUMNS[1:], result[1:]):
            response = ''.join([response, ' ', str(key),': ',"Not Updated" if value is None else str(value), ','])
        await waterfall_step._turn_context.send_activity("Thank you for providing the same.")
        await waterfall_step._turn_context.send_activity(response)
        return await waterfall_step.end_dialog()


    async def on_turn(self, turn_context: TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if(dialog_context.active_dialog is not None):
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")
        
        await self.conversation_state.save_changes(turn_context)