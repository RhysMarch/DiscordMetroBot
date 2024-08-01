import os
import asyncio
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests
import openai
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1264365566907650128

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_updates = ""
message_sent = None

MAX_MESSAGE_LENGTH = 1900

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


@tasks.loop(minutes=1)
async def check_metro_updates():
    global last_updates, message_sent
    url = "https://www.nexus.org.uk/metro/updates"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        updates_divs = soup.find_all('div', class_='views-row')
        if updates_divs:
            current_updates = ""
            for div in updates_divs:
                current_update = div.get_text(separator='\n', strip=True)
                current_update = ' '.join(current_update.split())
                current_updates += current_update + "\n\n"

            if current_updates != last_updates:
                # Summarize the updates using OpenAI API
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that summarizes Metro service updates in a concise and user-friendly manner in bullet points. Focus on the key information relevant to passengers, excluding antisocial behaviour reporting. Include the date and time of the update if provided. Keep each summary point to a maximum of two short sentences."
                            },
                            {
                                "role": "user",
                                "content": f"Please summarize these Metro updates:\n{current_updates}"
                            }
                        ]
                    )
                    summarized_updates = response.choices[0].message.content.strip()
                except openai.OpenAIError as e:
                    print(f"Error summarizing updates with OpenAI API: {e}")
                    summarized_updates = current_updates  # Fall back to original if error

                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    # Split the summarized updates if they exceed the maximum length
                    if len(summarized_updates) > MAX_MESSAGE_LENGTH:
                        split_messages = [summarized_updates[i:i + MAX_MESSAGE_LENGTH]
                                          for i in range(0, len(summarized_updates), MAX_MESSAGE_LENGTH)]
                        for i, part in enumerate(split_messages):
                            message_sent = None
                            header = "**Nexus Metro Updates:**\n" if i == 0 else ""
                            await channel.send(f"{header}{part}")
                    else:
                        if message_sent:
                            await message_sent.edit(content=f"**Nexus Metro Updates:**\n{summarized_updates}")
                        else:
                            message_sent = await channel.send(f"**Nexus Metro Updates:**\n{summarized_updates}")

                    print(f"Sent Metro updates: {summarized_updates}")

                last_updates = current_updates
        else:
            print("Updates divs not found on the page.")

    except (requests.RequestException, AttributeError) as e:
        print(f"Error fetching or parsing updates: {e}")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    check_metro_updates.start()


bot.run(TOKEN)
