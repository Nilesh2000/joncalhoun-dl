import logging
import os
from typing import Dict, List, Tuple

import requests
from tqdm import tqdm

from scraper import get_mp4_url

logger = logging.getLogger(__name__)


def ensure_directory_exists(path: str) -> None:
    """Ensures the given directory exists. If not, creates it.

    Args:
        path: The directory path to check/create.
    """
    os.makedirs(path, exist_ok=True)


def get_section_path(destination: str, section_num: int, section_name: str) -> str:
    """Generates the full directory path for a section, prefixed with section number.

    Args:
        destination: The base directory for saving videos.
        section_num: The section number (used as prefix).
        section_name: The sanitized section name.

    Returns:
        The full path of the section folder.
    """
    formatted_section = f"{section_num:02d}_{section_name}"
    section_path = os.path.join(destination, formatted_section)
    ensure_directory_exists(section_path)
    return section_path


def get_file_path(section_path: str, lesson_num: int, filename: str) -> str:
    """Generates the full file path for a video file, prefixed with lesson number.

    Args:
        section_path: The path to the section directory.
        lesson_num: The lesson number (used as prefix).
        filename: The sanitized name of the video file.

    Returns:
        The full file path including the .mp4 extension.
    """
    formatted_filename = f"{lesson_num:03d}_{filename}.mp4"
    return os.path.join(section_path, formatted_filename)


def file_already_downloaded(file_path: str) -> bool:
    """Checks if the video file already exists.

    Args:
        file_path: The full path of the video file.

    Returns:
        True if the file exists, otherwise False.
    """
    if os.path.exists(file_path):
        logger.warning("[!] Skipping (already downloaded): %s", file_path)
        return True
    return False


def download_file(
    session: requests.Session, url: str, file_path: str, filename: str
) -> None:
    """Downloads a video file and saves it to disk.

    Args:
        session: The session object for maintaining authentication.
        url: The direct URL of the video file.
        file_path: The path where the file should be saved.
        filename: The sanitized name of the video file.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    logger.info("[*] Initiating download: %s", file_path)

    try:
        with session.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with open(file_path, "wb") as file, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=filename
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))

        logger.info("[+] Download complete: %s", file_path)

    except requests.exceptions.RequestException as e:
        logger.error("[!] Download error for %s: %s", file_path, e)


def download_video(
    session: requests.Session,
    url: str,
    section_path: str,
    lesson_num: int,
    filename: str,
) -> None:
    """Handles the process of downloading a single video file.

    Args:
        session: The session object for maintaining authentication.
        url: The direct URL of the video file.
        section_path: The section directory path.
        lesson_num: The lesson number (used as prefix).
        filename: The sanitized name of the video file.
    """
    file_path = get_file_path(section_path, lesson_num, filename)

    if file_already_downloaded(file_path):
        return

    download_file(session, url, file_path, filename)


def download_videos(
    session: requests.Session,
    sections: Dict[str, List[Tuple[str, str]]],
    destination: str,
    course_prefix: str,
) -> None:
    """Manages the process of downloading videos from the given sections.

    Args:
        session: The session object for maintaining authentication.
        sections: Dictionary of sections with video details.
        destination: The base directory for saving videos.
        course_prefix: The course-specific prefix
    """
    lesson_counter = 1  # Global lesson counter across all sections
    section_counter = 1  # Section counter for prefixing section folders

    for section, videos in sections.items():
        section_path = get_section_path(destination, section_counter, section)
        section_counter += 1  # Increment section counter

        logger.info("=== Processing Section: %s (%d videos) ===", section, len(videos))

        for lesson_title, lesson_url in videos:
            mp4_url = get_mp4_url(session, lesson_url, course_prefix)
            download_video(session, mp4_url, section_path, lesson_counter, lesson_title)
            lesson_counter += 1  # Increment lesson counter across sections
