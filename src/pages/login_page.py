from playwright.sync_api import Page

from src.config import BASE_URL


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> None:
        self.page.goto(BASE_URL)

    def login(self, username: str, password: str) -> None:
        self.page.get_by_placeholder("Username").fill(username)
        self.page.get_by_placeholder("Password").fill(password)
        self.page.get_by_role("button", name="Login").click()

    def error_message(self) -> str:
        return self.page.locator("[data-test='error']").inner_text()

    def is_visible(self) -> bool:
        return self.page.get_by_placeholder("Username").is_visible()