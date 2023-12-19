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
COMICS_FILE_PATH = 'comics1.json'  # File to store the comics data
REFRESH_INTERVAL = 60 * 60 * 2  # Set the refresh interval to 2 hours
DISCORD_TOKEN = 'NjcwMDY0MDYxNjAxNDE1MTk5.GP4gwi.SmpF8pqkG7GIbJlvhdLQ0DJSd94ndb2BHayGLU'
USER_ID_TO_NOTIFY = 365659613821009920  # Replace with the user ID you want to notify
MAX_CHAPTERS_TO_NOTIFY = 5
MAX_MESSAGE_LENGTH = 2000

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def process_comic(comic):
    try:
        scraper = cfscrape.create_scraper()
        response = scraper.get(comic['api_url'].format(comic_id=comic['comic_id']))

        if response.status_code == 200 and response.text:
            data = response.json()
            chapters_data = []

            for chap in data.get('chapters', [])[:MAX_CHAPTERS_TO_NOTIFY]:
                if 'chap' in chap:
                    chapter_info = {
                        'Chapter': chap['chap'],
                        'Created': datetime.datetime.strptime(chap['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
                        'Updated': datetime.datetime.strptime(chap['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
                    }
                    chapters_data.append(chapter_info)

            if os.path.exists(LOG_FILE_PATH):
                with open(LOG_FILE_PATH, 'r') as log_file:
                    existing_log_data = json.load(log_file)

                if existing_log_data != chapters_data:
                    await send_private_message(comic['comic_id'], chapters_data[:MAX_CHAPTERS_TO_NOTIFY])

            with open(LOG_FILE_PATH, 'w') as log_file:
                json.dump(chapters_data, log_file, indent=2)

        else:
            print(f"Error for Comic {comic['comic_id']}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error for Comic {comic['comic_id']}: {e}")

async def send_private_message(comic_id, chapters_data):
    try:
        user = await bot.fetch_user(USER_ID_TO_NOTIFY)
        if user:
            for chapter_info in chapters_data:
                message = f"Chapter update detected for Comic {comic_id}!\n"
                chapter_message = (
                    f"Chapter {chapter_info['Chapter']}:\n"
                    f" - Created: {chapter_info['Created']}\n"
                    f" - Updated: {chapter_info['Updated']}\n"
                 #   f" - Comic Link: https://comick.app/comic/{comic_id}\n\n"
                 #   f" - Comic Link: https://comick.ink/comic/{comic_id}\n\n"
                    f" - Comic Link: https://comick.cc/comic/{comic_id}\n\n"

                )
                message += chapter_message

                await user.send(message)
        else:
            print(f"Error: User with ID {USER_ID_TO_NOTIFY} not found.")
    except Exception as e:
        print(f"Error sending private message for Comic {comic_id}: {e}")

@tasks.loop(seconds=REFRESH_INTERVAL)
async def get_comic_chapters():
    for comic in COMICS:
        await process_comic(comic)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')
    for comic in COMICS:
        await process_comic(comic)
    get_comic_chapters.start()

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