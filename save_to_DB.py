import json
import mysql.connector
from mysql.connector import Error
import time

# MySQL database configuration
DB_HOST = "localhost"
DB_USER = "collectorDB"
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
                activity_name = activity.get("name")
                first_name = activity.get("athlete", {}).get("firstname")
                last_name = activity.get("athlete", {}).get("lastname")
                distance = activity.get("distance")
                moving_time = activity.get("moving_time")
                elapsed_time = activity.get("elapsed_time")
                total_elevation_gain = activity.get("total_elevation_gain")
                sport_type = activity.get("sport_type")
                workout_type = activity.get("workout_type")

                insert_query = "INSERT INTO strava_activities (activity_name, first_name, last_name, distance, moving_time,elapsed_time, total_elevation_gain, sport_type, workout_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                data_tuple = (activity_name, first_name, last_name, distance, moving_time, elapsed_time, total_elevation_gain, sport_type, workout_type)
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

    create_table_if_not_exists()  # Create the table if it doesn't exist

    while True:
        activities = load_activities_from_json("strava_activities.json")
        
        if activities:
            save_activities_to_mysql(activities, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        else:
            print("No activities to save.")
        
        # Set the time interval (in seconds) for continuous execution
        time.sleep(60)  # Execute every minute

