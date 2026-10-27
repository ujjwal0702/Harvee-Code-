from decimal import Decimal

from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def fill_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.page.get_by_placeholder("First Name").fill(first_name)
        self.page.get_by_placeholder("Last Name").fill(last_name)
        self.page.get_by_placeholder("Zip/Postal Code").fill(postal_code)

    def continue_checkout(self) -> None:
        self.page.get_by_role("button", name="Continue").click()

    def error_message(self) -> str:
        return self.page.locator("[data-test='error']").inner_text()

    def _summary_amount(self, label: str) -> Decimal:
        text = self.page.locator(label).inner_text()
        return Decimal(text.split("$")[-1])

    def item_total(self) -> Decimal:
        return self._summary_amount(".summary_subtotal_label")

    def tax(self) -> Decimal:
        return self._summary_amount(".summary_tax_label")

    def total(self) -> Decimal:
        return self._summary_amount(".summary_total_label")

    def finish(self) -> None:
        self.page.get_by_role("button", name="Finish").click()

    def cancel(self) -> None:
        self.page.get_by_role("button", name="Cancel").click()

    def confirmation_message(self) -> str:
        return self.page.locator(".complete-header").inner_text()