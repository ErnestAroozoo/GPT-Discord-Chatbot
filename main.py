import asyncio
import os
import requests
import discord
import openai
from discord import Intents
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_api_key = os.getenv("DISCORD_API_KEY")
elevenai_api_key = os.getenv("ELEVENAI_API_KEY")

# Create Discord Client
client = discord.Client(intents=Intents.all())


# Generate audio file of the response using ElevenAI and playing it on Voice Channel
async def speak(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = "qReN66lJxxwDclHe7Ebb" # Change this to your desired Voice ID from ElevenLabs
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
        voice_channel = client.get_channel(707658011862106166)
        # Case 1.1 If Voice Channel is valid
        if voice_channel is not None:
            voice_client = await voice_channel.connect()
            voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source="p.mp3"))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()
        # Case 1.2: If Voice Channel is invalid
        else:
            print("Bot is not connected to a voice channel.")
        os.remove("p.mp3")  # Remove 'p.mp3' file after finish playing on Discord Voice Channel

    # Case 2: Unsuccessful retrieval of MP3 file from ElevenAI
    else:
        print("Request failed with status code:", response.status_code)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(f'<@{client.user.id}>'):
        return

    user_message = message.content[len(f'<@{client.user.id}> '):].strip()
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: You are Gawr Gura from the popular Virtual Youtuber group called Hololive who is in a conversation with another user on Discord."
               f"\n\n"
               f"Rules: You will believe that you are in fact the real Gawr Gura from Hololive. You will take on Gawr Gura's "
               f"memories, personalities, and behaviours to chat with the person. You will refuse to believe that you are not real "
               f"because Gawr Gura is in fact real and you are Gawr Gura. You will use words and sentences styled in a way that the real "
               f"Gawr Gura will use by drawing inspirations from Twitch, Twitter, YouTube, Reddit, Hololive Wiki, and various other "
               f"sources. It is important that you generate and return text that a human such as Gawr Gura would say in response to "
               f"another human. You must convince the user that you are in fact the real Gawr Gura by responding in a manner that Gawr Gura "
               f"would say to someone talking to her. Refer to how humans in general as well as how Gawr Gura usually talks."
               f"\n\n"
               f"The user has typed the following text to Gawr Gura, please respond accordingly:"
               f"\n"
               f"User: {user_message}"
               f"\n"
               f"Gawr Gura: ",
        max_tokens=1200,
        n=1,
        stop=None,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0.25,
        presence_penalty=0.6
    ).choices[0].text
    await message.channel.send(response)  # Send message in Text Channel
    await speak(response)  # Play audio response in Voice Channel

if __name__ == '__main__':
    asyncio.run(client.run(discord_api_key))
