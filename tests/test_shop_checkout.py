import logging
import re
from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

from src.config import (
    ERROR_USER,
    LOCKED_OUT_USER,
    PERFORMANCE_GLITCH_USER,
    PROBLEM_USER,
    SAUCE_PASSWORD,
    STANDARD_USER,
    VISUAL_USER,
    page_url,
)
from src.pages import CartPage, CheckoutPage, InventoryPage, LoginPage

logger = logging.getLogger(__name__)


def login_as_user(page: Page, username: str, timeout_ms: int = 5000) -> InventoryPage:
    login = LoginPage(page)
    logger.info("Opening login page for user %s", username)
    login.open()
    login.login(username, SAUCE_PASSWORD)
    inventory = InventoryPage(page)
    expect(page).to_have_url(re.compile(r".*/inventory\.html$"), timeout=timeout_ms)
    logger.info("Login succeeded for %s; inventory page loaded", username)
    return inventory


def login_as_standard_user(page: Page) -> InventoryPage:
    return login_as_user(page, STANDARD_USER)


def test_TC01_standard_user_can_log_in(page: Page) -> None:
    inventory = login_as_standard_user(page)

    assert inventory.is_visible()
    logger.info("Product catalogue is visible")


def test_TC02_locked_out_user_sees_login_error(page: Page) -> None:
    login = LoginPage(page)
    login.open()
    login.login(LOCKED_OUT_USER, SAUCE_PASSWORD)

    error_message = login.error_message()
    logger.info("Locked-out login rejected with message: %s", error_message)
    assert "locked out" in error_message.lower()
    assert login.is_visible()


def assert_user_can_open_catalogue(
    page: Page, case_id: str, username: str, timeout_ms: int = 5000
) -> None:
    inventory = login_as_user(page, username, timeout_ms)
    product_names = inventory.product_names()

    assert product_names
    logger.info("%s: %s opened the catalogue with products %s", case_id, username, product_names)


def test_TC23_problem_user_can_log_in_and_open_catalogue(page: Page) -> None:
    assert_user_can_open_catalogue(page, "TC23", PROBLEM_USER)


def test_TC24_performance_glitch_user_can_log_in_and_open_catalogue(page: Page) -> None:
    assert_user_can_open_catalogue(page, "TC24", PERFORMANCE_GLITCH_USER, timeout_ms=20000)


def test_TC25_error_user_can_log_in_and_open_catalogue(page: Page) -> None:
    assert_user_can_open_catalogue(page, "TC25", ERROR_USER)


def test_TC26_visual_user_can_log_in_and_open_catalogue(page: Page) -> None:
    assert_user_can_open_catalogue(page, "TC26", VISUAL_USER)


