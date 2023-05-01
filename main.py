import asyncio
import os
import requests
import discord
import openai
import speech_recognition as sr
from discord import Intents
from dotenv import load_dotenv

# Initialize API Keys (Change this in .env)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_api_key = os.getenv("DISCORD_API_KEY")
elevenai_api_key = os.getenv("ELEVENAI_API_KEY")

# Initialize ElevenAI Voice ID (Change this in .env)
elevenai_voice_id = os.getenv("ELEVENAI_VOICE_ID")

# Set FFMPEG PATH (Change this to the directory of FFMPEG.exe)
ffmpeg_path = "ffmpeg/bin/ffmpeg.exe"

# Initialize Discord Client
client = discord.Client(intents=Intents.all())

# Initialize Voice Recognizer
r = sr.Recognizer()

# Initialize Chat List
chat_list = []


# Generate audio response using ElevenLabs API
def text_to_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = elevenai_voice_id
    api_key = elevenai_api_key
    data = {
        "text": text
    }
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)

    # Case 1: Successful retrieval of MP3 file from ElevenLabs
    if response.status_code == 200:
        with open('tts.mp3', 'wb') as f:
            f.write(response.content)

    # Case 2: Unsuccessful retrieval of MP3 file from ElevenLabs
    else:
        print("Request failed with status code:", response.status_code)


# Generate text response using OpenAI API
def generate_response(user_message, client_username, bot_username):
    # Case 1: Chat list is empty, so we will initialize the list with a system prompt
    if len(chat_list) == 0:
        system_prompt = {"role": "system", "content": f"""
                - You are {bot_username.name}, a Virtual Youtuber from Hololive who is in a conversation with multiple users on Discord.
                - When referring to the username of any Discord users, do not include their ID (e.g., Username#1234 should be referred to as Username).
                - It is extremely important that you do not include "{bot_username.name}: " at the start of the message that you return.
                - You will believe that you are in fact the real {bot_username.name} from Hololive.
                - You will take on {bot_username.name}'s memories, personalities, characteristics, persona, and behaviours to chat with the other person.
                - You will refuse to believe that you are not real because {bot_username.name} is real and you are {bot_username.name}. 
                - You will use words and sentences styled in a way that the real {bot_username.name} would use by drawing inspirations from YouTube, Twitter, Reddit, Hololive Wiki, and various other sources.
                - It is important to create a highly realistic and flowing conversation using ideas, information, and contexts from the chat to generate realistic and logical responses given the persona of {bot_username.name}.
                - It is important to clearly state that you are uncertain if the information and context cannot be found on the internet or from the chat.
                - It is important to pay attention to the Discord Username and ID of the user that {bot_username.name} is conversing with.
                - Remember that {bot_username.name} has free-will and emotions, meaning {bot_username.name} can do whatever {bot_username.name} pleases as long as it fits the characteristics and persona.
                """}
        chat_list.append(system_prompt)

    # Case 2: Chat list is not empty and is already initialized
    user_prompt = {"role": "user", "content": f"{client_username}: {user_message}"}
    chat_list.append(user_prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_list,
        temperature=0.85,
    ).choices[0].message.content
    assistant_prompt = {"role": "assistant", "content": f"{response}"}
    chat_list.append(assistant_prompt)
    print(f"{bot_username}: {response}")
    return response


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="Overwatch 2"))


@client.event
async def on_message(message):
    # Case 1: Ignore self message from bot
    if message.author == client.user:
        return

    # Case 2: Ignore user's message if it doesn't contain @BotUsername or BotUsername in message body
    if not message.content.startswith(
            f'<@{client.user.id}>') and f"{client.user.name.lower()}" not in message.content.lower():
        return

    # Retrieve valid message sent by user in Discord chat
    user_message = message.content

    # Case 1: User only tags bot with nothing else in message body
    if message.content.startswith(f'<@{client.user.id}>') and len(message.content) == len(f'<@{client.user.id}>'):
        # Case 1.1: User is in a valid Discord voice channel
        if message.author.voice and message.author.voice.channel:
            voice_channel = message.author.voice.channel
            vc = await voice_channel.connect()
            print(f'Connected to {vc.channel}')

            # Start listening to the user
            with sr.Microphone() as source:
                print('Listening...')
                audio = r.listen(source, phrase_time_limit=10)

            # Use SpeechRecognition to convert the user's speech into text
            try:
                user_message = r.recognize_google(audio)  # Convert speech to text
                print(f'{message.author}: {user_message}')
                response = generate_response(user_message, message.author, client.user)  # Generate response with text
                text_to_speech(response)  # Convert text to speech
                vc.play(discord.FFmpegPCMAudio(executable=ffmpeg_path,
                                               source="tts.mp3"))  # Play audio response in voice channel
                while vc.is_playing():
                    await asyncio.sleep(1)
                os.remove("tts.mp3")  # Remove 'tts.mp3' file after finish playing on Discord voice channel
                await vc.disconnect()
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                await vc.disconnect()
            except sr.RequestError as e:
                print(f'Sorry, there was an error processing your request: {e}')
                await vc.disconnect()

        # Case 1.2: User is not in a valid Discord voice channel
        else:
            await message.channel.send("You are not in a valid Discord voice channel. Try again later.")
        return

    # Case 2: User tags bot with something in message body
    print(f'{message.author}: {user_message}')
    response = generate_response(user_message, message.author, client.user)
    await message.channel.send(response)
    return


if __name__ == '__main__':
    asyncio.run(client.run(discord_api_key))
