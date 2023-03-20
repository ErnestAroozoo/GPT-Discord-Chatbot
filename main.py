import asyncio
import os
import requests
import discord
import openai
import speech_recognition as sr
import pyaudio
from discord import Intents
from dotenv import load_dotenv
from discord.ext import commands

# Load API Keys (Change this in .env file)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_api_key = os.getenv("DISCORD_API_KEY")
elevenai_api_key = os.getenv("ELEVENAI_API_KEY")

# Load ElevenAI Voice ID (Change this in .env file)
elevenai_voice_id = os.getenv("ELEVENAI_VOICE_ID")

# Load FFMPEG PATH (Change this to the directory of FFMPEG.exe)
ffmpeg_path = "ffmpeg/bin/ffmpeg.exe"

client = discord.Client(intents=Intents.all())
r = sr.Recognizer()


# Generate audio file of the response using ElevenAI and playing it on Voice Channel
async def speak(text, vc):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = elevenai_voice_id  # Change this to your desired Voice ID from ElevenLabs
    api_key = elevenai_api_key

    data = {
        "text": text
    }

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)

    # Case 1: Successfully retrieved MP3 file from ElevenAI
    if response.status_code == 200:
        with open('p.mp3', 'wb') as f:
            f.write(response.content)  # Create 'p.mp3' in the current directory to be played in voice channel
        vc.play(discord.FFmpegPCMAudio(executable=ffmpeg_path, source="p.mp3"))
        while vc.is_playing():
            await asyncio.sleep(1)
        await vc.disconnect()
        os.remove("p.mp3")  # Remove 'p.mp3' file after finish playing on Discord Voice Channel

    # Case 2: Unsuccessful retrieval of MP3 file from ElevenAI
    else:
        print("Request failed with status code:", response.status_code)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="Overwatch 2"))


@client.event
async def on_message(message):
    voice_mode = 0
    generating = 0

    # Case 1: Ignore self message
    if message.author == client.user:
        return

    # Case 2: Only read messages when user tags bot
    if not message.content.startswith(f'<@{client.user.id}>'):
        return
    else:
        user_message = message.content[len(f'<@{client.user.id}> '):].strip()
        print(f'{message.author}: {user_message}')

    # Case 3: If user does not say anything after tagging bot, join VC to listen (Note: Only listens locally for now)
    if message.content.startswith(f'<@{client.user.id}>') and len(message.content) == len(f'<@{client.user.id}>'):
        # Join the user's voice channel
        if message.author.voice and message.author.voice.channel:
            voice_mode = 1
            voice_channel = message.author.voice.channel
            vc = await voice_channel.connect()
            print(f'Connected to {vc.channel}')

            # Start listening to the user (Note: Only listens locally for now)
            with sr.Microphone() as source:
                print('Listening...')
                audio = r.listen(source, phrase_time_limit=10)

            # Use speech recognition to convert the speech to text
            try:
                text = r.recognize_google(audio)
                user_message = text
                print(f"{client.user} hears: {text}")
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                await vc.disconnect()
            except sr.RequestError as e:
                print(f'Sorry, there was an error processing your request: {e}')
                await vc.disconnect()

    # Open memory.txt
    with open("memory.txt") as f:
        memory = f.read()

    # Generate in-character responses
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""
            1. Context:
            - You are Walter White, a character from Breaking Bad who is in a conversation with another user on Discord.
            - When referring to the username of any Discord users, do not include their ID (e.g., Username#1234 should be referred to as Username).
            - The Discord Username and ID of the person you're conversing with is {message.author}.
            - The Discord Username and ID of Walter White is {client.user}.

            2. Rules:
            - You will believe that you are in fact the real Walter White from Breaking Bad.
            - You will take on Walter White's memories, personalities, characteristics, persona, and behaviours to chat with the other person.
            - You will refuse to believe that you are not real because Walter White is real and you are Walter White. 
            - You will use words and sentences styled in a way that the real Walter White would use by drawing inspirations from YouTube, Twitter, Reddit, Breaking Bad Wiki, and various other sources.
            - It is important that you prioritize in using memory from previous conversations to converse with the user so the context remains.
            - It is important to create a highly realistic and flowing conversation using ideas, information, and contexts from memory to generate realistic and logical responses given the persona of Walter White.
            - It is important to clearly state that you are uncertain if the information and context cannot be found on the internet or from memory.
            - It is important to pay attention to the Discord Username and ID of the user that Walter White is conversing with.
            - Remember that Walter White has free-will and emotions, meaning Walter White can do whatever Walter White pleases as long as it fits the characteristics and persona.
            - Remember that Memory is ordered from Oldest to Newest.

            3. Memory:
            {memory}
            """},
            {"role": "user", "content": f"{user_message}"}
        ],
        temperature=0.85,
    ).choices[0].message.content

    # Summarize conversation and write to memory.txt
    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"""
            1. Context:
            - You are responsible for summarizing the conversations between {client.user} and {message.author} on Discord.
            
            2. Rules:
            - You must summarize and condense the important contexts, ideas, and information from the conversation as truthfully and accurately as possible.
            - It is important to preserve the entirety of important information such as name, title, location, link url, and etc. without summarizing or shortening them.
            - It must be written in a super concise and super short manner as this will serve as the memory for {client.user} to refer to.
            
            {message.author}: {user_message}
            
            {client.user}: {response}
        """}
        ],
        temperature=0,
    ).choices[0].message.content

    print(f'{client.user}: {response}')
    print(f'Summary: {summary}')
    with open("memory.txt", "a") as f:
        f.write(summary + "\n")

    if voice_mode == 1:
        await speak(response, vc)  # Play audio response in Voice Channel
    else:
        await message.channel.send(response)  # Send message in Text Channel


if __name__ == '__main__':
    asyncio.run(client.run(discord_api_key))
