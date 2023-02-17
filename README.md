# GPT-Discord-Chatbot

This is a chatbot that utilizes OpenAI's GPT-3 and ElevenLabs API to converse with users through text and voice on Discord. By default, the chatbot takes on the persona of Walter White, a popular character from Breaking Bad.

## Requirements

- `requests`
- `discord`
- `python-dotenv`
- `pyaudio`
- `SpeechRecognition`

## Usage

1. Make sure you have the above requirements installed in your environment.
2. Clone this repository to your local machine.
3. Create a .env file in the root directory of this project and store your OpenAI, ElevenLabs, and Discord API key in it.
4. Run the code by executing the following command in your terminal: `python main.py`

## API Keys

The API keys for OpenAI, ElevenLabs and Discord are stored in a .env file in the root directory. The code uses the `os` and `dotenv` libraries to retrieve the API keys from the .env file.

## Note
It is important to install the FFmpeg library in the same directory as main.py in order for the voice chat function to work appropriately.

To talk to the Discord chatbot in voice mode, simply tag the bot's username (e.g., @Bot).

To talk to the Discord chatbot in text mode, simply tag the bot's username followed by the message (e.g., @Bot Hey, tell me more about yourself).
