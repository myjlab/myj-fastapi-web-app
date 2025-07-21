import unittest
from playwright.sync_api import sync_playwright
import time
import random
from faker import Faker


class FrontendInteractionTest(unittest.TestCase):
    """フロントエンド操作テスト - バックエンドサービスがlocalhost:8000で動作が必要"""

    @classmethod
    def setUpClass(cls):
        """テストクラス初期化"""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=False
        )  # Falseに設定するとブラウザ操作が見えます
        cls.fake = Faker("ja_JP")

        # テスト用のベースURL
        cls.frontend_url = "http://localhost:3000"
        cls.backend_url = "http://localhost:8000"

    @classmethod
    def tearDownClass(cls):
        """テストクラス終了処理"""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """各テストメソッド実行前の初期化"""
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        # ダイアログハンドラーを設定
        self.page.on("dialog", lambda dialog: dialog.accept())

        # ランダムなテスト用ユーザーデータを生成
        self.test_user = {
            "email": f"test_{random.randint(1000, 9999)}@example.com",
            "nickname": self.fake.name(),
            "password": "testpassword123",
        }

    def tearDown(self):
        """各テストメソッド実行後のクリーンアップ"""
        self.context.close()

    def test_user_signup_and_login_flow(self):
        """ユーザー登録とログインフローのテスト"""
        # 新規登録ページにアクセス
        self.page.goto(f"{self.frontend_url}/signup.html")
        self.page.wait_for_load_state("networkidle")

        # 新規登録フォームを入力
        self.page.fill("#nickname", self.test_user["nickname"])
        self.page.fill("#email", self.test_user["email"])
        self.page.fill("#password", self.test_user["password"])

        # 新規登録ボタンをクリック
        self.page.click("button:has-text('新規登録')")

        # 登録成功メッセージを待機
        self.page.wait_for_selector("#megs:has-text('新規登録に成功しました')")

        # ログインページリンクをクリック
        self.page.click("a[href='/login.html']")
        self.page.wait_for_load_state("networkidle")

        # ログインフォームを入力
        self.page.fill("#email", self.test_user["email"])
        self.page.fill("#password", self.test_user["password"])

        # ログインボタンをクリック
        self.page.click("button:has-text('ログイン')")

        # トップページへの遷移とウェルカムメッセージの表示を確認
        self.page.wait_for_url(f"{self.frontend_url}/index.html")
        welcome_text = self.page.text_content("#welcome")
        self.assertIn(self.test_user["nickname"], welcome_text)

    def test_task_creation_flow(self):
        """タスク作成フローのテスト"""
        # 事前にログイン
        self._login_user()

        # タスク作成ページにアクセス
        self.page.click("a[href='/task-create.html']")
        self.page.wait_for_load_state("networkidle")

        # タスク情報を入力
        task_title = f"テストタスク_{random.randint(100, 999)}"
        self.page.fill("#title", task_title)
        self.page.fill("#due-date", "2024-12-31")

        # 作成ボタンをクリック
        self.page.click("button:has-text('作成')")

        # トップページへの遷移を確認
        self.page.wait_for_url(f"{self.frontend_url}/index.html")
        time.sleep(2)  # ページ読み込みを待機

        # タスクがページに表示されていることを確認
        page_content = self.page.content()
        self.assertIn(
            task_title, page_content, f"Task '{task_title}' not found in page"
        )

    def test_task_detail_and_edit_flow(self):
        """タスク詳細表示と編集フローのテスト"""
        # 事前にログインしてタスクを作成
        self._login_user()
        task_title = self._create_test_task()

        # タスクリンクをクリックして詳細ページへ
        self.page.click(
            f"a:has-text('{task_title}')",
            position={"x": 10, "y": 0},
        )
        self.page.wait_for_load_state("networkidle")

        # タスク詳細の表示を確認
        self.assertIn(task_title, self.page.text_content("#task-detail"))

        # 編集ボタンをクリック
        self.page.click("button:has-text('編集')")
        self.page.wait_for_load_state("networkidle")

        # タスクタイトルを変更
        updated_title = f"{task_title}_更新済み"
        self.page.fill("#title", updated_title)

        # 更新ボタンをクリック
        self.page.click("button:has-text('更新')")

        # トップページに戻って更新確認
        self.page.goto(f"{self.frontend_url}/index.html")
        self.page.wait_for_load_state("networkidle")

        # 更新されたタスクタイトルを確認
        updated_task_found = False
        task_links = self.page.query_selector_all(
            "a[href*='/task-detail.html']"
        )
        for link in task_links:
            if updated_title in link.text_content():
                updated_task_found = True
                break
        self.assertTrue(
            updated_task_found, f"Updated task '{updated_title}' not found"
        )

    def test_task_completion_toggle(self):
        """タスク完了状態切り替えのテスト"""
        # 事前にログインしてタスクを作成
        self._login_user()
        self._create_test_task()

        # タスクのチェックボックスを見つける
        task_checkbox = self.page.query_selector(
            "input[type='checkbox'][id*='task-done-checkbox']"
        )
        self.assertIsNotNone(task_checkbox, "Task checkbox not found")

        # チェックボックスをクリックして完了状態に変更
        initial_checked = task_checkbox.is_checked()
        task_checkbox.click()
        time.sleep(1)  # API呼び出し完了を待機

        # 状態が変更されたことを確認
        self.assertNotEqual(initial_checked, task_checkbox.is_checked())

        # もう一度クリックして元の状態に戻す
        task_checkbox.click()
        time.sleep(1)

        # 初期状態に戻ったことを確認
        self.assertEqual(initial_checked, task_checkbox.is_checked())

    def test_task_deletion_flow(self):
        """タスク削除フローのテスト"""
        # 事前にログインしてタスクを作成
        self._login_user()
        task_title = self._create_test_task()

        # タスク詳細ページへ移動
        self.page.click(
            f"a:has-text('{task_title}')",
            position={"x": 10, "y": 0},
        )
        self.page.wait_for_load_state("networkidle")

        # 削除ボタンをクリック
        self.page.click("button:has-text('削除')")

        # トップページへの遷移を待機
        self.page.wait_for_url(f"{self.frontend_url}/index.html")

        # タスクがリストから消えていることを確認
        task_links = self.page.query_selector_all(
            "a[href*='/task-detail.html']"
        )
        task_found = False
        for link in task_links:
            if task_title in link.text_content():
                task_found = True
                break
        self.assertFalse(
            task_found, f"Deleted task '{task_title}' still exists in list"
        )

    def test_logout_flow(self):
        """ログアウトフローのテスト"""
        # 事前にログイン
        self._login_user()

        # ログアウトボタンをクリック
        self.page.click("button:has-text('ログアウト')")

        # ログインページへの遷移を確認
        self.page.wait_for_url(f"{self.frontend_url}/login.html")

        # 直接トップページにアクセスしようとするとログインページにリダイレクトされることを確認
        self.page.goto(f"{self.frontend_url}/index.html")
        self.page.wait_for_url(f"{self.frontend_url}/login.html")

    def _login_user(self):
        """ヘルパーメソッド: ユーザーログイン"""
        # まずユーザー登録
        self.page.goto(f"{self.frontend_url}/signup.html")
        self.page.wait_for_load_state("networkidle")

        self.page.fill("#nickname", self.test_user["nickname"])
        self.page.fill("#email", self.test_user["email"])
        self.page.fill("#password", self.test_user["password"])
        self.page.click("button:has-text('新規登録')")

        # 登録成功を待機
        self.page.wait_for_selector("#megs:has-text('新規登録に成功しました')")

        # ログイン
        self.page.goto(f"{self.frontend_url}/login.html")
        self.page.wait_for_load_state("networkidle")

        self.page.fill("#email", self.test_user["email"])
        self.page.fill("#password", self.test_user["password"])
        self.page.click("button:has-text('ログイン')")

        # トップページへの遷移を待機
        self.page.wait_for_url(f"{self.frontend_url}/index.html")

    def _create_test_task(self):
        """ヘルパーメソッド: テスト用タスクを作成"""
        task_title = f"テストタスク_{random.randint(100, 999)}"

        self.page.click("a[href='/task-create.html']")
        self.page.wait_for_load_state("networkidle")

        self.page.fill("#title", task_title)
        self.page.fill("#due-date", "2024-12-31")
        self.page.click("button:has-text('作成')")

        # トップページへの遷移を待機
        self.page.wait_for_url(f"{self.frontend_url}/index.html")

        return task_title


if __name__ == "__main__":
    # テスト実行時に詳細情報を表示
    unittest.main(verbosity=2)
