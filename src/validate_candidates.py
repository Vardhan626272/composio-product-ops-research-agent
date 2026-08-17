import csv
from pathlib import Path

from url_candidates import URL_CANDIDATES


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_FILE = PROJECT_ROOT / "data" / "apps.csv"


def load_apps() -> list[dict]:
    with APPS_FILE.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    apps = load_apps()

    print("Apps in CSV:", len(apps))
    print("URL candidate entries:", len(URL_CANDIDATES))

    missing = []

    for row in apps:
        app = row["app"]

        if app not in URL_CANDIDATES:
            missing.append(app)

    if missing:
        print("\nMissing URL candidates:")
        for app in missing:
            print("-", app)
    else:
        print("\nAll 100 apps have URL candidates.")