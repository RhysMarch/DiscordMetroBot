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
last_update = None

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@tasks.loop(minutes=5)
async def check_metro_updates():
    global last_update, last_message

    url = "https://www.nexus.org.uk/metro/updates"
    try:
        print("Fetching Metro updates...")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check if the div with updates exists, using a more specific class
        updates_div = soup.find('div', class_="views-element-container")
        if updates_div:
            current_update = updates_div.get_text(separator='\n').strip()

            if current_update != last_update:
                last_update = current_update
                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    if last_message:  # Check if there was a previous message
                        await last_message.delete()  # Delete the old message
                    embed = discord.Embed(title="Nexus Metro Updates", description=current_update, color=0x00ff00)
                    last_message = await channel.send(embed=embed)  # Store the new message
    except (requests.RequestException, AttributeError) as e:
        print(f"Error fetching or parsing updates: {e}")


async def main():  # async function to start the bot
    async with bot:
        check_metro_updates.start()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
