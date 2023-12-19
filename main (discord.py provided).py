import cfscrape
import datetime
import json
import os
import discord
from discord.ext import tasks

# Define the information for each comic
COMICS = [
    {
        'comic_id': 'bXUxIbHc',
        'api_url': 'https://api.comick.app/comic/{comic_id}/chapters',
        'comic_link': 'https://comick.app/comic/{comic_id}',
    },
    {
        'comic_id': 'uTrdHTHN',
        'api_url': 'https://api.comick.app/comic/{comic_id}/chapters?lang=en',
        'comic_link': 'https://comick.app/comic/{comic_id}',
    },
    {
        'comic_id': 'pws_rHUb',
        'api_url': 'https://api.comick.app/comic/{comic_id}/chapters?lang=en',
        'comic_link': 'https://comick.app/comic/{comic_id}',
    },
    # Add more comics as needed
]

LOG_FILE_PATH = 'chapter_log.txt'
REFRESH_INTERVAL = 60 * 60 * 20  # Set the refresh interval to 20 hours
DISCORD_TOKEN = 'NjcwMDY0MDYxNjAxNDE1MTk5.Gb8JTe.h2YxNB1mGgOxn9VhZgkcrc7wo-aenjxFCPpiJc'
USER_ID_TO_NOTIFY = 365659613821009920  # Replace with the user ID you want to notify
MAX_CHAPTERS_TO_NOTIFY = 5  # Adjust the maximum number of chapters to notify

MAX_MESSAGE_LENGTH = 2000  # Discord's maximum message length

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True  # Enable presence intent
intents.guilds = True  # Enable server members intent
intents.members = True  # Enable server members intent

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user.name}')

    # Send current chapters for each comic on bot activation
    for comic in COMICS:
        await send_current_chapters(comic)

    # Start the background task
    get_comic_chapters.start()

@tasks.loop(seconds=REFRESH_INTERVAL)
async def get_comic_chapters():
    for comic in COMICS:
        await process_comic(comic)

async def process_comic(comic):
    try:
        scraper = cfscrape.create_scraper()
        response = scraper.get(comic['api_url'].format(comic_id=comic['comic_id']))

        # Check if the response is successful (status code 200)
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

                    print(f"Comic {comic['comic_id']} - Chapter {chap['chap']}")
                    print(f" - Created: {chapter_info['Created']}")
                    print(f" - Updated: {chapter_info['Updated']}")

            # Check if the log file exists and content has changed
            if os.path.exists(LOG_FILE_PATH):
                with open(LOG_FILE_PATH, 'r') as log_file:
                    existing_log_data = json.load(log_file)

                if existing_log_data != chapters_data:
                    print(f"Log content has changed for Comic {comic['comic_id']}. Deleting the existing log file.")
                    os.remove(LOG_FILE_PATH)
                    await send_private_message(comic, chapters_data)
            else:
                print(f"Log file does not exist for Comic {comic['comic_id']}.")

            # Write the new log data to the file
            with open(LOG_FILE_PATH, 'w') as log_file:
                json.dump(chapters_data, log_file, indent=2)

        else:
            print(f"Error for Comic {comic['comic_id']}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error for Comic {comic['comic_id']}: {e}")

async def send_current_chapters(comic):
    await process_comic(comic)

async def send_private_message(comic, chapters_data):
    user = client.get_user(USER_ID_TO_NOTIFY)
    if user:
        message = f"Chapter update detected for Comic {comic['comic_id']}!\n"
        for chapter_info in chapters_data:
            chapter_message = (
                f"Chapter {chapter_info['Chapter']}:\n"
                f" - Created: {chapter_info['Created']}\n"
                f" - Updated: {chapter_info['Updated']}\n"
                f" - Comic Link: {comic['comic_link'].format(comic_id=comic['comic_id'])}\n\n"
            )

            # Check if adding the chapter message exceeds the maximum length
            if len(message) + len(chapter_message) > MAX_MESSAGE_LENGTH:
                # If it does, send the current message and start a new one
                await user.send(message)
                message = f"Chapter update detected for Comic {comic['comic_id']}!\n"

            message += chapter_message

        # Send the remaining message if any
        if len(message) > len(f"Chapter update detected for Comic {comic['comic_id']}!\n"):
            await user.send(message)
    else:
        print(f"Error: User with ID {USER_ID_TO_NOTIFY} not found.")

# Run the Discord bot
client.run(DISCORD_TOKEN)
