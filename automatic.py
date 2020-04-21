import datetime
import json
import logging
import os
from typing import List

import requests
from pymongo import MongoClient

from apscheduler.schedulers.blocking import BlockingScheduler
from main import main

logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_URL = os.environ["TELEGRAM_BOT_URL"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MONGO_URI = os.environ["MONGO_URI"]
DB_NAME = os.environ["DB_NAME"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]
CLIENT = MongoClient(MONGO_URI)

SCHED = BlockingScheduler(timezone="America/Santiago")

def send_message(message: str) -> None:
    send_url = f"{TELEGRAM_BOT_URL}/sendMessage"
    req_params = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.get(send_url, params=req_params)


def get_to_be_collected() -> List[int]:
    db = CLIENT[DB_NAME]
    collection = db[COLLECTION_NAME]
    date = datetime.datetime.combine(
        datetime.datetime.now(), datetime.datetime.min.time())
    query_results = list(collection.find({"date": date}))
    to_be_collected = [result["contest_name"] for result in query_results]
    logging.info(to_be_collected)
    return to_be_collected


def edit_collect_file(contest_name: str) -> None:
    with open("collect.json") as f:
        collect = json.load(f)

    collect["sheets"][0]["tabName"] = contest_name
    collect["sheets"][0]["contests"][0]["link"] = contest_name

    with open("collect.json", "w") as f:
        json.dump(collect, f, indent=4)


@SCHED.scheduled_job("cron", id="collect_labs", hour=0, minute=0)
def collect_labs() -> None:
    logging.info("Collecting")
    contests = get_to_be_collected()
    if not contests:
        send_message("There aren't any contests to collect today.")
    for contest in contests:
        edit_collect_file(contest)
        main()
        send_message(f"Contest: {contest} succesfully collected.")


SCHED.start()
