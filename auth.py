import logging

import requests

logger = logging.getLogger(__name__)

LOGIN_URL = "https://courses.calhoun.io/signin"


def login(session: requests.Session, email: str, password: str) -> None:
    """Logs into the course website.

    Args:
        session: The session object to maintain authentication.
        email: The user's email.
        password: The user's password.

    Raises:
        ValueError: If login fails due to invalid credentials.
    """
    logger.info("[*] Attempting login...")

    payload = {"email": email, "password": password}
    response = session.post(LOGIN_URL, data=payload)

    if response.status_code != 200:
        logger.error("[!] Login failed. Please check credentials.")
        raise ValueError("Login failed. Invalid credentials.")

    logger.info("[+] Login successful!")
