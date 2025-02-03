import logging
from typing import Dict, List, Tuple
import requests
from bs4 import BeautifulSoup
from config import COURSE_CONFIG

logger = logging.getLogger(__name__)

BASE_URL = "https://courses.calhoun.io"


def fetch_html(session: requests.Session, url: str) -> BeautifulSoup:
    """Fetches and parses HTML from a URL.

    Args:
        session: The session object to maintain authentication.
        url: The URL to fetch.

    Returns:
        Parsed HTML content.

    Raises:
        ConnectionError: If the page fails to load.
    """
    logger.info("[*] Fetching HTML from %s", url)

    response = session.get(url)
    if response.status_code != 200:
        logger.error("[!] Failed to fetch %s", url)
        raise ConnectionError(f"Failed to load {url}")

    return BeautifulSoup(response.text, "html.parser")


def extract_section_name(section_div) -> str:
    """Extracts and formats a section name from an <h3> inside a section <div>.

    Args:
        section_div: BeautifulSoup tag representing the section.

    Returns:
        The formatted section name.
    """
    h3_tag = section_div.find("h3")  # Extract <h3> inside this section div
    if h3_tag:
        return h3_tag.text.strip().replace("/", "_").replace(" ", "_")
    return "Uncategorized"  # Fallback in case no <h3> is found


def extract_lesson_details(lesson_link) -> Tuple[str, str]:
    """Extracts lesson title and URL from a lesson link.

    Args:
        lesson_link: BeautifulSoup tag containing the lesson link.

    Returns:
        A tuple of (lesson title, lesson URL).
    """
    lesson_title = lesson_link.text.strip().replace("/", "_").replace(" ", "_")
    lesson_url = f"{BASE_URL}{lesson_link['href']}"
    return lesson_title, lesson_url


def extract_sections_and_lessons(soup: BeautifulSoup, course_prefix: str) -> Dict[str, List[Tuple[str, str]]]:
    """Extracts section names and corresponding lesson links from the HTML using div IDs.

    Args:
        soup: The BeautifulSoup object containing course page HTML.
        course_prefix: The course-specific section prefix to identify sections.

    Returns:
        A dictionary where section names are keys and values are lists
        of (lesson name, lesson URL) tuples.

    Raises:
        ValueError: If no lessons are found.
    """
    sections: Dict[str, List[Tuple[str, str]]] = {}
    section_divs = soup.find_all("div", id=lambda x: x and x.startswith(course_prefix))

    for section_div in section_divs[1:]:  # Skip the first section div
        section_name = extract_section_name(section_div)  # Extract the title from <h3>
        logger.info("[+] Found section: %s", section_name)

        sections[section_name] = []
        for lesson_link in section_div.find_all("a", href=True):
            if "/lessons/" in lesson_link["href"]:
                lesson_title, lesson_url = extract_lesson_details(lesson_link)
                sections[section_name].append((lesson_title, lesson_url))

    if not sections:
        logger.error("[!] No sections or lessons found.")
        raise ValueError("No lessons available for download.")

    return sections


def get_sections_and_lesson_urls(session: requests.Session, course_name: str) -> Tuple[Dict[str, List[Tuple[str, str]]], int]:
    """Fetches course page HTML and extracts structured lesson data.

    Args:
        session: The session object to maintain authentication.
        course_name: The course name to determine the correct section prefix.

    Returns:
        A dictionary with section names as keys and a list of (lesson name, URL) tuples as values,
        and the total number of videos found.
    """
    course_info = COURSE_CONFIG.get(course_name)
    if not course_info:
        logger.error("[!] Invalid course name: %s", course_name)
        raise ValueError(f"Course '{course_name}' not found in configuration.")

    soup = fetch_html(session, course_info["url"])
    sections = extract_sections_and_lessons(soup, course_info["div_prefix"])

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
