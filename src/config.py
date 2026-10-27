import os
from urllib.parse import urljoin


BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
STANDARD_USER = os.getenv("STANDARD_USER", "standard_user")
LOCKED_OUT_USER = os.getenv("LOCKED_OUT_USER", "locked_out_user")
PROBLEM_USER = os.getenv("PROBLEM_USER", "problem_user")
PERFORMANCE_GLITCH_USER = os.getenv("PERFORMANCE_GLITCH_USER", "performance_glitch_user")
ERROR_USER = os.getenv("ERROR_USER", "error_user")
VISUAL_USER = os.getenv("VISUAL_USER", "visual_user")
SAUCE_PASSWORD = os.getenv("SAUCE_PASSWORD", "secret_sauce")


def page_url(path: str) -> str:
	return urljoin(f"{BASE_URL.rstrip('/')}/", path.lstrip("/"))