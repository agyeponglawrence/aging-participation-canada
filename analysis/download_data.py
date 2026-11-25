"""Download the full Statistics Canada Table 14-10-0017-01 (Canada and all provinces).

The repo ships a Canada-only extract in data/raw/. To run the analysis for a province,
download the full table first:

    python analysis/download_data.py

This saves data/raw/14100017.csv (about 55 MB to download, 750 MB unzipped; it is git-ignored).
Then run, for example:

    python analysis/run.py --geo Saskatchewan --data data/raw/14100017.csv

If the script fails (StatCan's site is sometimes down for maintenance), download the CSV
by hand from https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701
("Download options" -> "Download entire table"), unzip it, and put 14100017.csv in data/raw/.
"""
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "raw"
# StatCan refuses requests with no client name, so the script names itself
HEADERS = {"User-Agent": "aging-participation-canada/1.0 (+https://github.com/agyeponglawrence/aging-participation-canada)"}
WDS = "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/14100017/en"


DIRECT = "https://www150.statcan.gc.ca/n1/tbl/csv/14100017-eng.zip"


def zip_url():
    """Ask StatCan's web data service for the current link; fall back to the fixed one."""
    try:
        with urllib.request.urlopen(urllib.request.Request(WDS, headers=HEADERS), timeout=60) as r:
            info = json.load(r)
        if info.get("status") == "SUCCESS":
            return info["object"]
    except Exception:
        pass
    return DIRECT


def main():
    url = zip_url()
    print(f"Downloading {url} (about 55 MB) ...")
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=600) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extract("14100017.csv", DEST)
    print(f"Saved {DEST / '14100017.csv'}")


MANUAL = ("Download failed. Get the table by hand instead:\n"
          "  1. Open https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701\n"
          "  2. Choose Download options -> Download entire table\n"
          "  3. Unzip it and put 14100017.csv in data/raw/")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # network errors, site maintenance, unexpected response
        sys.exit(f"{type(e).__name__}: {e}\n\n{MANUAL}")
