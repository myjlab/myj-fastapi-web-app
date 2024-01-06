# # * FOR DEBUGGING
# import sys
# from pathlib import Path

# sys.path.insert(0, str(Path(__file__).parent.parent))


import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from faker import Faker

from api.db import Base, get_db
from api.main import app


# MARK: - setup test db

TEST_DB_URL = "sqlite://"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# Override dependencies
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# MARK: - test cases

fake = Faker("ja_JP")


class TestTaskRouter(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.client = TestClient(app)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)

    def create_task(self, data=None):
        """Create a task and return the response"""
        if data is None:
            data = {"title": fake.sentence(nb_words=4)}
        res = self.client.post("/tasks", json=data)
        self.assertEqual(res.status_code, 200)
        return res

    def test_get_tasks_with_empty_db(self):
        res = self.client.get("/tasks")
        res_json = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res_json), 0)

    def test_get_tasks(self):
        """
        Test if the tasks are created and returned correctly,
        but no matter the order
        """
        # Create many tasks
        insert_list = []
        for _ in range(39):
            res = self.create_task()
            insert_list.append(res.json())

        # Get the task
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertEqual(
            set([task["title"] for task in res_json]),
            set([task["title"] for task in insert_list]),
        )

    def test_get_task(self):
        # Create a task
        created_task = self.create_task()
        created_task_json = created_task.json()
        task_id = created_task_json["id"]

        # Get the task
        res = self.client.get(f"/tasks/{task_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {**created_task_json, "done": False})

    def test_create_task(self):
        test_data = [
            # task with title only
            ({"title": fake.sentence(nb_words=4)}, 200),
            # task with title and due_date
            (
                {
                    "title": fake.sentence(nb_words=4),
                    "due_date": str(fake.date_between("-3d", "+1M")),
                },
                200,
            ),
            # task with invalid due_date
            (
                {
                    "title": fake.sentence(nb_words=4),
                    "due_date": "invalid date",
                },
                422,
            ),
        ]

        for i, (data, expected_status_code) in enumerate(test_data):
            with self.subTest(i=i):
                res = self.client.post("/tasks", json=data)
                self.assertEqual(res.status_code, expected_status_code)
                if expected_status_code == 200:
                    res_json = res.json()
                    # has id
                    self.assertIn("id", res_json)
                    self.assertEqual(res_json["title"], data["title"])
                    if "due_date" not in data:
                        continue
                    self.assertEqual(res_json["due_date"], data["due_date"])

    def test_update_task(self):
        # Create a task
        created_task = self.create_task()
        task_id = created_task.json()["id"]

        # Update the task
        update_data = {"title": fake.sentence(nb_words=4)}
        res = self.client.put(f"/tasks/{task_id}", json=update_data)
        self.assertEqual(res.status_code, 200)
        updated_task = res.json()

        # Check if the task is updated
        self.assertEqual(updated_task["title"], update_data["title"])

    def test_update_non_existent_task(self):
        update_data = {"title": fake.sentence(nb_words=4)}
        res = self.client.put("/tasks/1", json=update_data)
        self.assertEqual(res.status_code, 404)

    def test_delete_task(self):
        # Create a task
        created_task = self.create_task()
        task_id = created_task.json()["id"]

        # Check if the task is created
        res = self.client.get(f"/tasks/{task_id}")
        self.assertEqual(res.status_code, 200)

        # Delete the task
        res = self.client.delete(f"/tasks/{task_id}")
        self.assertEqual(res.status_code, 200)

        # Check if the task is deleted
        res = self.client.get(f"/tasks/{task_id}")
        self.assertEqual(res.status_code, 404)

    def test_delete_non_existent_task(self):
        # Delete a non-existent task
        non_existent_task_id = 9999
        res = self.client.delete(f"/tasks/{non_existent_task_id}")
        self.assertEqual(res.status_code, 404)

    def test_done_flag(self):
        # Create a task
        created_task = self.create_task()
        task_id = created_task.json()["id"]

        # 完了フラグを立てる
        res = self.client.put(f"/tasks/{task_id}/done")
        self.assertEqual(res.status_code, 200)

        # 既に完了フラグが立っているので400を返却
        res = self.client.put(f"/tasks/{task_id}/done")
        self.assertEqual(res.status_code, 400)

        # 完了フラグを外す
        res = self.client.delete(f"/tasks/{task_id}/done")
        self.assertEqual(res.status_code, 200)

        # 既に完了フラグが外れているので404を返却
        res = self.client.delete(f"/tasks/{task_id}/done")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
