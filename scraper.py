import logging
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://courses.calhoun.io"


def fetch_html(session: requests.Session, url: str) -> BeautifulSoup:
    """Fetches and parses HTML from a URL.

    Args:
        session: The session object to maintain authentication.
        url: The URL to fetch.

    Returns:
        BeautifulSoup object containing the parsed HTML.

    Raises:
        ConnectionError: If the page fails to load.
    """
    logger.info("[*] Fetching HTML from %s", url)

    response = session.get(url)
    if response.status_code != 200:
        logger.error("[!] Failed to fetch %s", url)
        raise ConnectionError(f"Failed to load {url}")

    return BeautifulSoup(response.text, "html.parser")


def extract_section_name(tag) -> str:
    """Extracts and formats a section name from an <h3> tag.

    Args:
        tag: BeautifulSoup tag containing the section name.

    Returns:
        The formatted section name.
    """
    return tag.text.strip().replace("/", "_").replace(" ", "_")


def extract_lesson_details(tag) -> Tuple[str, str]:
    """Extracts lesson title and URL from an <a> tag.

    Args:
        tag: BeautifulSoup tag containing the lesson link.

    Returns:
        A tuple of (lesson title, lesson URL).
    """
    lesson_title = tag.text.strip().replace("/", "_").replace(" ", "_")
    lesson_url = f"{BASE_URL}{tag['href']}"
    return lesson_title, lesson_url


def extract_sections_and_lessons(
    soup: BeautifulSoup,
) -> Dict[str, List[Tuple[str, str]]]:
    """Extracts section names and corresponding lesson links from the HTML, ignoring the first <h3>.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing course page HTML.

    Returns:
        Dict[str, List[Tuple[str, str]]]: A dictionary where section names are keys
        and values are lists of (lesson name, lesson URL) tuples.

    Raises:
        ValueError: If no lessons are found.
    """
    sections: Dict[str, List[Tuple[str, str]]] = {}
    current_section = "Uncategorized"
    first_h3_skipped = False  # Track if the first <h3> has been skipped

    for tag in soup.find_all(["h3", "a"]):
        if tag.name == "h3":
            if not first_h3_skipped:
                first_h3_skipped = True  # Ignore the first <h3> (page heading)
                continue  # Skip this iteration

            current_section = tag.text.strip().replace("/", "_").replace(" ", "_")
            logger.info("[+] Found section: %s", current_section)
            sections[current_section] = []

        elif tag.name == "a" and "/lessons/" in tag["href"]:
            lesson_title, lesson_url = extract_lesson_details(tag)
            sections[current_section].append((lesson_title, lesson_url))

    if not sections:
        logger.error("[!] No sections or lessons found.")
        raise ValueError("No lessons available for download.")

    return sections


def get_sections_and_lesson_urls(
    session: requests.Session, course_url: str
) -> Tuple[Dict[str, List[Tuple[str, str]]], int]:
    """Fetches course page HTML and extracts structured lesson data.

    Args:
        session: The session object to maintain authentication.
        course_url: The course page URL.

    Returns:
        A dictionary with section names as keys and a list of (lesson name, URL) tuples as values.
        The total number of videos found.
    """
    soup = fetch_html(session, course_url)
    sections = extract_sections_and_lessons(soup)
    total_lessons = sum(len(v) for v in sections.values())

    logger.info("[*] Extracted Sections: %d, Lessons: %d", len(sections), total_lessons)
    return sections, total_lessons


def find_mp4_link(soup: BeautifulSoup, course_prefix: str) -> str:
    """Finds the MP4 download link in a lesson page based on the course prefix.

    Args:
        soup: Parsed HTML content of the lesson page.
        course_prefix: The course-specific prefix used to identify MP4 file links.

    Returns:
        The direct MP4 URL if found, otherwise an empty string.
    """
    for a_tag in soup.find_all("a", href=True):
        if f"files/{course_prefix}" in a_tag["href"]:
            return f"{BASE_URL}{a_tag['href']}"
    return ""


def get_mp4_url(session: requests.Session, lesson_url: str, course_prefix: str) -> str:
    """Extracts the direct MP4 download link from a lesson page.

    Args:
        session: The session object for authentication.
        lesson_url: The URL of the lesson page.
        course_prefix: The course-specific prefix used to identify MP4 file links.

    Returns:
        The direct MP4 URL if found, otherwise an empty string.
    """
    soup = fetch_html(session, lesson_url)
    return find_mp4_link(soup, course_prefix)
