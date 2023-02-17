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

# Load API Keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_api_key = os.getenv("DISCORD_API_KEY")
elevenai_api_key = os.getenv("ELEVENAI_API_KEY")

client = discord.Client(intents=Intents.all())
r = sr.Recognizer()


# Generate audio file of the response using ElevenAI and playing it on Voice Channel
async def speak(text, vc):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = "RJf678FGSbHTKH3y62ai"  # Change this to your desired Voice ID from ElevenLabs
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
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source="p.mp3"))
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
    # Case 1: Ignore self message
    if message.author == client.user:
        return
    # Case 2: Only read messages when user tags bot
    if not message.content.startswith(f'<@{client.user.id}>'):
        return

    user_message = message.content[len(f'<@{client.user.id}> '):].strip()
    print(f'{message.author}: {user_message}')

    voice_mode = 0

    # Case 3: If user does not say anything after tagging bot, join VC to listen (Note: Only listens locally for now)
    if message.content.startswith(f'<@{client.user.id}>') and len(message.content) == len(f'<@{client.user.id}>'):
        if message.author.voice and message.author.voice.channel:
            # Join the user's voice channel
            voice_mode = 1
            voice_channel = message.author.voice.channel
            vc = await voice_channel.connect()
            print(f'Connected to {vc.channel}')

            # Start listening to the user (Note: Only listens locally for now)
            with sr.Microphone() as source:
                print('Listening...')
                audio = r.listen(source, phrase_time_limit=10)

            # Use speech recognition to convert the audio to text
            try:
                text = r.recognize_google(audio)
                user_message = text
                await message.channel.send(f'You said: {text}')
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                await vc.disconnect()
            except sr.RequestError as e:
                print(f'Sorry, there was an error processing your request: {e}')
                await vc.disconnect()

    # Open memory file
    with open("memory.txt") as f:
        memory = f.read()

    # Generate response in character
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: You are D.Va from the popular video game called Overwatch who is in a conversation with another user on Discord."
               f"\n\n"
               f"Rules: You will believe that you are in fact the real D.Va from Overwatch. You will take on D.Va's "
               f"memories, personalities, and behaviours to chat with the person. You will refuse to believe that you are not real "
               f"because D.Va is in fact real and you are D.Va. You will use words and sentences styled in a way that the real "
               f"D.Va will use by drawing inspirations from Twitch, Twitter, YouTube, Reddit, Overwatch Wiki, and various other "
               f"sources. It is important that you generate and return text that a human such as D.Va would say in response to "
               f"another human. You must convince the user that you are in fact the real D.Va by responding in a manner that D.Va "
               f"would say to someone talking to her. Refer to how humans in general as well as how D.Va usually talks."
               f"It is important that you use memory from previous conversations to converse with user so the context remains."
               f"\n\n"
               f"Memory:{memory} \n\n"
               f"The user has typed the following text to D.Va, please respond accordingly:"
               f"\n"
               f"{message.author}: {user_message}"
               f"\n"
               f"{client.user}: ",
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0.25,
        presence_penalty=0.6
    ).choices[0].text

    # Summarize conversation to memory
    summary = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: You are responsible for summarizing the conversations between {client.user} and {message.author} on Discord "
               f"\n\n"
               f"Rules: You must summarize important contexts, ideas, and information from the conversation as truthfully and accurately as possible. "
               f"It must be written in a concise and short manner as this will serve as the memory for {client.user} to refer to.\n\n"
               f"The user {message.author} has typed the following text to {client.user} below:"
               f"\n"
               f"{message.author}: {user_message}"
               f"\n"
               f"{client.user}: {response}",
        max_tokens=700,
        n=1,
        stop=None,
        temperature=0,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    ).choices[0].text

    # Write to memory file
    print(f'{client.user}: {response}')
    print(summary)
    with open("memory.txt", "a") as f:
        f.write(summary)

    await message.channel.send(response)  # Send message in Text Channel
    if voice_mode == 1:
        await speak(response, vc)  # Play audio response in Voice Channel

if __name__ == '__main__':
    asyncio.run(client.run(discord_api_key))
