# # * FOR DEBUGGING
# import sys
# from pathlib import Path

# sys.path.insert(0, str(Path(__file__).parent.parent))


from pathlib import Path
import unittest

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text

from api.main import app
from tests.utils import setup_testing_db

fake = Faker("ja_JP")


class AppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app, cls.engine = setup_testing_db(app)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.client = TestClient(self.app)
        self._reset_database()

    def tearDown(self):
        self._reset_database()

    def _reset_database(self):
        with self.engine.connect() as connection:
            # Drop all tables
            result = connection.execute(
                text(
                    """SELECT name FROM sqlite_master
                    WHERE type='table' AND name != 'sqlite_sequence';"""
                )
            )
            tables = result.fetchall()
            for table in tables:
                connection.execute(text(f"DROP TABLE IF EXISTS {table[0]}"))

            # Create tables
            sql_commands = (
                Path("./init.sql")
                .read_text()
                .replace("AUTO_INCREMENT", "AUTOINCREMENT")
                .split(";")
            )
            for command in sql_commands:
                if command.strip():
                    connection.execute(text(command.strip()))

    def create_user(self, data=None):
        if data is None:
            data = {
                "email": fake.email(),
                "password": fake.password(length=12),
            }
        res = self.client.post("/user", json=data)
        res.post_data = data
        return res

    def login(self, username, password):
        return self.client.post(
            "/token",
            data={
                "username": username,
                "password": password,
            },
        )

    def create_user_and_login(self, data=None):
        user_res = self.create_user(data)
        login_json = self.login(
            user_res.post_data["email"],
            user_res.post_data["password"],
        ).json()

        token_type = login_json["token_type"]
        access_token = login_json["access_token"]
        auth_headers = {
            "Authorization": f"{token_type} {access_token}",
        }
        return user_res, auth_headers

    def create_task(self, auth_headers, data=None):
        """Create a task and return the response"""
        if data is None:
            data = {"title": fake.sentence(nb_words=4)}
        res = self.client.post("/task", json=data, headers=auth_headers)

        if res.status_code == status.HTTP_401_UNAUTHORIZED:
            raise Exception("You need to login first", res)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        return res


