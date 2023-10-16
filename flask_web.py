from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# MySQL database configuration
DB_HOST = "localhost"
DB_USER = "collectorDB"
DB_PASSWORD = "mypass"
DB_NAME = "collectorDB"

@app.route('/')
def display_data():
    # Connect to MySQL and fetch data
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM strava_activities")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('index.html', data=rows)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=3000)

