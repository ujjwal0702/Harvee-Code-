import re
from html import escape
from pathlib import Path

import pytest


_test_reports = []

_CASE_TITLES = {
    "TC01": "Standard customer signs in and sees the product catalogue",
    "TC02": "Locked-out customer is denied access",
    "TC04": "Products are ordered from lowest to highest price",
    "TC05": "Products are ordered from highest to lowest price",
    "TC06": "Product names are ordered A to Z",
    "TC07": "Product names are ordered Z to A",
    "TC08": "Two products are added and one is removed from the cart",
    "TC10": "Product is removed from the catalogue and cart count updates",
    "TC11": "Checkout total is correct and the completed cart is empty",
    "TC12": "Checkout rejects a missing first name",
    "TC13": "Checkout rejects a missing last name",
    "TC14": "Checkout rejects a missing postal code",
    "TC15": "Checkout is cancelled without placing an order",
    "TC20": "A logged-out customer cannot reopen the catalogue by URL",
    "TC23": "Problem-profile customer can sign in and view products",
    "TC24": "Performance-profile customer reaches products within 20 seconds",
    "TC25": "Error-profile customer can sign in and view products",
    "TC26": "Visual-profile customer can sign in and view products",
}


def pytest_configure(config):
    Path("reports").mkdir(exist_ok=True)


def pytest_html_report_title(report):
    report.title = "Sauce Demo | Checkout Quality Report"


def pytest_metadata(metadata):
    metadata["Project"] = "Sauce Demo practice store"
    metadata["Suite"] = "Shop and checkout"
    metadata["Automation"] = "Python + Playwright"
    metadata["Target"] = "Public practice site only"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" or (report.when == "setup" and (report.failed or report.skipped)):
        _test_reports.append(report)


def pytest_html_results_summary(prefix, summary, postfix):
    total = len(_test_reports)
    failed = sum(report.failed for report in _test_reports)
    skipped = sum(report.skipped for report in _test_reports)
    passed = max(total - failed - skipped, 0)
    duration = sum(report.duration for report in _test_reports)
    outcome = "Review required" if failed else "All checks passed"
    status_class = "needs-attention" if failed else "all-clear"
    result_by_case = _results_by_case()

    prefix.append(
        f'<section class="run-overview {status_class}" aria-label="Run overview">'
        '<div class="overview-heading">'
        '<div><p class="eyebrow">QUALITY RUN OVERVIEW</p>'
        '<h2>Shop and checkout</h2>'
        f'<p class="overview-status">{outcome}</p></div>'
        '<div class="overview-actions">'
        '<button id="environment-toggle" type="button" aria-expanded="false" '
        'aria-controls="environment" '
        'onclick="const open=document.body.classList.toggle(\'show-environment\');'
        'this.setAttribute(\'aria-expanded\',open);'
        'this.querySelector(\'.toggle-label\').textContent=open?\'Hide environment\':\'Show environment\';">'
        '<span class="toggle-label">Show environment</span><span class="toggle-mark" aria-hidden="true">+</span>'
        '</button>'
        f'<div class="run-total"><strong>{total}</strong><span>tests executed</span></div>'
        '</div>'
        '</div><div class="metric-grid">'
        f'<div class="run-metric metric-passed"><span>Passed</span><strong>{passed}</strong></div>'
        f'<div class="run-metric metric-failed"><span>Failed</span><strong>{failed}</strong></div>'
        f'<div class="run-metric metric-skipped"><span>Skipped</span><strong>{skipped}</strong></div>'
        f'<div class="run-metric metric-duration"><span>Execution time</span><strong>{duration:.1f}s</strong></div>'
        '</div></section>'
    )

    summary.append(_manual_case_table(result_by_case))
    postfix.append(
        '<section class="execution-heading"><h2>Automated execution details</h2>'
        '<p>Expand a result row to review captured logs, screenshots, and failure evidence.</p></section>'
    )


def _case_id_from_node_id(node_id):
    parameter_case = re.search(r"\[(?:[^\]-]+-)?(TC\d{2})_", node_id)
    if parameter_case:
        return parameter_case.group(1)
    test_case = re.search(r"test_(TC\d{2})_", node_id)
    return test_case.group(1) if test_case else None


