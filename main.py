import requests
from dotenv import load_dotenv
from datetime import datetime
from loguru import logger
import time
import os

hashmap = {}
count = 0

RED = 15548997
YELLOW = 16705372
GREEN = 5763719


def send_error(error):
    requests.post(os.getenv("WEBHOOK_URL"), json={
        "content": error,
        "username": "Mouli Alert",
        "avatar_url": "https://cdn.discordapp.com/attachments/785951129187778614/1184883690283741295/BjbgphqX3BpyAAAAAElFTkSuQmCC.png?ex=658d97ed&is=657b22ed&hm=ddbb51c4efbe4ecf213861a1ecd595e79df070b58975cf5035391678777c4077&",
        "attachments": []
    })


def send_message(message):
    requests.post(os.getenv("WEBHOOK_URL"), json={
        "content": None,
        "embeds": [
            {
                "description": "{}".format(message),
                "color": 3158326
            }
        ],
        "username": "Mouli Alert",
        "avatar_url": "https://cdn.discordapp.com/attachments/785951129187778614/1184883690283741295/BjbgphqX3BpyAAAAAElFTkSuQmCC.png?ex=658d97ed&is=657b22ed&hm=ddbb51c4efbe4ecf213861a1ecd595e79df070b58975cf5035391678777c4077&",
        "attachments": []
    })


def send_webhook(job):
    if count == 1:
        return
    date_obj = datetime.strptime(job["date"], "%Y-%m-%dT%H:%M:%S.%fZ")
    date = date_obj.strftime("%d/%m/%y, %H:%M:%S")
    percent = job["trace"]["total_tests_percentage"]
    if job["trace"]["result"] == "FUNCTIONAL":
        if percent >= 75:
            color = GREEN
        elif percent >= 15:
            color = YELLOW
        else:
            color = RED
    else:
        color = RED
    requests.post(os.getenv("WEBHOOK_URL"), json={
        "content": "<@{}>".format(os.getenv("DISCORD_ID")),
        "embeds": [
            {
                "title": "Une nouvelle moulinette est disponible !",
                "color": color,
                "fields": [
                    {
                        "name": "Projet",
                        "value": "» `{}`".format(job["trace"]["instance"]["projectName"]),
                        "inline": True
                    },
                    {
                        "name": "Résultat :",
                        "value": "» `{:.2f}%`".format(percent),
                        "inline": True
                    },
                    {
                        "name": "État :",
                        "value": "» `{}`".format(job["trace"]["result"]),
                        "inline": True
                    },
                    {
                        "name": "Date :",
                        "value": "» `{}`".format(date),
                        "inline": True
                    },
                    {
                        "name": "Repository :",
                        "value": "» [Lien]({})".format(job["trace"]["githubUrl"]),
                        "inline": True
                    }
                ]
            }
        ],
        "username": "Mouli Alert",
        "avatar_url": "https://cdn.discordapp.com/attachments/785951129187778614/1184883690283741295"
                      "/BjbgphqX3BpyAAAAAElFTkSuQmCC.png?ex=658d97ed&is=657b22ed&hm"
                      "=ddbb51c4efbe4ecf213861a1ecd595e79df070b58975cf5035391678777c4077&",
        "attachments": []
    })


def check_data(job, project_name, commit_hash):
    if project_name in hashmap:
        if hashmap[project_name] != commit_hash:
            hashmap[project_name] = commit_hash
            send_webhook(job)
    else:
        hashmap[project_name] = commit_hash
        send_webhook(job)


def main():
    global count
    token = os.getenv("TOKEN")

    data = requests.get("https://tekme.eu/api/profile/moulinettes", headers={'Authorization': token})
    if data.status_code != 200:
        print("Error while getting moulinette data (status code {})".format(data.status_code))
        send_error("Error while getting moulinette data (status code {})".format(data.status_code))
        logger.error("Error while getting moulinette data (status code {})".format(data.status_code))
        return
    full_data = data.json()

    logger.info("Checking for new moulinette... (nb: {})".format(count))
    count += 1
    for job in full_data["jobs"]:
        if "gitCommit" not in job["trace"]:
            continue
        git_commit = job["trace"]["gitCommit"]
        project_name = job["trace"]["instance"]["projectName"]
        check_data(job, project_name, git_commit)


if __name__ == "__main__":
    load_dotenv()
    send_message("**Mouli Alert is now running!**")
    print("Mouli Alert is now running!")
    logger.remove(0)
    logger.add("app.log", format="{level} : {time} : {message}: {process}")
    try:
        while True:
            try:
                main()
            except Exception as e:
                print("Error while running main function : ", e)
                send_error("Error while running main function : {}".format(e))
                logger.error("Error while running main function : {}".format(e))
            time.sleep(int(os.getenv("TIME")))

    except KeyboardInterrupt:
        send_message("**Mouli Alert has been stopped!**")
        exit(0)
