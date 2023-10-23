# strava-docker-project
My project still has several bugs.
Instructions:
1. Create volume: docker volume create --name=mysql
2. Change authen_token: line 11 in file call_and_save.py. Anyone who wants to test; must have authen_token because it resets every 6 hours.
3. Open port 3000 in the host running the project.
