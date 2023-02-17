# GPT Discord Chatbot

This is a Discord chatbot written in Python. It can generate audio responses using the ElevenLabs text-to-speech API and respond to user messages using OpenAI's GPT-3 language model. It also has the ability to listen to a user's speech and convert it to text using the SpeechRecognition library. By default, the chatbot takes on the persona of Walter White, a character from Breaking Bad.

![](https://github.com/ErnestAroozoo/GPT-Discord-Chatbot/blob/main/tutorial.png)

## Requirements

This program requires Python 3.8 or later, as well as several Python libraries including:

- asyncio
- os
- requests
- discord
- openai
- speech_recognition
- pyaudio

Additionally, you will need to obtain API keys from ElevenAI and Discord to use this program.

## Usage

1. Clone the repository and navigate to the project directory.
2. Install the required libraries by running `pip install -r requirements.txt`.
3. Create a `.env` file and enter your API keys and other settings.
4. Run the program by running `python main.py`.

## Features

- Responds to user messages using OpenAI's GPT-3 language model.
- Listens to a user's speech and converts it to text using the SpeechRecognition library.
- Generates audio responses using the ElevenLabs text-to-speech API.
- Plays generated audio responses in a Discord voice channel.

## Configuration

This program uses a `.env` file to store configuration settings. The following environment variables are used:

- `OPENAI_API_KEY`: Your OpenAI API key.
- `DISCORD_API_KEY`: Your Discord API key.
- `ELEVENAI_API_KEY`: Your ElevenAI API key.
- `ELEVENAI_VOICE_ID`: The ID of the voice you want to use for the ElevenAI text-to-speech API.
- `FFMPEG_PATH`: The path to your FFMPEG executable.

## Note

The chatbot listens locally for voices for now.