def test_TC04_sort_price_low_to_high_orders_entire_list(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.sort_by("lohi")

    prices = inventory.prices()
    logger.info("Prices after low-to-high sort: %s", prices)
    assert len(prices) > 1
    assert prices == sorted(prices)


def test_TC05_sort_price_high_to_low_orders_entire_list(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.sort_by("hilo")

    prices = inventory.prices()
    logger.info("Prices after high-to-low sort: %s", prices)
    assert len(prices) > 1
    assert prices == sorted(prices, reverse=True)


def test_TC08_add_two_products_and_remove_one_from_cart(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.add_product("Sauce Labs Backpack")
    inventory.add_product("Sauce Labs Bike Light")
    logger.info("Added Backpack and Bike Light; cart badge: %s", inventory.cart_badge_count())
    assert inventory.cart_badge_count() == 2

    inventory.open_cart()
    cart = CartPage(page)
    logger.info("Cart contains: %s", cart.product_names())
    assert set(cart.product_names()) == {"Sauce Labs Backpack", "Sauce Labs Bike Light"}

    cart.remove_product("Sauce Labs Backpack")
    logger.info("Removed Backpack; remaining cart items: %s", cart.product_names())
    assert cart.badge_count() == 1
    assert cart.product_names() == ["Sauce Labs Bike Light"]


def test_TC10_remove_product_from_products_page_updates_badge(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.add_product("Sauce Labs Backpack")
    logger.info("Added Backpack; cart badge: %s", inventory.cart_badge_count())
    assert inventory.cart_badge_count() == 1

    inventory.remove_product("Sauce Labs Backpack")

    logger.info("Removed Backpack from inventory page; cart badge: %s", inventory.cart_badge_count())
    assert inventory.cart_badge_count() == 0


def test_TC11_checkout_calculates_total_and_clears_cart(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.add_product("Sauce Labs Backpack")
    inventory.add_product("Sauce Labs Bike Light")
    inventory.open_cart()
    CartPage(page).checkout()

    checkout = CheckoutPage(page)
    checkout.fill_information("Ada", "Lovelace", "10001")
    checkout.continue_checkout()

    logger.info(
        "Checkout amounts: items=%s tax=%s total=%s",
        checkout.item_total(),
        checkout.tax(),
        checkout.total(),
    )
    assert checkout.total() == checkout.item_total() + checkout.tax()
    checkout.finish()
    logger.info("Order confirmation: %s", checkout.confirmation_message())
    assert checkout.confirmation_message() == "Thank you for your order!"

    CartPage(page).open_cart()
    assert CartPage(page).product_names() == []
    assert CartPage(page).badge_count() == 0
    logger.info("Order completed; cart is empty")


@pytest.mark.parametrize(
    ("case_id", "first_name", "last_name", "postal_code", "expected_error"),
    [
        ("TC12_missing_first_name", "", "Lovelace", "10001", "Error: First Name is required"),
        ("TC13_missing_last_name", "Ada", "", "10001", "Error: Last Name is required"),
        ("TC14_missing_postal_code", "Ada", "Lovelace", "", "Error: Postal Code is required"),
    ],
    ids=["TC12_missing_first_name", "TC13_missing_last_name", "TC14_missing_postal_code"],
)
def test_TC12_checkout_requires_all_customer_fields(
    page: Page,
    case_id: str,
    first_name: str,
    last_name: str,
    postal_code: str,
    expected_error: str,
) -> None:
    inventory = login_as_standard_user(page)
    inventory.add_product("Sauce Labs Backpack")
    inventory.open_cart()
    CartPage(page).checkout()

    checkout = CheckoutPage(page)
    checkout.fill_information(first_name, last_name, postal_code)
    checkout.continue_checkout()

    error_message = checkout.error_message()
    logger.info("%s produced validation message: %s", case_id, error_message)
    assert error_message == expected_error
    assert "/checkout-step-one.html" in page.url


def test_TC20_inventory_url_after_logout_returns_to_login(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.logout()
    logger.info("Logged out; requesting protected inventory URL directly")
    expect(page).to_have_url(re.compile(r"https?://[^/]+/?$"))

    page.goto(page_url("inventory.html"))

    logger.info("Protected URL redirected to login page: %s", page.url)
    assert LoginPage(page).is_visible()
    assert "/inventory.html" not in page.url


def test_TC06_sort_name_a_to_z_orders_entire_list(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.sort_by("az")

    names = inventory.product_names()
    logger.info("Product names after A-to-Z sort: %s", names)
    assert len(names) > 1
    assert names == sorted(names)


def test_TC07_sort_name_z_to_a_orders_entire_list(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.sort_by("za")

    names = inventory.product_names()
    logger.info("Product names after Z-to-A sort: %s", names)
    assert len(names) > 1
    assert names == sorted(names, reverse=True)


def test_TC15_cancel_checkout_returns_to_cart_without_order(page: Page) -> None:
    inventory = login_as_standard_user(page)
    inventory.add_product("Sauce Labs Backpack")
    inventory.open_cart()
    CartPage(page).checkout()

    checkout = CheckoutPage(page)
    checkout.fill_information("Ada", "Lovelace", "10001")
    checkout.continue_checkout()
    checkout.cancel()

    logger.info("Checkout cancelled; cart badge remains %s", InventoryPage(page).cart_badge_count())
    expect(page).to_have_url(re.compile(r".*/inventory\.html$"))
    assert InventoryPage(page).cart_badge_count() == 1