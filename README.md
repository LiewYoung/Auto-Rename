# Before you start

1. Install Python 3.10 or higher.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your Zhipu AI API key:
   Create a file named `config.json` in the same directory as the scripts, with the following content:
   ```json
   {
       "header": {
           "Authorization": "Bearer YOUR_API_KEY_HERE",
           "Content-Type": "application/json"
       }
   }
   ```
   Replace `YOUR_API_KEY_HERE` with your actual Zhipu AI API key.

# What is this?  

Is an Auto Renamer for files  

# How to use it?

1. Ensure you have completed the steps in "Before you start".
2. Run the `chat.py` script:
   ```bash
   python chat.py
   ```
3. Enter the directory path when prompted.
4. Enjoy!

# Want to change ai model?

1. Open the api_chat.py
2. Change the model name/url...
3. Enjoy!