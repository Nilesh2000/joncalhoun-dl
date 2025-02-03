import argparse

from config import COURSE_CONFIG


def get_parser() -> argparse.ArgumentParser:
    """Creates and returns the argument parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="Download course videos from Calhoun.io."
    )

    parser.add_argument("--email", required=True, help="Your email for login.")
    parser.add_argument("--password", required=True, help="Your password for login.")
    parser.add_argument(
        "--course",
        required=True,
        choices=COURSE_CONFIG.keys(),
        help="The course to download.",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Custom destination folder for downloaded videos.",
    )

    return parser


def parse_arguments() -> argparse.Namespace:
    """Handles command-line arguments.

    Returns:
        The parsed command-line arguments.
    """
    parser = get_parser()
    args = parser.parse_args()

    # Set default destination folder if not provided
    if not args.dest:
        args.dest = COURSE_CONFIG[args.course]["default_folder"]

    return args
