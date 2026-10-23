#!/usr/bin/env python3
"""Editor Supremo — upload a finished video to YouTube straight from the cloud server.

Subcommands (run from the OpenMontage folder, with the .venv active):

  auth    One-time authorization per channel. Needs an SSH tunnel from your PC:
            (PC)      ssh -L 8765:localhost:8765 editor@<server-ip>
            (server)  python scripts/channel_cloud/youtube_upload.py auth --channel HTH
          Open the printed link on your PC, pick the Google account AND the YouTube channel,
          accept. The channel id is recorded so a video can never go to the wrong channel.

  whoami  Show which YouTube channel each code is authorized for.
            python scripts/channel_cloud/youtube_upload.py whoami

  upload  Upload projects/<id>/renders/final.mp4 using projects/<id>/youtube_upload.json.
            python scripts/channel_cloud/youtube_upload.py upload --project projects/<id> [--dry-run]
          Refuses to run unless the render audit is PASS, the channel matches the project prefix
          (hth- / sv- / ba-), and the project was not uploaded before (YOUTUBE.txt).

youtube_upload.json:
  {
    "title": "...",                       # <= 100 chars, no < >
    "description": "...",                 # <= 5000 bytes, no < >
    "tags": ["...", "..."],               # total <= 500 chars
    "category_id": "27",                  # 27 Education, 22 People & Blogs, 19 Travel & Events
    "privacy": "private",                 # private | unlisted | public
    "publish_at": "2026-10-26T14:00:00Z", # optional; requires privacy=private (scheduled publish)
    "made_for_kids": false,
    "contains_synthetic_media": true,     # YouTube "altered or synthetic content" disclosure
    "default_language": "en",
    "thumbnail": "renders/thumbnail.jpg"  # optional; channel must be phone-verified
  }

Files (outside the repo, private to the server user):
  ~/.config/editor-supremo/youtube/client_secret.json   OAuth Desktop client from Google Cloud
  ~/.config/editor-supremo/youtube/token_<CODE>.json    one token per channel
  ~/.config/editor-supremo/youtube/channels.json        code -> channel id/title
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
CONFIG_DIR = Path(os.environ.get("EDITOR_SUPREMO_YT_DIR", Path.home() / ".config/editor-supremo/youtube"))
CLIENT_SECRET = CONFIG_DIR / "client_secret.json"
CHANNELS_FILE = CONFIG_DIR / "channels.json"
PREFIX_TO_CODE = {"hth-": "HTH", "sv-": "SV", "ba-": "BA"}
CODE_TO_NAME = {"HTH": "Hard Times Heritage", "SV": "Sumerian Vault", "BA": "Beneath America"}
VALID_PRIVACY = {"private", "unlisted", "public"}


def fail(message: str) -> None:
    sys.exit(f"[youtube] {message}")


def token_path(code: str) -> Path:
    return CONFIG_DIR / f"token_{code}.json"


def load_channels() -> dict:
    return json.loads(CHANNELS_FILE.read_text(encoding="utf-8")) if CHANNELS_FILE.exists() else {}


def save_private(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    os.chmod(path, 0o600)


def youtube_client(code: str):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    path = token_path(code)
    if not path.exists():
        fail(f"channel {code} is not authorized yet. Run: youtube_upload.py auth --channel {code}")
    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_private(path, creds.to_json())
        else:
            fail(f"token for {code} is no longer valid. Run auth again for {code}.")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def my_channel(youtube) -> dict:
    items = youtube.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not items:
        fail("this Google login has no YouTube channel selected")
    return {"channel_id": items[0]["id"], "title": items[0]["snippet"]["title"]}


# ------------------------------------------------------------------ auth

def cmd_auth(args: argparse.Namespace) -> None:
    from google_auth_oauthlib.flow import InstalledAppFlow

    code = args.channel.upper()
    if code not in CODE_TO_NAME:
        fail("--channel must be HTH, SV or BA")
    if not CLIENT_SECRET.exists():
        fail(f"missing {CLIENT_SECRET}. Copy the OAuth Desktop client JSON there first.")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    print(f"\nAuthorizing {CODE_TO_NAME[code]} ({code}).")
    print("Keep the SSH tunnel open on your PC:  ssh -L 8765:localhost:8765 editor@<server-ip>")
    creds = flow.run_local_server(
        host="localhost", port=args.port, open_browser=False,
        authorization_prompt_message="\nOpen this link on your PC, choose the account AND the channel "
                                     f"'{CODE_TO_NAME[code]}', then accept:\n\n{{url}}\n",
        success_message="Listo. Ya puedes cerrar esta pestaña y volver a la terminal.",
        prompt="consent", access_type="offline",
    )
    save_private(token_path(code), creds.to_json())
    from googleapiclient.discovery import build
    channel = my_channel(build("youtube", "v3", credentials=creds, cache_discovery=False))
    channels = load_channels()
    channels[code] = {**channel, "authorized_at": dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    save_private(CHANNELS_FILE, json.dumps(channels, indent=2))
    print(f"\nAuthorized {code} -> YouTube channel '{channel['title']}' ({channel['channel_id']})")
    if CODE_TO_NAME[code].lower().replace(" ", "") not in channel["title"].lower().replace(" ", "").replace(".", ""):
        print("WARNING: the channel title does not look like "
              f"'{CODE_TO_NAME[code]}'. If you picked the wrong channel, run auth again and choose the right one.")


def cmd_whoami(_: argparse.Namespace) -> None:
    channels = load_channels()
    if not channels:
        print("No channel authorized yet.")
    for code, info in channels.items():
        print(f"{code}: {info['title']} ({info['channel_id']}) authorized {info.get('authorized_at', '?')}")


# ------------------------------------------------------------------ upload

def validate_metadata(meta: dict, project: Path) -> list[str]:
    problems = []
    title = meta.get("title", "")
    if not title or len(title) > 100 or "<" in title or ">" in title:
        problems.append("title is required, max 100 characters, no < or >")
    description = meta.get("description", "")
    if len(description.encode("utf-8")) > 5000 or "<" in description or ">" in description:
        problems.append("description max 5000 bytes, no < or >")
    if len(",".join(meta.get("tags", []))) > 500:
        problems.append("tags exceed 500 characters in total")
    privacy = meta.get("privacy", "private")
    if privacy not in VALID_PRIVACY:
        problems.append(f"privacy must be one of {sorted(VALID_PRIVACY)}")
    publish_at = meta.get("publish_at")
    if publish_at:
        if privacy != "private":
            problems.append("publish_at requires privacy = private (YouTube publishes it at that time)")
        try:
            when = dt.datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
            if when <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15):
                problems.append("publish_at must be at least 15 minutes in the future (UTC)")
        except ValueError:
            problems.append("publish_at must be ISO 8601 UTC, e.g. 2026-10-26T14:00:00Z")
    if "contains_synthetic_media" not in meta:
        problems.append("contains_synthetic_media must be set explicitly (true/false) per the channel bible")
    thumb = meta.get("thumbnail")
    if thumb and not (project / thumb).exists():
        problems.append(f"thumbnail not found: {thumb}")
    return problems


def cmd_upload(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    project_id = project.name
    code = next((c for p, c in PREFIX_TO_CODE.items() if project_id.startswith(p)), None)
    if not code:
        fail("project id must start with hth-, sv- or ba-")
    video = project / "renders" / "final.mp4"
    if not video.exists():
        fail(f"missing {video}")
    report = project / "audit" / "render" / "audit_report.json"
    status = json.loads(report.read_text()).get("status") if report.exists() else None
    if status != "PASS":
        fail(f"BLOCKED: render audit is not PASS ({report})")
    done = project / "YOUTUBE.txt"
    if done.exists() and not args.force:
        fail(f"already uploaded ({done}). Use --force only if you deleted that video on YouTube.")
    meta_path = project / "youtube_upload.json"
    if not meta_path.exists():
        fail(f"missing {meta_path} (written at the publish stage from the channel bible)")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    problems = validate_metadata(meta, project)
    if problems:
        fail("youtube_upload.json problems:\n  - " + "\n  - ".join(problems))

    channels = load_channels()
    expected = channels.get(code)
    if not expected:
        fail(f"channel {code} is not authorized. Run: youtube_upload.py auth --channel {code}")

    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "categoryId": str(meta.get("category_id", "27")),
            "defaultLanguage": meta.get("default_language", "en"),
            "defaultAudioLanguage": meta.get("default_language", "en"),
        },
        "status": {
            "privacyStatus": meta.get("privacy", "private"),
            "selfDeclaredMadeForKids": bool(meta.get("made_for_kids", False)),
            "containsSyntheticMedia": bool(meta["contains_synthetic_media"]),
        },
    }
    if meta.get("publish_at"):
        body["status"]["publishAt"] = meta["publish_at"]

    print(f"Channel: {CODE_TO_NAME[code]} -> {expected['title']} ({expected['channel_id']})")
    print(f"Video:   {video} ({video.stat().st_size / 1e9:.2f} GB)")
    print(json.dumps(body, indent=2))
    if args.dry_run:
        print("\nDRY RUN: nothing uploaded.")
        return

    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    youtube = youtube_client(code)
    actual = my_channel(youtube)
    if actual["channel_id"] != expected["channel_id"]:
        fail(f"token for {code} points to '{actual['title']}', not '{expected['title']}'. Run auth again.")

    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=16 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media, notifySubscribers=True)
    response, retries = None, 0
    while response is None:
        try:
            status_chunk, response = request.next_chunk()
            if status_chunk:
                print(f"  uploaded {int(status_chunk.progress() * 100)}%")
        except HttpError as err:
            if err.resp.status in (500, 502, 503, 504) and retries < 8:
                retries += 1
                time.sleep(min(60, 2 ** retries))
                continue
            raise
        except (ConnectionError, TimeoutError, OSError):
            if retries < 8:
                retries += 1
                time.sleep(min(60, 2 ** retries))
                continue
            raise

    video_id = response["id"]
    url = f"https://youtu.be/{video_id}"
    print(f"Uploaded: {url}")

    thumb = meta.get("thumbnail")
    if thumb:
        try:
            youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(project / thumb))).execute()
            print("Thumbnail set.")
        except HttpError as err:
            print(f"WARNING: thumbnail not set ({err.resp.status}). Is the channel phone-verified? youtube.com/verify")

    check = youtube.videos().list(part="status", id=video_id).execute().get("items", [{}])[0].get("status", {})
    lines = [f"video_id={video_id}", f"url={url}", f"channel={expected['title']}",
             f"uploaded_at={dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
             f"privacy={check.get('privacyStatus')}", f"publish_at={check.get('publishAt', '')}",
             f"upload_status={check.get('uploadStatus')}"]
    done.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    wanted = meta.get("privacy", "private")
    if wanted != "private" and check.get("privacyStatus") == "private":
        print("\nNOTE: YouTube kept the video PRIVATE although you asked for "
              f"'{wanted}'. Your API project is probably unaudited; see the guide (audit form).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("auth")
    a.add_argument("--channel", required=True, help="HTH, SV or BA")
    a.add_argument("--port", type=int, default=8765)
    sub.add_parser("whoami")
    u = sub.add_parser("upload")
    u.add_argument("--project", required=True)
    u.add_argument("--dry-run", action="store_true")
    u.add_argument("--force", action="store_true")
    args = parser.parse_args()
    {"auth": cmd_auth, "whoami": cmd_whoami, "upload": cmd_upload}[args.command](args)


if __name__ == "__main__":
    main()
