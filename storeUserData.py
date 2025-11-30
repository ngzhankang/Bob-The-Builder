import json
import os

USER_DATA_FILE: "userData.json"

# load user data if previously recorded things such as bmi and age are inside already
def LoadUserData():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# for first timers, save the data for future 
def SaveUserProfile(user_id: int, data: dict):
    users = LoadUserData()
    users[str(user_id)] = data
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

# retrieve user profile and then ltr inject into prompt to reduce hallucination
def GetUserProfile(user_id: int):
    users = LoadUserData()
    return users.get(str(user_id))

# delete user profile if requested
def DeleteUserProfile(user_id: int):
    users = LoadUserData()
    users.pop(str(user_id), None)
    with open(USER_DATA_FILE, "W") as f:
        json.dump(users, f, indent=4)