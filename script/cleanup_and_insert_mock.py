"""
cleanup and insert mock data
"""
import random

import requests
from faker import Faker

host = "http://localhost:8000"


def delete_all():
    url = host + "/tasks"
    res = requests.get(url)
    for task in res.json():
        requests.delete(f"{url}/{task['id']}")


def insert_mock_task():
    url = host + "/tasks"
    fake = Faker("ja_JP")
    res_list = []
    for _ in range(39):
        payload = {
            "title": fake.sentence(nb_words=4),
            "due_date": str(fake.date_between("-3d", "+1M")),
        }

        res = requests.post(url, json=payload)
        if not res.ok:
            print(res.json())
            raise Exception("Failed to insert mock task")
        res_list.append(res)

    # randomly done some tasks
    for res in random.sample(res_list, 10):
        requests.put(f"{url}/{res.json()['id']}/done")
        if not res.ok:
            print(res.json())
            raise Exception("Failed to done mock task")


if __name__ == "__main__":
    delete_all()
    insert_mock_task()
