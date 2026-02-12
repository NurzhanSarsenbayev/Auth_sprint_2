import argparse
import os

from core.config import settings
from helpers.superuser import ensure_superuser


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/ensure superuser")
    parser.add_argument("--db", type=str, help="Database URL (optional)")
    args = parser.parse_args()

    url = args.db or os.getenv("DB_URL") or settings.database_url
    url = url.replace("+asyncpg", "")

    print(f"Using database URL: {url}")
    ensure_superuser(url)


if __name__ == "__main__":
    main()