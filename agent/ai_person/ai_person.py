from .memory import Memory
from .personality import Personality
from .identity import Identity
from .purpose import Purpose
from .actions import Actions
from .llm_service import get_response_from_llm
import json
import logging
import os
from datetime import datetime

# Configure logging
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"ai_person_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(agent_id)s] - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - [%(agent_id)s] - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

class AiPerson:
    def __init__(self):
        logger.info("Initializing AiPerson", extra={'agent_id': "system"})
        self.identity = Identity()
        self.personality = Personality()
        self.purpose = Purpose()
        self.memory = Memory()
        self.actions = Actions()
        logger.info("AiPerson initialization complete", extra={'agent_id': "system"})
    

    def hear_text(self, agent_id: str, text: str) -> None:
        try:
            logger.info(f"Received text from human: {text}", extra={'agent_id': agent_id})
            print(text)
            user_dialouge = f"Human: {text}"
            self.memory.add_dialogue_to_current_converstaion(agent_id, user_dialouge)
            logger.debug(f"Added dialogue to conversation: {user_dialouge}", extra={'agent_id': agent_id})


            response_structure = {
                "action": {
                    "action_name": "<Name of the Action from the list of actions>",
                    "action_args": {
                        "<argument key>": "<argument_value>"
                    }
                },
                "details_about_human": {
                    "<key name of the part you want to update>":"<full new value of that part>",
                },
                "conversational_behavior": "<Updated text for Conversational behavior (if required)>",
                "debugInfo": "<Informational regarding what do you think was wrong or incomplete about the information provided>"
            }

            response_structure_str = json.dumps(response_structure)

            prompt = f"""
            - Indentity:
            {self.identity.get_indentity_prompt(agent_id) if hasattr(self.identity, 'get_indentity_prompt') and 'agent_id' in self.identity.get_indentity_prompt.__code__.co_varnames else self.identity.get_indentity_prompt()}
            - Purpose:
            {self.purpose.get_purpose_prompt(agent_id) if hasattr(self.purpose, 'get_purpose_prompt') and 'agent_id' in self.purpose.get_purpose_prompt.__code__.co_varnames else self.purpose.get_purpose_prompt()}
            - Personality:
            {self.personality.get_personality_prompt_text(agent_id)}
            - Details about Human:
            {self.memory.get_information_about_the_human_prompt(agent_id)}
            - Available Actions:
            {self.actions.get_all_available_actions_prompt()}
            - Current Conversation:
            {self.memory.get_current_conversation_prompt(agent_id)}
            - Expected Resonse:
            Base on the current converstaion, respond what should be the next action from the available actions.
            Analyze and Understand the most recent ask/want from human from the converstaion, not some previous ask.
            The past converstational history is for better understanding of the context.
            Incorporate the details and information provided in each section.
            
            From the converstational context and the available details about the human, you might need to update what you know about the human.
            Analyze the converstaion and the details about the human and if required update the Details about the Human section.
            You have to include the the key, value pair you want to update in the Details about Human section. You can have multiple key value pair and the keys should be from what is provided already in the Details about Human section.
            
            Also, based on feedback you might have to adjust your conversational behvaior and update the converstaional behvior part in your personality.
            Also include that in the response. Respond with the full text that needs to go in the Converstaional behvaior section. 
            
            Don't include the update sections if not required to update.

            Sometimes the human dialogue can have [System] in the begnining of the dialogue it means the text didn't directly come from the human.
            It came from the a system that is working on the user's behalf. Understand that decide on the action that way. 
            But think in the way that you have decided that to send yourself rather than system asking you.
            
            There is also a debugInfo sections which you can fill if desired. 
            Don't keep it more than 3 lines and include only if required. 
            Here you can include if you want some new sections in the user info or other palces.
            
            Response should be a json string of the following structure:
            {response_structure_str}
            The response should only be the action json string.
            """

            response_from_llm = get_response_from_llm(prompt=prompt)
            logger.info(f"Prompt to LLM {prompt}", extra={'agent_id': agent_id})

            # Null and type checks for response_from_llm
            if not response_from_llm or not isinstance(response_from_llm, str):
                logger.error(f"Invalid response from LLM: {response_from_llm}", extra={'agent_id': agent_id})
                print("Error: Invalid response from LLM.")
                return
            try:
                response_json = json.loads(response_from_llm)
            except Exception as e:
                logger.error(f"Failed to parse LLM response as JSON: {response_from_llm}", extra={'agent_id': agent_id})
                print(f"Error: Failed to parse LLM response as JSON. {e}")
                return
            logger.debug(f"Parsed LLM response: {json.dumps(response_json, indent=2)}", extra={'agent_id': agent_id})
            print(response_json)

            actions = response_json.get('action', {})
            action_name = actions.get('action_name', 'default_action')
            action_args = actions.get('action_args', {})
            logger.info(f"Executing action: {action_name} with args: {action_args}", extra={'agent_id': agent_id})
            
            if details_about_human := response_json.get('details_about_human'):
                logger.info(f"Updating human details: {details_about_human}", extra={'agent_id': agent_id})
                for key, value in details_about_human.items():
                    self.memory.update_user_info(agent_id, field=key, value=value)

            if conversational_behavior := response_json.get('conversational_behavior'):
                logger.info("Updating conversational behavior", extra={'agent_id': agent_id})
                self.personality.update_conversational_behavior(agent_id, conversational_behavior)

            debug_info = response_json.get('debugInfo', None)
            if debug_info:
                logger.debug(f"Debug info from LLM: {debug_info}", extra={'agent_id': agent_id})
            print("debugInfo:\n")
            print(debug_info)

            self.actions.execute_action(agent_id=agent_id, action_name=action_name, action_args=action_args)
            logger.info(f"Action {action_name} execution completed", extra={'agent_id': agent_id})

        except Exception as e:
            logger.error(f"Error in hear_text: {str(e)}", exc_info=True, extra={'agent_id': agent_id})
            print(e)

    def initialize_agent(self, agent_id: str) -> None:
        """Initialize a new agent_id in all relevant submodules."""
        logger.info(f"Initializing new agent_id: {agent_id}", extra={'agent_id': agent_id})
        self.personality.initialize_personality(agent_id)
        self.memory.initialize_memory(agent_id)
        logger.info(f"Initialization complete for agent_id: {agent_id}", extra={'agent_id': agent_id})
