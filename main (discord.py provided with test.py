import cfscrape
import datetime
import json
import os
import discord
from discord.ext import tasks, commands


LOG_FILE_PATH = 'chapter_log.txt'
COMICS_FILE_PATH = 'comics.json'  # File to store the comics data

# Define initial comics
DEFAULT_COMICS = [
    {
        'comic_id': 'bXUxIbHc',
        'api_url': 'https://api.comick.cc/comic/{comic_id}/chapters',
        'comic_link': 'https://comick.cc/comic/{comic_id}',
    },
    {
        'comic_id': 'uTrdHTHN',
        'api_url': 'https://api.comick.cc/comic/{comic_id}/chapters?lang=en',
        'comic_link': 'https://comick.cc/comic/{comic_id}',
    },
    {
        'comic_id': 'pws_rHUb',
        'api_url': 'https://api.comick.cc/comic/{comic_id}/chapters?lang=en',
        'comic_link': 'https://comick.cc/comic/{comic_id}',
    },
]

def load_comics():
    global COMICS
    if os.path.exists(COMICS_FILE_PATH):
        with open(COMICS_FILE_PATH, 'r') as file:
            COMICS = json.load(file)
    else:
        COMICS = DEFAULT_COMICS

# Load comics at bot startup
load_comics()

# Dictionary to store dynamically added comics
comics_data = {}

LOG_FILE_PATH = 'chapter_log.txt'
COMICS_FILE_PATH = 'comics.json'  # File to store the comics data
REFRESH_INTERVAL = 60 * 60 * 2  # Set the refresh interval to 2 hours
DISCORD_TOKEN = '-'
USER_ID_TO_NOTIFY = 365659613821009920  # Replace with the user ID you want to notify
MAX_CHAPTERS_TO_NOTIFY = 5
MAX_MESSAGE_LENGTH = 2000

# Intents for Discord bot
#intents = discord.Intents.default()
#intents.message_content = True
#intents.presences = True
#intents.guilds = True
#intents.members = True

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.guilds = True
intents.members = True

# Initialize Discord bot
bot = commands.Bot(command_prefix='!', intents=intents)

async def send_notification_message(message, channel_id):
    try:
        channel = await client.fetch_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            print(f"Error: Channel with ID {channel_id} not found.")
    except Exception as e:
        print(f"Error sending message to channel {channel_id}: {e}")

#def send_notification_message(message, channel_id):
    # Replace this with the actual code to send a message to the specified Discord channel
#    print(f"Sending message to channel {channel_id}:")
#    print(message)

#@tasks.loop(seconds=REFRESH_INTERVAL)
#async def process_chapters():
#    try:
#        scraper = cfscrape.create_scraper()
#        response = scraper.get('https://api.comick.cc/chapter?accept_erotic_content=true&page=1&device-memory=8&order=new')
#
#        if response.status_code == 200 and response.text:
#            data = response.json()
#
#            if isinstance(data, list):
#                for idx, chapter in enumerate(data, start=1):
#                    try:
#                        chapter_info = {
#                            'Chapter': chapter.get('chap', 'Unknown Chapter'),
#                            'Last Updated At': datetime.datetime.strptime(chapter.get('last_at', ''), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S') if chapter.get('last_at') else 'Unknown',
#                            'Created At': datetime.datetime.strptime(chapter.get('created_at', ''), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S') if chapter.get('created_at') else 'Unknown',
#                            'Updated At': datetime.datetime.strptime(chapter.get('updated_at', ''), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S') if chapter.get('updated_at') else 'Unknown',
#                            'Comic ID': chapter.get('hid', 'Unknown ID'),
#                            'Title': chapter['md_comics']['title'] if 'md_comics' in chapter and 'title' in chapter['md_comics'] else 'Unknown Title',
#                            'Country': chapter.get('country', 'Unknown Country')
#                        }
#
#                        message = "New Chapter Update:\n"
#                        for key, value in chapter_info.items():
#                            message += f"{key}: {value}\n"
#
#                        channel_id = 1185841250616750090  # Replace with your channel ID
#                        channel = await bot.fetch_channel(channel_id)
#                        if channel:
#                            await channel.send(message)
#                        else:
#                            print(f"Error: Channel with ID {channel_id} not found.")
#                    except Exception as e:
#                        error_message = f"Error processing chapter {idx}: {e}\nChapter {idx} data: {chapter}\n"
#                        print(error_message)
#                        with open('error_log.txt', 'a', encoding='utf-8') as error_log:
#                            error_log.write(f"{datetime.datetime.now()} - {error_message}\n")
#            else:
#                error_message = "Error: Response data is not in the expected list format."
#                print(error_message)
#                with open('error_log.txt', 'a', encoding='utf-8') as error_log:
#                    error_log.write(f"{datetime.datetime.now()} - {error_message}\n")
#
#    except Exception as e:
#        error_message = f"Error in process_chapters: {e}"
#        print(error_message)
#        with open('error_log.txt', 'a', encoding='utf-8') as error_log:
#           error_log.write(f"{datetime.datetime.now()} - {error_message}\n")

@tasks.loop(seconds=REFRESH_INTERVAL)
async def process_chapters():
    try:
        scraper = cfscrape.create_scraper()
        response = scraper.get('https://api.comick.cc/chapter?accept_erotic_content=true&page=1&device-memory=8&order=new')

        if response.status_code == 200 and response.text:
            data = response.json()

            if isinstance(data, list):
                for idx, chapter in enumerate(data, start=1):
                    try:
                        if chapter.get('lang') == 'en':  # Filter for English chapters only
                            md_comics_data = chapter.get('md_comics', {})
                            comic_id = md_comics_data.get('hid', 'Unknown HID')
                            comic_url = f"https://comick.cc/comic/{comic_id}"

                            chapter_info = {
                                'Chapter': chapter.get('chap', 'Unknown Chapter'),
                                'Last Updated At': datetime.datetime.strptime(chapter.get('last_at', ''), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S') if chapter.get('last_at') else 'Unknown',
                                'Created At': datetime.datetime.strptime(chapter.get('created_at', ''), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S') if chapter.get('created_at') else 'Unknown',
                                'Updated At': datetime.datetime.strptime(chapter.get('updated_at', ''), '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S') if chapter.get('updated_at') else 'Unknown',
                                'Comic ID': comic_id,
                                'Title': md_comics_data.get('title', 'Unknown Title'),
                                'Country': chapter.get('country', 'Unknown Country')
                            }

                            message = f"New Chapter Update:\n"
                            for key, value in chapter_info.items():
                                message += f"{key}: {value}\n"
                            
                            # Include the comic URL in the message
                            message += f"Comic URL: {comic_url}"

                            channel_id = 1185841250616750090  # Replace with your channel ID
                            channel = await bot.fetch_channel(channel_id)
                            if channel:
                                await channel.send(message)
                            else:
                                print(f"Error: Channel with ID {channel_id} not found.")
                    except Exception as e:
                        error_message = f"Error processing chapter {idx}: {e}\nChapter {idx} data: {chapter}\n"
                        print(error_message)
                        with open('error_log.txt', 'a', encoding='utf-8') as error_log:
                            error_log.write(f"{datetime.datetime.now()} - {error_message}\n")
            else:
                error_message = "Error: Response data is not in the expected list format."
                print(error_message)
                with open('error_log.txt', 'a', encoding='utf-8') as error_log:
                    error_log.write(f"{datetime.datetime.now()} - {error_message}\n")

    except Exception as e:
        error_message = f"Error in process_chapters: {e}"
        print(error_message)
        with open('error_log.txt', 'a', encoding='utf-8') as error_log:
            error_log.write(f"{datetime.datetime.now()} - {error_message}\n")



#async def process_comic(comic):
#    try:
#        scraper = cfscrape.create_scraper()
#        response = scraper.get(comic['api_url'].format(comic_id=comic['comic_id']))
#
#        if response.status_code == 200 and response.text:
#            data = response.json()
#            chapters_data = []
#
#            for chap in data.get('chapters', [])[:MAX_CHAPTERS_TO_NOTIFY]:
#                if 'chap' in chap:
#                    chapter_info = {
#                        'Chapter': chap['chap'],
#                        'Created': datetime.datetime.strptime(chap['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
#                        'Updated': datetime.datetime.strptime(chap['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
#                    }
#                    chapters_data.append(chapter_info)
#
#            if os.path.exists(LOG_FILE_PATH):
#                with open(LOG_FILE_PATH, 'r') as log_file:
#                    existing_log_data = json.load(log_file)
#
#                if existing_log_data != chapters_data:
#                    await send_private_message(comic['comic_id'], chapters_data[:MAX_CHAPTERS_TO_NOTIFY])
#
#            with open(LOG_FILE_PATH, 'w') as log_file:
#                json.dump(chapters_data, log_file, indent=2)
#
#        else:
#            print(f"Error for Comic {comic['comic_id']}: {response.status_code} - {response.text}")
#
#    except Exception as e:
#        print(f"Error for Comic {comic['comic_id']}: {e}")
#
#
#    except Exception as e:
#        error_message = f"Error in process_new_feature: {e}"
#        print(error_message)
#        # Log the error message
#        with open('error_log.txt', 'a') as error_log:
#            error_log.write(f"{datetime.datetime.now()} - {error_message}\n")



#@tasks.loop(seconds=REFRESH_INTERVAL)
#async def get_comic_chapters():
#    for comic in COMICS:
#        await process_comic(comic)



@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
#    for comic in COMICS:
#        await process_comic(comic)
#    get_comic_chapters.start()
    process_chapters.start()

@bot.command(name='addcomic')
async def add_comic(ctx, comic_id: str):
    global COMICS
    for comic in COMICS:
        if comic['comic_id'] == comic_id:
            await ctx.send(f"Comic with ID {comic_id} already exists.")
            return

    new_comic_template = {
        'comic_id': comic_id,
        'api_url': f'https://api.comick.cc/comic/{comic_id}/chapters?lang=en',
        'comic_link': f'https://comick.cc/comic/{comic_id}',
    }

    COMICS.append(new_comic_template)
    await ctx.send(f"Comic with ID {comic_id} added successfully!")
    await process_comic(new_comic_template)

    with open(COMICS_FILE_PATH, 'w') as file:
        json.dump(COMICS, file, indent=2)

bot.run(DISCORD_TOKEN)
