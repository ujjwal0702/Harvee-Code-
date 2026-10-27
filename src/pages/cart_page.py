from playwright.sync_api import Page


class CartPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def product_names(self) -> list[str]:
        return self.page.locator(".cart_item .inventory_item_name").all_text_contents()

    def remove_product(self, name: str) -> None:
        item = self.page.locator(".cart_item").filter(has_text=name)
        item.get_by_role("button", name="Remove").click()

    def badge_count(self) -> int:
        badge = self.page.locator(".shopping_cart_badge")
        return int(badge.inner_text()) if badge.count() else 0

    def open_cart(self) -> None:
        self.page.locator(".shopping_cart_link").click()

    def checkout(self) -> None:
        self.page.get_by_role("button", name="Checkout").click()