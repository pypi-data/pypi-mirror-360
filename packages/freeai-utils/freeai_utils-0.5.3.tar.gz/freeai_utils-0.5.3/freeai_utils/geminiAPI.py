from google import genai # pip install google-genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import pyperclip #need pip install pyperclip
from dotenv import load_dotenv #need pip install python-dotenv
import os
from PIL import Image
import logging
from typing import Optional
from freeai_utils.log_set_up import setup_logging
from typing import Union

class GeminiChatBot:
    
    __api_key: str
    logger: logging.Logger
    _model_name: str
    client : genai.Client
    _history: list
    _max_length: int
    _word_prompt: str
    
    def __init__(self, model_name : str ='models/gemini-2.0-flash-lite', api_key : Optional[str] = None, memories_length : int = 4, limit_word_per_respond : int = 150):
        #check data type
        self.__enforce_type(memories_length, int, "memories_length")
        self.__enforce_type(limit_word_per_respond, int, "limit_word_per_respond")
        
        env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(env_path) # load if there is env file
        self.__api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.__api_key:
            raise ValueError("API key was not provided or found in the 'GEMINI_API_KEY' environment variable.")
        
        #check data type before proceed further into connecting
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(self.__api_key, str, "api_key")
        
        #logging
        self.logger = setup_logging(self.__class__.__name__)
        
        try:
            self._client = genai.Client(api_key=self.__api_key)
            self.logger.info("Gemini API configured successfully.")
        except Exception as e:
            self.logger.critical(f"Error configuring Gemini API: {e}")
            raise
        
        self.logger.info(f"This class only supports text input only, if you need image input or google search, please consider switching to GeminiClient")
        self._model_name = model_name
        
        self._history = []
        self._max_length = memories_length
        self._word_prompt = f"Please remember to answer with less than {limit_word_per_respond} words."
    
    @property
    def model_name(self):
        return self._model_name
    
    @property
    def history(self):
        # Returns the conversation history as a tuple.
        return tuple(self._history)
    
    @property
    def max_memory_length(self):
        # Returns the maximum length of the conversation history.
        return self._max_length

    @property
    def word_prompt(self):
        # Returns the word limit prompt.
        return self._word_prompt

    @max_memory_length.setter
    def max_memory_length(self, value) -> None:
        if isinstance(value, int) and value > 0:
            self._max_length = value
        else:
            raise ValueError("Memory length must be a positive integer.")
    
    def ask(self, prompt : str) -> str:
        #not str, return...
        self.__enforce_type(prompt, str, "prompt")
        
        if not prompt:
            self.logger.warning("WARNING: Empty prompt provided, skipping API call.")
            return None
        
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents = self._word_prompt + prompt)

            if response.text:
                answer = response.text
                self.logger.info("INFO: Received response successfully.")
                return answer
            else:
                self.logger.info("No response received. This could be due to safety filters or other reasons.") 
                return ""

        except Exception as e:
            self.logger.error(f"ERROR: An error occurred during the API call: {e}") # Replaced logging.error
            return ""
        
    def list_models(self, search : str = "") -> None:
        self.__enforce_type(search, str, "search")
        
        print("Retrieve available models: ")
        try:
            print("-" * 40)
            for model in self._client.models.list():
                if search in model.name:
                    print(f"Model: {model.name}")
                    print(f"  Name: {model.display_name}")
                    print(f"  Description: {model.description}")
                    print("-" * 40)
        except Exception as e:
            self.logger.error(f"Error retrieving models with new lib: {e}")
   
    def ask_and_copy_to_clipboard(self, prompt : str) -> str:
        answer = self.ask(prompt)
        if answer:
            try:
                pyperclip.copy(answer)
                self.logger.info("Copy to clipboard the answer")
            except Exception as e:
                self.logger.error(f"CANT COPY TO CLIPBOARD, {e}")
        return answer

    def ask_with_memories(self, prompt : str) -> str: # use if you want to store history to ask again (cap with memories_length)
        self.__enforce_type(prompt, str, "prompt") #check type
        
        if not prompt: #check if input
            self.logger.warning("WARNING: Empty prompt provided, skipping API call.")
            return None
        
        line = "Here's our previous conversation:\n"
        if self._history:
            for turn in self._history:
                line += f"User: {turn['question']}\nAI: {turn['answer']}\n"
        line += "Now, continue the conversation:\n"
        line += prompt
        answer = self.ask(line)
        self.__add_turn(prompt, answer)
        return answer
    
    def _clear_history(self) -> None:
        if self._history:
            self._history.clear()
    
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")
    
    def __add_turn(self, question, answer) -> None:
        self.__enforce_type(question, str, "question")
        self.__enforce_type(answer, str, "answer")

        while len(self._history) >= self._max_length: #change from if to while because the memories could now be modified
            self._history.pop(0)  # Remove the oldest turn
        self._history.append({"question": question, "answer": answer})
        

