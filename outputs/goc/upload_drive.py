#!/usr/bin/env python3
"""Upload SIA GoC collateral to Google Drive.

Requires OAuth setup once: run the google-workspace skill setup, or
place google_token.json + google_client_secret.json in ~/.hermes/,
then this script uploads outputs/goc/* to a 'SIA' folder on Drive.
Usage: python3 outputs/goc/upload_drive.py [--folder SIA]
"""
import json
import sys
from pathlib import Path

HOME = Path.home()
TOKEN = HOME / ".hermes" / "google_token.json"
SECRET = HOME / ".hermes" / "google_client_secret.json"
GOC = Path(__file__).resolve().parent
FILES = sorted(p for p in GOC.iterdir() if p.suffix in (".md", ".pptx", ".py"))


def main():
    if not TOKEN.exists() or not SECRET.exists():
        print("Drive upload requires OAuth setup first:")
        print("  1. python ~/.hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret <path>")
        print("  2. follow the auth URL, paste back the redirect code")
        print("  3. rerun this script")
        sys.exit(1)
    # Once OAuth exists, use googleapiclient (pip: google-api-python-client)
    print(f"OAuth present. Would upload {len(FILES)} files from {GOC}:" )
    for f in FILES:
        print(" -", f.name)
    print("(google-api-python-client upload logic hooks here when auth is done)")


if __name__ == "__main__":
    main()
