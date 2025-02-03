import logging

import requests

from auth import login
from config import COURSE_CONFIG
from downloader import download_videos
from scraper import get_sections_and_lesson_urls
from utils import parse_arguments

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to handle authentication, scraping, and downloading course videos."""
    try:
        args = parse_arguments()

        email: str = args.email
        password: str = args.password
        course_name: str = args.course
        destination: str = args.dest

        # Fetch course metadata
        course_info = COURSE_CONFIG.get(course_name)
        if not course_info:
            logger.error("[!] Invalid course selected: %s", course_name)
            return

        course_prefix = course_info["prefix"]

        session: requests.Session = requests.Session()

        # Login
        login(session, email, password)

        # Fetch sections and videos
        sections, total_lessons = get_sections_and_lesson_urls(session, course_name)

        # Download Videos
        download_videos(session, sections, destination, course_prefix)

        logger.info(
            "=== ✅ Download Complete. Total Videos Processed: %d ===", total_lessons
        )

    except Exception as e:
        logger.error("[!] An unexpected error occurred: %s", str(e), exc_info=True)


if __name__ == "__main__":
    main()
