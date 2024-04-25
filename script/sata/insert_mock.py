"""
cleanup and insert mock data
"""

import random

import requests
from faker import Faker

host = "http://localhost:8000"
fake = Faker("ja_JP")


def create_user(data=None):
    if data is None:
        data = {
            "email": fake.email(domain="aoyama.jp"),
            "nickname": fake.name(),
            "password": "1",
        }
    url = host + "/user"
    res = requests.post(url, json=data)
    res.post_data = data
    return res


def login(email, password):
    return requests.post(
        host + "/token",
        data={"username": email, "password": password},
    )


def insert_mock_task():
    user_data = [
        {
            "email": f"u{i+1}@aoyama.jp",
            "nickname": fake.name(),
            "password": "1",
        }
        for i in range(5)
    ]
    for data in user_data:
        print(data["email"])
        res = create_user(data)

    num_of_tasks_for_each_user = [0, 0, 2, 10]
    random.shuffle(num_of_tasks_for_each_user)
    num_of_tasks_for_each_user.insert(0, 39)

    for user, num_of_tasks in zip(user_data, num_of_tasks_for_each_user):
        if num_of_tasks == 0:
            continue
        login_res = login(user["email"], user["password"])

        url = host + "/task"
        res_list = []
        for _ in range(num_of_tasks):
            payload = {
                "title": fake.sentence(nb_words=4),
                "due_date": str(fake.date_between("-3d", "+1M")),
            }

            res = requests.post(
                url,
                json=payload,
                cookies=login_res.cookies,
            )
            if not res.ok:
                print(res.json())
                raise Exception("Failed to insert mock task")
            res_list.append(res)

        # randomly add image to some tasks
        for res in random.sample(
            res_list, num_of_tasks // random.randint(2, 5)
        ):
            image_res = requests.put(
                f"{url}/{res.json()['id']}/image",
                files={"image": ("image.png", fake.image(), "image/png")},
                cookies=login_res.cookies,
            )
            if not image_res.ok:
                print(res.json())
                raise Exception("Failed to add image to mock task")

        # randomly done some tasks
        for res in random.sample(
            res_list, num_of_tasks // random.randint(2, 5)
        ):
            done_res = requests.put(
                f"{url}/{res.json()['id']}/done",
                cookies=login_res.cookies,
            )
            if not done_res.ok:
                print(res.json())
                raise Exception("Failed to done mock task")


if __name__ == "__main__":
    insert_mock_task()
