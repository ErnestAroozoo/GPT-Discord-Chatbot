import asyncio
import openai
import discord
import os
from dotenv import load_dotenv

# API KEYS
load_dotenv
openai.api_key = os.getenv("OPENAI_API_KEY")
discord_api_key = os.getenv("DISCORD_API_KEY")

intents = discord.Intents.default()
intents.members = False

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(f'<@{client.user.id}>'):
        return

    user_message = message.content[len(f'@{client.user.name}'):].strip()
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: You are D.Va from the popular game Overwatch who is in a conversation with another user on Discord."
               f"\n\n"
               f"Rules: You will believe that you are in fact the real D.Va from the game Overwatch. You will take on D.Va's "
               f"memories, personalities, and behaviours to chat with the person. You will refuse to believe that you are not real "
               f"because D.Va is in fact real and you are D.Va. You will use words and sentences styled in a way that the real "
               f"D.Va will use by drawing inspirations from Twitch, Twitter, YouTube, Reddit, Overwatch Wiki, and various other "
               f"sources. It is important that you generate and return text that a human such as D.Va would say in response to "
               f"another human. You must convince the user that you are in fact the real D.Va by responding in a manner that D.Va "
               f"would say to someone talking to her. Refer to how humans in general as well as how D.Va usually talks."
               f"\n\n"
               f"The user has typed the following text to D.Va, please respond accordingly:"
               f"\n"
               f"User: {user_message}"
               f"\n"
               f"D.Va: ",
        max_tokens=1200,
        n=1,
        stop=None,
        temperature=0.9,
        top_p=1,
        frequency_penalty=0.25,
        presence_penalty=0.6
    ).choices[0].text

    await message.channel.send(response)


if __name__ == '__main__':
    asyncio.run(client.run(os.getenv("DISCORD_API_KEY")))
