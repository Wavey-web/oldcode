import cfscrape
import datetime
import json
import os
import time

API_URL = 'https://api.comick.app/comic/{comic_id}/chapters'
LOG_FILE_PATH = 'chapter_log.txt'
REFRESH_INTERVAL = 60 * 60  # Set the refresh interval in seconds (e.g., 1 hour)

def get_comic_chapters(comic_id):
    try:
        scraper = cfscrape.create_scraper()
        while True:
            response = scraper.get(API_URL.format(comic_id=comic_id))

            # Check if the response is successful (status code 200)
            if response.status_code == 200:
                if response.text:  # Check if the response content is not empty
                    data = response.json()

                    if 'chapters' in data:
                        log_data = []  # List to store chapter information for logging

                        for chap in data['chapters']:
                            if 'chap' in chap:
                                chapter_info = {
                                    'Chapter': chap['chap'],
                                    'Created': datetime.datetime.strptime(chap['created_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'),
                                    'Updated': datetime.datetime.strptime(chap['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
                                }
                                log_data.append(chapter_info)

                                print(f"Chapter {chap['chap']}")
                                print(f" - Created: {chapter_info['Created']}")
                                print(f" - Updated: {chapter_info['Updated']}")

                        # Check if the log file exists
                        if os.path.exists(LOG_FILE_PATH):
                            with open(LOG_FILE_PATH, 'r') as log_file:
                                existing_log_data = json.load(log_file)

                            # Check if the content has changed
                            if existing_log_data != log_data:
                                print("Log content has changed. Deleting the existing log file.")
                                os.remove(LOG_FILE_PATH)
                        else:
                            print("Log file does not exist.")

                        # Write the new log data to the file
                        with open(LOG_FILE_PATH, 'w') as log_file:
                            json.dump(log_data, log_file, indent=2)

                else:
                    print("Error: Empty response")
            else:
                print(f"Error: {response.status_code} - {response.text}")

            time.sleep(REFRESH_INTERVAL)  # Wait for the refresh interval before making the next request

    except Exception as e:
        print(f"Error: {e}")

get_comic_chapters('bXUxIbHc')
