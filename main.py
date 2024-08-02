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

stations = {
    "Airport": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/APT/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/APT/2"
    },
    "Bank Foot": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/BFT/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/BFT/2"
    },
    "Bede": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/BDE/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/BDE/2"
    },
    "Benton": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/BTN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/BTN/2"
    },
    "Brockley Whins": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/BNR/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/BNR/2"
    },
    "Byker": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/BYK/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/BYK/2"
    },
    "Callerton Parkway": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/CAL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/CAL/2"
    },
    "Central Station": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/CEN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/CEN/2"
    },
    "Chichester": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/CHI/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/CHI/2"
    },
    "Chillingham Road": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/CRD/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/CRD/2"
    },
    "Cullercoats": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/CUL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/CUL/2"
    },
    "East Boldon": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/EBL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/EBL/2"
    },
    "Fawdon": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/FAW/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/FAW/2"
    },
    "Felling": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/FEL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/FEL/2"
    },
    "Fellgate": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/FEG/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/FEG/2"
    },
    "Four Lane Ends": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/FLE/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/FLE/2"
    },
    "Gateshead": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/GHD/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/GHD/2"
    },
    "Gateshead Stadium": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/GST/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/GST/2"
    },
    "Hadrian Road": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/HDR/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/HDR/2"
    },
    "Haymarket": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/HAY/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/HAY/2"
    },
    "Hebburn": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/HEB/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/HEB/2"
    },
    "Heworth": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/HEW/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/HEW/2"
    },
    "Howdon": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/HOW/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/HOW/2"
    },
    "Ilford Road": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/ILF/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/ILF/2"
    },
    "Jarrow": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/JAR/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/JAR/2"
    },
    "Jesmond": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/JES/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/JES/2"
    },
    "Kingston Park": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/KSP/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/KSP/2"
    },
    "Longbenton": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/LBN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/LBN/2"
    },
    "Manors": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/MAN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/MAN/2"
    },
    "Meadow Well": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/MWL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/MWL/2"
    },
    "Millfield": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/MLF/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/MLF/2"
    },
    "Monkseaton": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/MSN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/MSN/2"
    },
    "Monument": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/MMT/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/MMT/2",
        "Platform 3": "https://metro-rti.nexus.org.uk/api/times/MMT/3",
        "Platform 4": "https://metro-rti.nexus.org.uk/api/times/MMT/4"
    },
    "Northumberland Park": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/NPK/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/NPK/2"
    },
    "North Shields": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/NSH/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/NSH/2"
    },
    "Pallion": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/PAL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/PAL/2"
    },
    "Palmersville": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/PMV/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/PMV/2"
    },
    "Park Lane": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/PLI/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/PLI/2"
    },
    "Pelaw": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/PLW/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/PLW/2"
    },
    "Percy Main": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/PCM/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/PCM/2"
    },
    "Regent Centre": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/RGC/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/RGC/2"
    },
    "Seaburn": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SBN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SBN/2"
    },
    "Shiremoor": {
            "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SMR/1",
            "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SMR/2"
        },
    "Simonside": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SMD/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SMD/1"
    },
    "South Hylton": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SHL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SHL/2"
    },
    "South Shields": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SSS/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SSS/2"
    },
    "St James": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SJM/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SJM/2"
    },
    "St Peter's": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/STZ/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/STZ/2"
    },
    "Stadium of Light": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SFC/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SFC/2"
    },
    "Sunderland": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/SUN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/SUN/2"
    },
    "Tyne Dock": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/TDK/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/TDK/2"
    },
    "Tynemouth": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/TYN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/TYN/2"
    },
    "University": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/UNI/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/UNI/2"
    },
    "Wallsend": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/WSD/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/WSD/2"
    },
    "Walkergate": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/WKG/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/WKG/2"
    },
    "Wansbeck Road": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/WBR/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/WBR/2"
    },
    "West Jesmond": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/WJS/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/WJS/2"
    },
    "West Monkseaton": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/WMN/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/WMN/2"
    },
    "Whitley Bay": {
        "Platform 1": "https://metro-rti.nexus.org.uk/api/times/WTL/1",
        "Platform 2": "https://metro-rti.nexus.org.uk/api/times/WTL/2"
    },
}

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