def _results_by_case():
    result_by_case = {}
    for report in _test_reports:
        case_id = _case_id_from_node_id(getattr(report, "nodeid", ""))
        if case_id is None:
            continue
        if report.failed:
            result = "Failed"
        elif report.skipped:
            result = "Skipped"
        else:
            result = "Passed"
        result_by_case.setdefault(case_id, []).append(result)

    if "TC08" in result_by_case:
        result_by_case.setdefault("TC09", result_by_case["TC08"])
    return result_by_case


def _manual_case_table(result_by_case):
    answers_path = Path(__file__).resolve().parents[1] / "ANSWERS.md"
    headers = [
        "ID",
        "Area",
        "Type",
        "Title",
        "Pre-conditions",
        "Steps",
        "Test data",
        "Expected result",
        "Priority",
        "Automate? and why",
    ]
    table_rows = []
    reading_cases = False
    for line in answers_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ID | Area | Type | Title |"):
            reading_cases = True
            continue
        if not reading_cases:
            continue
        if line.startswith("|---"):
            continue
        if not line.startswith("| TC"):
            break

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        case_id = cells[0]
        case_results = result_by_case.get(case_id, [])
        if any(result == "Failed" for result in case_results):
            run_result = "Failed"
        elif case_results and all(result == "Passed" for result in case_results):
            run_result = "Passed"
        elif case_results and any(result == "Skipped" for result in case_results):
            run_result = "Skipped"
        elif cells[9].startswith("Yes"):
            run_result = "Not run"
        else:
            run_result = "Manual only"

        row_cells = "".join(f"<td>{escape(cell)}</td>" for cell in cells)
        result_class = run_result.lower().replace(" ", "-")
        row_cells += f'<td><span class="suite-result {result_class}">{escape(run_result)}</span></td>'
        table_rows.append(f'<tr class="suite-row">{row_cells}</tr>')

    heading_cells = "".join(f"<th scope=\"col\">{escape(header)}</th>" for header in headers)
    return (
        '<section class="manual-suite" aria-labelledby="manual-suite-title">'
        '<div class="suite-heading"><div><p class="eyebrow">TEST CASE REGISTER</p>'
        '<h2 id="manual-suite-title">Manual suite and run status</h2></div>'
        '<p>Cases marked “Manual only” are not part of this automated run.</p></div>'
        '<div class="manual-case-table-wrap"><table class="manual-case-table">'
        f'<thead><tr>{heading_cells}<th scope="col">Run result</th></tr></thead>'
        f'<tbody>{"".join(table_rows)}</tbody>'
        '</table></div></section>'
    )


def pytest_html_results_table_header(cells):
    cells[0] = '<th class="sortable" data-column-type="result">Status</th>'
    cells[1] = '<th class="sortable" data-column-type="testId">Automated check</th>'
    cells[2] = '<th class="sortable" data-column-type="duration">Duration</th>'
    cells[3] = "<th>Evidence</th>"


def pytest_html_results_table_row(report, cells):
    node_id = getattr(report, "nodeid", "")
    case_id = re.search(r"\[(?:[^\]-]+-)?(TC\d{2})_", node_id)
    if case_id:
        manual_id = case_id.group(1)
    else:
        test_name = node_id.rsplit("::", 1)[-1]
        match = re.search(r"(TC\d{2})_", test_name)
        manual_id = match.group(1) if match else ""

    title = _CASE_TITLES.get(manual_id, "Automated test result")
    browser_match = re.search(r"\[(chromium|firefox|webkit)(?:-|\])", node_id)
    browser_label = browser_match.group(1).capitalize() if browser_match else "Configured browser"
    label = (
        f'<td class="col-testId"><span class="case-id">{escape(manual_id)}</span>'
        '<span class="case-content">'
        f'<span class="case-title">{escape(title)}</span>'
        f'<span class="case-meta">{escape(browser_label)} browser</span>'
        '</span></td>'
    )
    cells[1] = label