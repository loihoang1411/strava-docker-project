import requests
import json
import time
import mysql.connector
from mysql.connector import Error

# Strava API endpoints
ACTIVITIES_URL = "https://www.strava.com/api/v3/clubs/775880/activities"

# Replace with your Strava API access token
ACCESS_TOKEN = "f982a81e755be4d35026c1f0bd919514ff694f2c"


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

# MySQL database configuration
DB_HOST = "172.18.0.2"
DB_USER = "root"
DB_PASSWORD = "mypass"
DB_NAME = "collectorDB"

# Function to load activities from JSON file
def load_activities_from_json(filename):
    try:
        with open(filename, 'r') as json_file:
            activities = json.load(json_file)
        return activities
    except FileNotFoundError:
        return []

# Function to create the table if it doesn't exist
def create_table_if_not_exists():
#    global connection
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()

        # Check if the table exists
        table_exists = False
        cursor.execute("SHOW TABLES LIKE 'strava_activities'")
        if cursor.fetchone():
            table_exists = True

        # If the table doesn't exist, create it
        if not table_exists:
            cursor.execute("""
                CREATE TABLE strava_activities (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    activity_name VARCHAR(255),
                    moving_time INT,
                    distance FLOAT,
                    elapsed_time INT,
                    total_elevation_gain FLOAT,
                    sport_type VARCHAR(255),
                    workout_type VARCHAR(255)
                )
            """)
            connection.commit()
            print("Table 'strava_activities' created.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Add a function to check for duplicate activities in the database
def is_duplicate_activity(activity, cursor):
    activity_id = activity.get("id")
    cursor.execute("SELECT id FROM strava_activities WHERE activity_id = %s", (activity_id,))
    return cursor.fetchone() is not None

# Function to save activities to a MySQL database
def save_activities_to_mysql(activities, host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()

            for activity in activities:
                if not is_duplicate_activity(activity, cursor):
                    activity_name = activity.get("name")
                    first_name = activity.get("athlete", {}).get("firstname")
                    last_name = activity.get("athlete", {}).get("lastname")
                    distance = activity.get("distance")
                    moving_time = activity.get("moving_time")
                    elapsed_time = activity.get("elapsed_time")
                    total_elevation_gain = activity.get("total_elevation_gain")
                    sport_type = activity.get("sport_type")
                    workout_type = activity.get("workout_type")
                    activity_id = activity.get("id")

                insert_query = "INSERT INTO strava_activities (activity_id, activity_name, first_name, last_name, distance, moving_time,elapsed_time, total_elevation_gain, sport_type, workout_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data_tuple = (activity_id, activity_name, first_name, last_name, distance, moving_time, elapsed_time, total_elevation_gain, sport_type, workout_type)
                cursor.execute(insert_query, data_tuple)

            connection.commit()
            print(f"{len(activities)} activities saved to MySQL database.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    while True:
        activities = fetch_strava_activities(ACCESS_TOKEN)

        if activities:
            save_activities_to_json(activities, "strava_activities.json")
            create_table_if_not_exists()
            activities = load_activities_from_json("strava_activities.json")
            if activities:
                save_activities_to_mysql(activities, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
            else:
                print("No activities to save to MySQL.")

        # Set the time interval (in seconds) for data collection
        time.sleep(60)  # Collect data every minute

