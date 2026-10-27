from decimal import Decimal

from playwright.sync_api import Page


class InventoryPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def is_visible(self) -> bool:
        return len(self.product_names()) > 0

    def sort_by(self, option: str) -> None:
        self.page.locator("[data-test='product-sort-container']").select_option(option)

    def product_names(self) -> list[str]:
        return self.page.locator(".inventory_item_name").all_text_contents()

    def prices(self) -> list[Decimal]:
        labels = self.page.locator(".inventory_item_price").all_text_contents()
        return [Decimal(label.replace("$", "")) for label in labels]

    def add_product(self, name: str) -> None:
        product = self.page.locator(".inventory_item").filter(has_text=name)
        product.get_by_role("button", name="Add to cart").click()

    def remove_product(self, name: str) -> None:
        product = self.page.locator(".inventory_item").filter(has_text=name)
        product.get_by_role("button", name="Remove").click()

    def cart_badge_count(self) -> int:
        badge = self.page.locator(".shopping_cart_badge")
        return int(badge.inner_text()) if badge.count() else 0

    def open_cart(self) -> None:
        self.page.locator(".shopping_cart_link").click()

    def logout(self) -> None:
        self.page.locator("#react-burger-menu-btn").click()
        self.page.locator("#logout_sidebar_link").click()