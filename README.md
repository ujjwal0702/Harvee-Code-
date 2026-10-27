# Sauce Demo QA Automation Assessment

This submission uses **Python and Playwright**. It targets only the public Sauce Demo practice store. It does not use Selenium; the assessment asks for one UI automation framework, and Playwright is the selected framework.

## Setup and run

Requires Python 3.10 or later.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
playwright install chromium
pytest
```

By default, the suite uses Sauce Demo's published practice credentials. Override configuration with environment variables when needed: `BASE_URL`, `STANDARD_USER`, `LOCKED_OUT_USER`, `PROBLEM_USER`, `PERFORMANCE_GLITCH_USER`, `ERROR_USER`, `VISUAL_USER`, and `SAUCE_PASSWORD`. The `.env.example` file documents the names; pytest does not load a `.env` file automatically.

Pytest runs Chromium, saves screenshots for failed tests under `test-results/`, and writes a styled, self-contained HTML report to `reports/report.html` plus a JUnit XML report to `reports/junit.xml`. The HTML report opens with run metrics, then shows the manual case register from `ANSWERS.md` with automated run status; use **Show environment** in the top-right of the summary to reveal runtime details. Expand rows in **Automated execution details** for INFO logs and failure evidence. Run `pytest -k TC04` to select a case, or `pytest --browser firefox` after installing the Firefox browser with `playwright install firefox`.

## Manual-to-automated traceability

| Manual case | Automated test |
|---|---|
| TC01 | `test_TC01_standard_user_can_log_in` |
| TC02 | `test_TC02_locked_out_user_sees_login_error` |
| TC03 | Manual only: invalid password and error behavior |
| TC04 | `test_TC04_sort_price_low_to_high_orders_entire_list` |
| TC05 | `test_TC05_sort_price_high_to_low_orders_entire_list` |
| TC06 | `test_TC06_sort_name_a_to_z_orders_entire_list` |
| TC07 | `test_TC07_sort_name_z_to_a_orders_entire_list` |
| TC08 | `test_TC08_add_two_products_and_remove_one_from_cart` |
| TC09 | `test_TC08_add_two_products_and_remove_one_from_cart` |
| TC10 | `test_TC10_remove_product_from_products_page_updates_badge` |
| TC11 | `test_TC11_checkout_calculates_total_and_clears_cart` |
| TC12 | `test_TC12_checkout_requires_all_customer_fields[TC12_missing_first_name]` |
| TC13 | `test_TC12_checkout_requires_all_customer_fields[TC13_missing_last_name]` |
| TC14 | `test_TC12_checkout_requires_all_customer_fields[TC14_missing_postal_code]` |
| TC15 | `test_TC15_cancel_checkout_returns_to_cart_without_order` |
| TC16 | Manual only: empty cart checkout behavior |
| TC17 | Manual only: keyboard-only navigation and focus visibility |
| TC18 | Manual only: responsive layout and browser coverage |
| TC19 | Manual only: screen-reader names and status announcements |
| TC20 | `test_TC20_inventory_url_after_logout_returns_to_login` |
| TC21 | Manual only: 15-minute exploratory charter for a known-problem user |
| TC22 | Manual only: session and cart isolation across users |
| TC23 | `test_TC23_problem_user_can_log_in_and_open_catalogue` |
| TC24 | `test_TC24_performance_glitch_user_can_log_in_and_open_catalogue` |
| TC25 | `test_TC25_error_user_can_log_in_and_open_catalogue` |
| TC26 | `test_TC26_visual_user_can_log_in_and_open_catalogue` |

## Growing the suite to 200 tests

Keep the page objects focused on reusable user actions, then add data-driven tests for product and checkout variations rather than duplicating flows. Group tests by feature and risk, assign stable case IDs, and keep each test independent with a fresh browser context. Add API or unit coverage where the client exposes those layers, and reserve UI tests for critical end-to-end paths. Use markers to separate smoke, regression, and cross-browser runs; shard the slower regression suite in CI, publish JUnit and failure artifacts, and quarantine flaky tests only with an owner and expiry date. Review runtime and failure trends regularly so 200 tests remain diagnosable rather than becoming a slower, noisier gate.