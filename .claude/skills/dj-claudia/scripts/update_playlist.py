#!/usr/bin/env python3
"""
DJ Claudia — Playlist Updater
Takes a list of tracks (artist + title), searches Spotify,
and refreshes the "DJ Claudia" playlist.

Usage:
    python3 update_playlist.py --tracks '["Artist - Title", "Artist - Title", ...]'

Called by the NanoClaw skill after Claude generates the track list.
"""

import argparse
import json
import os
import sys
import time

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("ERROR: spotipy not installed. Run setup.sh first.")
    sys.exit(1)

CONFIG_DIR  = os.environ.get("DJ_CLAUDIA_CONFIG_DIR", os.path.join(os.path.expanduser("~"), ".dj-claudia"))
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
CACHE_FILE  = os.path.join(CONFIG_DIR, ".spotify_cache")

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = " ".join([
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-private",
])

TARGET_TRACKS = 8   # minimum acceptable playlist length
MAX_TRACKS    = 10  # maximum tracks in final playlist


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        print("ERROR: Config not found. Run setup.sh first.")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_spotify_client(config: dict) -> spotipy.Spotify:
    auth_manager = SpotifyOAuth(
        client_id=config["spotify_client_id"],
        client_secret=config["spotify_client_secret"],
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=CACHE_FILE,
        open_browser=False,  # never open browser during normal operation
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def search_track(sp: spotipy.Spotify, track_string: str) -> str | None:
    """
    Search Spotify for a track given "Artist - Title".
    Returns the Spotify URI if found, None if not.
    """
    # Parse "Artist - Title" format
    if " - " in track_string:
        parts = track_string.split(" - ", 1)
        artist = parts[0].strip()
        title  = parts[1].strip()
        query  = f"track:{title} artist:{artist}"
    else:
        # Fallback: treat whole string as a free search
        query = track_string

    try:
        results = sp.search(q=query, type="track", limit=3)
        tracks  = results.get("tracks", {}).get("items", [])
        if tracks:
            return tracks[0]["uri"]
    except Exception as e:
        print(f"  Search error for '{track_string}': {e}", file=sys.stderr)

    return None


def resolve_tracks(sp: spotipy.Spotify, track_list: list[str]) -> list[str]:
    """
    Search each track and collect URIs.
    Returns up to MAX_TRACKS valid URIs.
    Logs hits and misses for transparency.
    """
    uris   = []
    misses = []

    for track in track_list:
        if len(uris) >= MAX_TRACKS:
            break

        uri = search_track(sp, track)
        if uri:
            uris.append(uri)
            print(f"  ✅ Found:   {track}")
        else:
            misses.append(track)
            print(f"  ⚠️  Missed:  {track}")

        # Be gentle with Spotify rate limits
        time.sleep(0.1)

    if misses:
        print(f"\n  {len(misses)} track(s) not found on Spotify — skipped.")

    return uris


def update_playlist(sp: spotipy.Spotify, playlist_id: str, uris: list[str]) -> None:
    """Replace all playlist tracks atomically (clear + add in one call, max 100)."""
    sp.playlist_replace_items(playlist_id, uris)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tracks",
        required=True,
        help='JSON array of "Artist - Title" strings. E.g. \'["Rosalía - BIZCOCHITO", "Kaytranada - 10%"]\''
    )
    args = parser.parse_args()

    # Parse track list
    try:
        track_list = json.loads(args.tracks)
        if not isinstance(track_list, list) or len(track_list) == 0:
            raise ValueError("Track list must be a non-empty JSON array.")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: Invalid --tracks argument: {e}")
        sys.exit(1)

    # Load config and authenticate
    config      = load_config()
    sp          = get_spotify_client(config)
    playlist_id = config["spotify_playlist_id"]

    print(f"\nSearching {len(track_list)} tracks on Spotify...\n")
    uris = resolve_tracks(sp, track_list)

    found = len(uris)

    if found < TARGET_TRACKS:
        # Signal to the skill that we need more suggestions
        print(f"\nRESULT: INSUFFICIENT tracks={found} needed={TARGET_TRACKS}")
        sys.exit(2)  # Exit code 2 = not enough tracks, retry needed

    print(f"\nUpdating '{config.get('spotify_playlist_id', 'DJ Claudia')}' playlist with {found} tracks...")
    update_playlist(sp, playlist_id, uris)

    print(f"\nRESULT: OK tracks={found}")
    sys.exit(0)


if __name__ == "__main__":
    main()
