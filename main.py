import os
import asyncio
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1264365566907650128

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_update = ""
message_sent = None


@tasks.loop(minutes=1)  # Check for updates every minute
async def check_metro_updates():
    global last_update, message_sent
    url = "https://www.nexus.org.uk/metro/updates"

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')


        updates_div = soup.find('div', class_='views-row')
        if updates_div:
            current_update = updates_div.get_text(separator='\n', strip=True)

            if current_update != last_update:
                last_update = current_update
                channel = bot.get_channel(CHANNEL_ID)

                if channel:
                    if message_sent:
                        await message_sent.edit(content=f"**Nexus Metro Updates:**\n{current_update}")
                    else:
                        message_sent = await channel.send(f"**Nexus Metro Updates:**\n{current_update}")

                    print(f"Sent Metro update: {current_update}")
        else:
            print("Updates div not found on the page.")

    except (requests.RequestException, AttributeError) as e:
        print(f"Error fetching or parsing updates: {e}")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    check_metro_updates.start()  # Start the update task


asyncio.run(bot.start(TOKEN))
