import os
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import requests
import openai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1264365566907650128
MAP_IMAGE_PATH = "metro-map-large.png"

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

last_updates = ""
message_sent = None
map_message_sent = None

MAX_MESSAGE_LENGTH = 1900

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


@tasks.loop(hours=1)
async def check_metro_updates():
    global last_updates, message_sent
    url = "https://www.nexus.org.uk/metro/updates"

    # Get the current hour
    current_hour = datetime.now().hour

    # Check if the current time is between 1 AM and 5 AM
    if 1 <= current_hour <= 5:
        print("Skipping updates check between 1 AM and 5 AM to save API requests.")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        updates_divs = soup.find_all('div', class_='views-row')
        if updates_divs:
            current_updates = ""
            for div in updates_divs:
                # Remove file size information and unnecessary line breaks
                for a_tag in div.find_all('a'):
                    if a_tag.text.endswith(')'):
                        a_tag.decompose()
                current_update = div.get_text(separator='\n', strip=True)
                current_update = ' '.join(current_update.split())
                current_updates += current_update + "\n\n"

            if current_updates != last_updates:
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that summarizes Metro service updates concisely and clearly, focusing on the key information relevant to passengers in bullet points and including any times the updates were posted. Exclude any anti-social behaviour information, and keep it brief."
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
                    summarized_updates = current_updates

                channel = bot.get_channel(CHANNEL_ID)
                if channel:
                    # Delete all previous messages in the channel except pinned ones
                    def check_not_pinned(message):
                        return not message.pinned

                    await channel.purge(limit=None, check=check_not_pinned)

                    await channel.send(f"**Nexus Metro Updates:**\n{summarized_updates}")
                    print(f"Sent Metro updates: {summarized_updates}")

                last_updates = current_updates
        else:
            print("Updates divs not found on the page.")

    except (requests.RequestException, AttributeError) as e:
        print(f"Error fetching or parsing updates: {e}")


@bot.event
async def on_ready():
    global map_message_sent
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        def check_not_pinned(message):
            return not message.pinned

        await channel.purge(limit=None, check=check_not_pinned)

        # Check if the map message already exists and is pinned
        pins = await channel.pins()
        for pin in pins:
            if pin.author == bot.user:
                map_message_sent = pin
                break

        if not map_message_sent:
            with open(MAP_IMAGE_PATH, 'rb') as f:
                image = discord.File(f)
                map_message_sent = await channel.send(file=image)
                await map_message_sent.pin()

    check_metro_updates.start()


bot.run(TOKEN)
