# Discord Chatbot using GPT-3

This is a chatbot that utilizes OpenAI's GPT-3 to converse with users in Discord. By default, the chatbot takes on the persona of D.Va, a character from the popular game Overwatch.

## Requirements

- `openai`
- `discord`
- `asyncio`
- `os`
- `dotenv`

## Usage

1. Make sure you have the above requirements installed in your environment.
2. Clone this repository to your local machine.
3. Create a .env file in the root directory of this project and store your OpenAI API key and Discord API key in it.
4. Run the code by executing the following command in your terminal: `python main.py`

## API Keys

The API keys for OpenAI and Discord are stored in a .env file in the root directory. The code uses the `os` and `dotenv` libraries to retrieve the API keys from the .env file.
