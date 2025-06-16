"""
This module provides the Chat class for interacting with the Zhipu AI API.

It handles API key management, request formatting, and response parsing
for generating titles based on input text.
"""
"""
This module provides the Chat class for interacting with the Zhipu AI API.

It handles API key management, request formatting, and response parsing
for generating titles based on input text.
"""
import requests as rq
from pathlib import Path
import json
import re # Import re for sanitization
from typing import Dict # For older Python versions, for 3.9+ use dict

class Chat:
    """
    Manages interactions with the Zhipu AI API for chat completions.

    This class loads the API key from a configuration file, prepares
    request headers and data, and processes responses to extract relevant
    information (e.g., a generated title). It also supports logging
    API responses.
    """
    def __init__(
            self,
            max_token: int = 1024,
            temperature: float = 0.9,
            top_p: float = 0.9,
            model: str = 'glm-zero-preview',
            CC_Chat: bool = False,  # 연속 대화 예약 매개변수 (Continuous conversation reserved parameter)
            log: bool = False  # 대화 로그 저장 여부 (Whether to save conversation logs)
        ):
        """
        Initializes the Chat object.

        Loads the API key from 'config.json' and sets up chat parameters.

        :param max_token: Maximum number of tokens to generate.
        :param temperature: Sampling temperature for generation.
        :param top_p: Nucleus sampling parameter.
        :param model: The model to use for chat completions.
        :param CC_Chat: Reserved parameter for continuous conversation (currently unused).
        :param log: If True, API responses will be logged to files.
        :raises FileNotFoundError: If 'config.json' is not found.
        :raises KeyError: If 'Authorization' key is missing in 'config.json'.
        """
        self.max_token: int = max_token
        self.temperature: float = temperature
        self.top_p: float = top_p
        self.model: str = model
        self.CC_Chat: bool = CC_Chat
        self.log: bool = log
        self.api_key: str

        try:
            with open("config.json", "r", encoding="utf-8") as f: # Added encoding
                config_data: dict = json.load(f)
            self.api_key = config_data['header']['Authorization']
            # The problem states to assume "Bearer " is included in config.json.
            # No explicit check here based on that assumption.
        except FileNotFoundError:
            # Consider logging this instead of printing, or raising a custom exception
            print("Error: config.json not found. Please create it with your API key.")
            raise
        except KeyError:
            print("Error: 'Authorization' key not found in config.json header. Please check the file structure.")
            raise
    
    def __get_header(self) -> dict:
        """
        Constructs the request headers for the API call.

        :return: A dictionary containing the authorization and content type.
        """
        header: dict = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
        }
        return header
    
    def __get_data(self, file_include: str) -> dict:
        """
        Constructs the request data payload for the API call.

        :param file_include: The text content to be included in the user message.
        :return: A dictionary representing the JSON payload for the API.
        """
        data: dict = {
            'model': self.model, # Use the model specified in __init__
            'messages':[
            {
                'role':'system',
                'content':'你会获得文件内容并归类为标题（title）必须是中文.您应该始终遵循指令并输出一个有效的JSON对象。请根据指令使用指定的JSON对象结构。如果不确定，请默认使用 {"answer": "$your_answer","title":"$your_title"}。确保始终以 "```" 结束代码块，以指示JSON对象的结束。',
            },
            {
                'role':'user',
                'content': file_include,
            },
        
            ],
            'response_format': {
                'type':'json_object'
            },
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_token,
        }
        return data
    
    def get_title(self, file_include: str) -> str:
        """
        Retrieves a title from the Zhipu AI API based on the input text.

        Makes a POST request to the chat completions endpoint and extracts
        the title from the JSON response. Logs the response if `self.log` is True.

        :param file_include: The text content to get a title for.
        :return: The generated title, or a default title like "空文件" (Empty File)
                 or "解析错误" (Parsing Error) if an issue occurs.
        """
        header: dict = self.__get_header()
        data: dict = self.__get_data(file_include=file_include)

        try:
            response = rq.post('https://open.bigmodel.cn/api/paas/v4/chat/completions', headers=header, json=data)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            response_json: dict = response.json()
            # It's good practice to check if 'choices' and its elements exist
            if response_json.get('choices') and response_json['choices'][0].get('message') and response_json['choices'][0]['message'].get('content'):
                content_str = response_json['choices'][0]['message']['content']
                title_data: dict = json.loads(content_str)
                title: str = title_data.get('title', '解析错误') # Default if 'title' key is missing
            else:
                print('Unexpected response structure:', response_json)
                title = '解析错误'

        except rq.exceptions.RequestException as e:
            print(f"API Request failed: {e}")
            title = 'API请求失败' # API Request Failed
        except KeyError:
            # This might be more specific if we know what key is missing from response_json
            print(f'KeyError during response parsing. file_include: {file_include}, response: {response.text if response else "No response"}')
            title = '空文件' # Or consider a more generic error like '解析错误'
        except json.JSONDecodeError:
            print(f'JSONDecodeError for content: {content_str if "content_str" in locals() else "Unknown"}. file_include: {file_include}')
            title = '解析错误'
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred in get_title: {e}")
            title = '未知错误' # Unknown error

        if self.log:
            log_dir = Path('log')
            log_dir.mkdir(parents=True, exist_ok=True)

            # Sanitize title for use in filename
            # Keep word characters (alphanumeric and underscore), dots, and hyphens. Replace others with an underscore.
            sanitized_title = re.sub(r'[^\w\.-]', '_', title)

            # If the title consists only of characters that are replaced,
            # or if the original title was empty, sanitized_title could be empty or just underscores.
            if not sanitized_title.strip('_'): # Check if it's empty or only underscores
                sanitized_title = "invalid_title_log"

            # Truncate long filenames (e.g., to 100 characters for the title part)
            truncated_sanitized_title = sanitized_title[:100]

            log_file_name = f'Title_{truncated_sanitized_title}.json'
            log_file_path = log_dir / log_file_name

            try:
                # Determine log content
                log_content_data = "No response object"
                if 'response' in locals() and response is not None:
                    if response.headers.get('Content-Type') == 'application/json':
                        try:
                            log_content_data = response.json()
                        except json.JSONDecodeError:
                            log_content_data = response.text # Fallback to text if JSON parsing fails
                    else:
                        log_content_data = response.text

                json_to_write = json.dumps(log_content_data, ensure_ascii=False, indent=4)
                log_file_path.write_text(json_to_write, encoding="utf-8")
            except Exception as log_e:
                print(f"Failed to write log file {log_file_path}: {log_e}")

        return title
        

    
if __name__ == '__main__':
    # Example usage:
    # Ensure config.json is present with a valid API key for this to run.
    print("Attempting to initialize Chat and get a title for '你好'...")
    try:
        chat_bot = Chat(log=True) # Enable logging for testing
        sample_title = chat_bot.get_title(file_include='你好 世界') # "Hello World"
        print(f"Generated title: {sample_title}")
    except FileNotFoundError:
        print("Test run failed: config.json not found. Please create it for testing.")
    except KeyError:
        print("Test run failed: API key not found in config.json. Please check it for testing.")
    except Exception as e:
        print(f"An error occurred during the test run: {e}")