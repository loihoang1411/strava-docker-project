import requests
import json
import time

# Strava API endpoints
ACTIVITIES_URL = "https://www.strava.com/api/v3/clubs/775880/activities"

# Replace with your Strava API access token
#ACCESS_TOKEN = "65fe9e1b42e41ad2320d41010821c6426d2bf300"
ACCESS_TOKEN = "1c287a30d60cb34a629882b02c73258c44a7a5a5"
# Function to fetch activities from Strava API
def fetch_strava_activities(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": 10}  # Adjust the number of activities per page

    response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        activities = response.json()
        return activities
    else:
        print(f"Failed to fetch activities. Status Code: {response.status_code}")
        return []

# Function to load existing activities from JSON file
def load_existing_activities(filename):
    try:
        with open(filename, 'r') as json_file:
            existing_activities = json.load(json_file)
        return existing_activities
    except FileNotFoundError:
        return []

# Function to save activities to a JSON file, excluding duplicates
def save_activities_to_json(activities, filename):
    existing_activities = load_existing_activities(filename)
    
    # Filter out activities that are already in the existing_activities list
    new_activities = [activity for activity in activities if activity not in existing_activities]

    if new_activities:
        updated_activities = existing_activities + new_activities
        with open(filename, 'w') as json_file:
            json.dump(updated_activities, json_file, indent=4)
        print(f"{len(new_activities)} new activities appended to {filename}.")
    else:
        print("No new activities to save.")

if __name__ == "__main__":
    while True:
        activities = fetch_strava_activities(ACCESS_TOKEN)
        
        if activities:
            save_activities_to_json(activities, "strava_activities.json")
        else:
            print("No activities to save.")
        
        # Set the time interval (in seconds) for data collection
        time.sleep(60)  # Collect data every minute

