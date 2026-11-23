"""Download the full Statistics Canada Table 14-10-0017-01 (Canada and all provinces).

The repo ships a Canada-only extract in data/raw/. To run the analysis for a province,
download the full table first:

    python analysis/download_data.py

This saves data/raw/14100017.csv (several hundred MB unzipped; it is git-ignored).
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
WDS = "https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/14100017/en"


def main():
    print("Asking StatCan for the download link...")
    with urllib.request.urlopen(WDS, timeout=60) as r:
        info = json.load(r)
    if info.get("status") != "SUCCESS":
        sys.exit(f"StatCan returned: {info}")
    url = info["object"]
    print(f"Downloading {url} ...")
    with urllib.request.urlopen(url, timeout=600) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extract("14100017.csv", DEST)
    print(f"Saved {DEST / '14100017.csv'}")


if __name__ == "__main__":
    main()