class GeminiClient:
    
    __api_key: str
    logger: logging.Logger
    _model_name: str
    client : genai.Client
    _history: list
    _max_length: int
    _word_prompt: str
    
    
    def __init__(self, model_name : str ='models/gemini-2.0-flash-lite', api_key : Optional[str] = None, memories_length : int = 4, limit_word_per_respond : int = 150):
        #check data type
        self.__enforce_type(memories_length, int, "memories_length")
        self.__enforce_type(limit_word_per_respond, int, "limit_word_per_respond")
        
        env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(env_path) # load if there is env file
        self.__api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.__api_key:
            raise ValueError("API key was not provided or found in the 'GEMINI_API_KEY' environment variable.")
        
        #check data type before proceed further into connecting
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(self.__api_key, str, "api_key")
        
        #logging
        self.logger = setup_logging(self.__class__.__name__)
        
        try:
            self._client = genai.Client(api_key=self.__api_key)
            self.logger.info("Gemini API configured successfully.")
        except Exception as e:
            self.logger.critical(f"Error configuring Gemini API: {e}")
            raise

        self._google_search_tool = Tool(google_search = GoogleSearch()) #init search tool for the LLM
        
        self._model_name = model_name
        
        self._history = []
        self._max_length = memories_length
        self._word_prompt = f"Please remember to answer with less than {limit_word_per_respond} words."
    
    @property
    def model_name(self):
        return self._model_name

    @property
    def history(self):
        # Returns the conversation history as a tuple.
        return tuple(self._history)

    @property
    def max_memory_length(self):
        # Returns the maximum length of the conversation history.
        return self._max_length

    @property
    def word_prompt(self):
        # Returns the word limit prompt.
        return self._word_prompt

    @max_memory_length.setter
    def max_memory_length(self, value) -> None:
        if isinstance(value, int) and value > 0:
            self._max_length = value
        else:
            raise ValueError("Memory length must be a positive integer.")
    
    def ask(self, prompt : str = None, img_path : str = None) -> str:
        #not str, return...
        self.__enforce_type(prompt, str, "prompt")
        self.__enforce_type(img_path, (str, type(None)), "img_path")
        
        if not prompt:
            self.logger.warning("WARNING: Empty prompt provided, skipping API call.")
            return ""
        
        prompt_parts = self.__prepare_prompt(prompt, img_path) #make the prompt to send
        
        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt_parts,
                config=GenerateContentConfig(
                    tools=[self._google_search_tool],
                    response_modalities=["TEXT"],
                )
            )
            
            if response.text:
                answer = response.text
                self.logger.info("INFO: Received response successfully.")
                return answer
            else:
                self.logger.info("No response received. This could be due to safety filters or other reasons.") 
                return ""
        
        except Exception as e:
            print(f"ERROR: An error occurred during the API call: {e}") # Replaced logging.error
            return ""

    def list_models(self, search : str = "") -> None:
        self.__enforce_type(search, str, "search")
        
        print("Retrieve available models: ")
        try:
            print("-" * 40)
            for model in self._client.models.list():
                if search in model.name:
                    print(f"Model: {model.name}")
                    print(f"  Name: {model.display_name}")
                    print(f"  Description: {model.description}")
                    print("-" * 40)
        except Exception as e:
            self.logger.error(f"Error retrieving models with new lib: {e}")
            
    def ask_and_copy_to_clipboard(self, prompt : str, img_path : str) -> str:
        answer = self.ask(prompt, img_path)
        if answer:
            try:
                pyperclip.copy(answer)
                self.logger.info("Copy to clipboard the answer")
            except Exception as e:
                self.logger.error(f"CANT COPY TO CLIPBOARD, {e}")
        return answer

    def ask_with_memories(self, prompt : str = None, img_path : str = None) -> str: # use if you want to store history to ask again (cap with memories_length)
        line = "Here's our previous conversation:\n"
        if self._history:
            for turn in self._history:
                line += f"User: {turn['question']}\nAI: {turn['answer']}\n"
        line += "Now, continue the conversation:\n"
        line += prompt
        answer = self.ask(line, img_path)
        self.__add_turn(prompt, answer)
        return answer
    
    def _clear_history(self) -> None:
        if self._history:
            self._history.clear()
    
    def __enforce_type(self, value, expected_types, arg_name):
        if not isinstance(value, expected_types):
            expected_names = [t.__name__ for t in expected_types] if isinstance(expected_types, tuple) else [expected_types.__name__]
            expected_str = ", ".join(expected_names)
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_str}, but received {type(value).__name__}")
    
    def __add_turn(self, question, answer) -> None:
        self.__enforce_type(question, str, "question")
        self.__enforce_type(answer, str, "answer")
        
        while len(self._history) >= self._max_length: #change from if to while because the memories could now be modified
            self._history.pop(0)  # Remove the oldest turn
        self._history.append({"question": question, "answer": answer})
    
    def __prepare_prompt(self, prompt : str, img_path : Union[str, None]) -> list:
        prompt_parts = [] # this is the actual prompt send to the model
        
        if img_path:
            try:
                img = Image.open(img_path)
                prompt_parts.append(img)
            except FileNotFoundError:
                self.logger.error(f"Image file not found: {img_path}")
                return ""
            except Exception as e:
                self.logger.error(f"Error loading image from {img_path}: {e}")
                return ""
        
        prompt_parts.append(self._word_prompt + prompt)
        
        return prompt_parts
    
if __name__ == "__main__":
    genbot = GeminiChatBot()
    genbot.list_models("2.5")
    genAI = GeminiClient()
    genAI.list_models()
    
    print(genbot.ask("Hi, how are you?"))
    print("AI : " + genAI.ask("Is the whether nice today?",))
    
    print(genbot.ask_with_memories("My name is Ngan, what about you?"))
    print(genbot.ask_with_memories("Hi, what are we talking about?"))
    print(genAI.ask_with_memories("Hi, my name is Huyen, what about you?"))
    print(genAI.ask_with_memories("Hi, what are we talking about?"))