class TestUserRouter(AppTestCase):
    def test_create_user(self):
        res = self.create_user()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # response should not contain password
        self.assertNotIn("password", res.json())

    def test_login(self):
        user_res = self.create_user()
        login_res = self.login(
            user_res.post_data["email"],
            user_res.post_data["password"],
        )

        res_json = login_res.json()

        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", res_json)
        self.assertIn("token_type", res_json)
        self.assertEqual(res_json["token_type"], "bearer")

    def test_login_with_invalid_password(self):
        user_res = self.create_user()
        login_res = self.login(user_res.post_data["email"], "invalid_password")

        self.assertEqual(login_res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestTaskRouter(AppTestCase):

    def test_create_task(self):
        test_data = [
            (
                "task with title only",
                {"title": fake.sentence(nb_words=4)},
                status.HTTP_200_OK,
            ),
            (
                "task with title and due_date",
                {
                    "title": fake.sentence(nb_words=4),
                    "due_date": str(fake.date_between("-3d", "+1M")),
                },
                status.HTTP_200_OK,
            ),
            (
                "task with invalid due_date",
                {
                    "title": fake.sentence(nb_words=4),
                    "due_date": "invalid date",
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
        ]

        for _ in range(3):
            self.create_user()
        user_res, auth_headers = self.create_user_and_login()
        user_id = user_res.json()["id"]

        for test_name, data, expected_status_code in test_data:
            with self.subTest(test_name):
                res = self.client.post(
                    "/task", json=data, headers=auth_headers
                )
                self.assertEqual(res.status_code, expected_status_code)
                if expected_status_code == status.HTTP_200_OK:
                    res_json = res.json()
                    self.assertIn("id", res_json)
                    self.assertEqual(res_json["user_id"], user_id)
                    self.assertEqual(res_json["title"], data["title"])
                    if "due_date" not in data:
                        continue
                    self.assertEqual(res_json["due_date"], data["due_date"])

    def test_create_task_without_login(self):
        with self.assertRaises(Exception) as e:
            self.create_task(None)
        res = e.exception.args[1]
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_multiple_tasks(self):
        res_user, auth_headers = self.create_user_and_login()
        user_id = res_user.json()["id"]

        # Create many tasks
        insert_list = []
        for _ in range(39):
            res = self.create_task(auth_headers)
            insert_list.append(res.json())

        # every task should res.user_id=user_id
        self.assertEqual(
            set([task["user_id"] for task in insert_list]),
            {user_id},
        )

        # Get the task
        res = self.client.get("/tasks", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_json = res.json()
        self.assertEqual(
            set([task["title"] for task in res_json]),
            set([task["title"] for task in insert_list]),
        )

    def test_get_multiple_tasks_with_empty_db(self):
        _, auth_headers = self.create_user_and_login()

        res = self.client.get("/tasks", headers=auth_headers)
        res_json = res.json()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_json), 0)

    def test_get_multiple_tasks_without_login(self):
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_task(self):
        _, auth_headers = self.create_user_and_login()

        # Create a task
        created_task = self.create_task(auth_headers)
        created_task_json = created_task.json()
        task_id = created_task_json["id"]

        # Get the task
        res = self.client.get(f"/task/{task_id}", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), {**created_task_json, "done": False})

    def test_get_non_existent_task(self):
        _, auth_headers = self.create_user_and_login()

        res = self.client.get("/task/1", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_task_with_not_logged_in(self):
        res = self.client.get("/task/1")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_other_user_task(self):
        _, user1_auth_headers = self.create_user_and_login()
        created_task = self.create_task(user1_auth_headers)
        created_task_json = created_task.json()
        task_id = created_task_json["id"]

        _, user2_auth_headers = self.create_user_and_login()
        res = self.client.get(f"/task/{task_id}", headers=user2_auth_headers)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task(self):
        _, auth_headers = self.create_user_and_login()

        created_task = self.create_task(auth_headers)
        task_id = created_task.json()["id"]

        update_data = {"title": fake.sentence(nb_words=4)}
        res = self.client.put(
            f"/task/{task_id}", json=update_data, headers=auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_task = res.json()
        new_task = self.client.get(f"/task/{task_id}", headers=auth_headers)

        self.assertEqual(updated_task["title"], update_data["title"])
        self.assertEqual({**updated_task, "done": False}, new_task.json())

    def test_update_non_existent_task(self):
        _, auth_headers = self.create_user_and_login()

        update_data = {"title": fake.sentence(nb_words=4)}
        res = self.client.put(
            "/task/1", json=update_data, headers=auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task_without_login(self):
        update_data = {"title": fake.sentence(nb_words=4)}
        res = self.client.put("/task/1", json=update_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_other_user_task(self):
        _, user1_auth_headers = self.create_user_and_login()
        created_task = self.create_task(user1_auth_headers)
        task_id = created_task.json()["id"]

        _, user2_auth_headers = self.create_user_and_login()
        update_data = {"title": fake.sentence(nb_words=4)}
        res = self.client.put(
            f"/task/{task_id}", json=update_data, headers=user2_auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task(self):
        _, auth_headers = self.create_user_and_login()

        # Create a task
        created_task = self.create_task(auth_headers)
        task_id = created_task.json()["id"]

        # Check if the task is created
        res = self.client.get(f"/task/{task_id}", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete the task
        res = self.client.delete(f"/task/{task_id}", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Check if the task is deleted
        res = self.client.get(f"/task/{task_id}", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existent_task(self):
        _, auth_headers = self.create_user_and_login()

        non_existent_task_id = 9999
        res = self.client.delete(
            f"/task/{non_existent_task_id}", headers=auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task_without_login(self):
        res = self.client.delete("/task/1")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_other_user_task(self):
        _, user1_auth_headers = self.create_user_and_login()
        created_task = self.create_task(user1_auth_headers)
        task_id = created_task.json()["id"]

        _, user2_auth_headers = self.create_user_and_login()
        res = self.client.delete(
            f"/task/{task_id}", headers=user2_auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_done_flag(self):
        _, auth_headers = self.create_user_and_login()

        # Create a task
        created_task = self.create_task(auth_headers)
        task_id = created_task.json()["id"]

        # 完了フラグを立てる
        res = self.client.put(f"/task/{task_id}/done", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 既に完了フラグが立っているので400を返却
        res = self.client.put(f"/task/{task_id}/done", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # 完了フラグを外す
        res = self.client.delete(f"/task/{task_id}/done", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 既に完了フラグが外れているので404を返却
        res = self.client.delete(f"/task/{task_id}/done", headers=auth_headers)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_done_flag_with_non_existent_task(self):
        _, auth_headers = self.create_user_and_login()

        non_existent_task_id = 9999
        res = self.client.put(
            f"/task/{non_existent_task_id}/done", headers=auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_done_flag_without_login(self):
        res = self.client.put("/task/1/done")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.delete("/task/1/done")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_done_flag_other_user_task(self):
        _, user1_auth_headers = self.create_user_and_login()
        task_id_1 = self.create_task(user1_auth_headers).json()["id"]
        task_id_2 = self.create_task(user1_auth_headers).json()["id"]

        self.client.put(f"/task/{task_id_2}/done", headers=user1_auth_headers)

        _, user2_auth_headers = self.create_user_and_login()
        res = self.client.put(
            f"/task/{task_id_1}/done", headers=user2_auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.delete(
            f"/task/{task_id_1}/done", headers=user2_auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        res = self.client.delete(
            f"/task/{task_id_2}/done", headers=user2_auth_headers
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_image_to_task(self):
        _, auth_headers = self.create_user_and_login()

        fake_image = fake.image()

        created_task = self.create_task(auth_headers)
        task_id = created_task.json()["id"]

        res = self.client.put(
            f"/task/{task_id}/image",
            files={"image": ("image.jpg", fake_image, "image/jpeg")},
            headers=auth_headers,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        task_detail = self.client.get(
            f"/task/{task_id}", headers=auth_headers
        ).json()
        self.assertEqual(task_detail["img_path"], res.json()["img_path"])

        updated_task = res.json()
        image_res = self.client.get(updated_task["img_path"])

        self.assertEqual(image_res.status_code, status.HTTP_200_OK)
        # delete the image
        Path(f".{updated_task['img_path']}").unlink()
        self.assertEqual(fake_image, image_res.content)

    def test_add_heif_image_to_task(self):
        _, auth_headers = self.create_user_and_login()

        fake_heif_image = fake.image(image_format="heif")
        task_id = self.create_task(auth_headers).json()["id"]

        res = self.client.put(
            f"/task/{task_id}/image",
            files={"image": ("image.heic", fake_heif_image, "image/heic")},
            headers=auth_headers,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        updated_task = res.json()
        image_res = self.client.get(updated_task["img_path"])

        self.assertEqual(image_res.status_code, status.HTTP_200_OK)
        # delete the image
        Path(f".{updated_task['img_path']}").unlink()
        self.assertEqual("image/jpeg", image_res.headers["content-type"])

    def test_add_image_to_task_with_non_existent_task(self):
        _, auth_headers = self.create_user_and_login()

        fake_image = fake.image()

        res = self.client.put(
            "/task/1/image",
            files={"image": ("image.jpg", fake_image, "image/jpeg")},
            headers=auth_headers,
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_image_to_task_without_login(self):
        fake_image = fake.image()

        res = self.client.put(
            "/task/1/image",
            files={"image": ("image.jpg", fake_image, "image/jpeg")},
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_image_to_task_with_other_user_task(self):
        _, auth_headers = self.create_user_and_login()
        task_id = self.create_task(auth_headers).json()["id"]

        _, auth_headers = self.create_user_and_login()
        fake_image = fake.image()
        res = self.client.put(
            f"/task/{task_id}/image",
            files={"image": ("image.jpg", fake_image, "image/jpeg")},
            headers=auth_headers,
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


if __name__ == "__main__":
    unittest.main()
