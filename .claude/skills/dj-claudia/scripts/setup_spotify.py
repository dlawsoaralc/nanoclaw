#!/usr/bin/env python3
"""
DJ Claudia — Spotify Setup
Handles OAuth, pulls taste profile, creates "DJ Claudia" playlist.
Called by setup.sh — not meant to be run directly.
"""

import argparse
import json
import os
import sys
from collections import Counter

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("❌ spotipy not found. Run setup.sh instead of this script directly.")
    sys.exit(1)

REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = " ".join([
    "user-top-read",           # read top artists/tracks for taste profile
    "playlist-modify-public",  # create and edit public playlists
    "playlist-modify-private", # create and edit private playlists
    "playlist-read-private",   # check if DJ Claudia playlist already exists
])

PLAYLIST_NAME = "DJ Claudia"
TOP_ARTISTS_LIMIT = 20   # how many top artists to pull per time range
TOP_TRACKS_LIMIT  = 20   # how many top tracks to pull per time range (for genre inference)


def build_taste_profile(sp: spotipy.Spotify) -> dict:
    """
    Pull top artists and infer top genres from medium_term (6 months)
    and long_term (all time), blending them with a 70/30 weight.
    """
    print("Pulling your Spotify taste profile...")

    def get_top_artists(time_range: str) -> list:
        results = sp.current_user_top_artists(limit=TOP_ARTISTS_LIMIT, time_range=time_range)
        return results.get("items", [])

    medium_artists = get_top_artists("medium_term")
    long_artists   = get_top_artists("long_term")

    # --- Artist names (medium_term primary, long_term fills in the rest) ---
    medium_names = [a["name"] for a in medium_artists]
    long_names   = [a["name"] for a in long_artists if a["name"] not in medium_names]
    top_artists  = medium_names[:15] + long_names[:5]  # 15 recent + 5 all-time

    # --- Genre blending ---
    # Weight: medium_term = 0.7, long_term = 0.3
    genre_scores: Counter = Counter()

    for artist in medium_artists:
        for genre in artist.get("genres", []):
            genre_scores[genre] += 0.7

    for artist in long_artists:
        for genre in artist.get("genres", []):
            genre_scores[genre] += 0.3

    # Top 15 genres by weighted score
    top_genres = [genre for genre, _ in genre_scores.most_common(15)]

    print(f"  ✅ Top artists ({len(top_artists)}): {', '.join(top_artists[:5])}{'...' if len(top_artists) > 5 else ''}")
    print(f"  ✅ Top genres ({len(top_genres)}):  {', '.join(top_genres[:5])}{'...' if len(top_genres) > 5 else ''}")

    return {
        "top_artists": top_artists,
        "top_genres": top_genres
    }


def get_or_create_playlist(sp: spotipy.Spotify, user_id: str) -> str:
    """
    Find the 'DJ Claudia' playlist if it exists, otherwise create it.
    Returns the playlist ID.
    """
    print(f"Looking for '{PLAYLIST_NAME}' playlist...")

    # Check existing playlists
    offset = 0
    while True:
        results = sp.current_user_playlists(limit=50, offset=offset)
        for playlist in results["items"]:
            if playlist["name"] == PLAYLIST_NAME:
                print(f"  ✅ Found existing playlist: {PLAYLIST_NAME}")
                return playlist["id"]
        if results["next"] is None:
            break
        offset += 50

    # Create it — use /me/playlists (newer endpoint, avoids 403 on /users/{id}/playlists)
    print(f"  Creating '{PLAYLIST_NAME}' playlist...")
    new_playlist = sp._post("me/playlists", payload={
        "name": PLAYLIST_NAME,
        "public": False,
        "description": "Curated by DJ Claudia 🎧 — refreshed every time you ask."
    })
    print(f"  ✅ Playlist created.")
    return new_playlist["id"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id",     required=True)
    parser.add_argument("--client-secret", required=True)
    parser.add_argument("--config-dir",    required=True)
    args = parser.parse_args()

    os.makedirs(args.config_dir, exist_ok=True)
    cache_path = os.path.join(args.config_dir, ".spotify_cache")

    # --- OAuth ---
    auth_manager = SpotifyOAuth(
        client_id=args.client_id,
        client_secret=args.client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        cache_path=cache_path,
        open_browser=True,
    )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    # Trigger auth flow — will open browser and prompt for redirect URL
    user = sp.current_user()
    user_id = user["id"]
    print(f"  ✅ Authenticated as: {user.get('display_name', user_id)}")
    print("")

    # --- Taste profile ---
    taste_profile = build_taste_profile(sp)
    print("")

    # --- Playlist ---
    playlist_id = get_or_create_playlist(sp, user_id)
    print("")

    # --- Save config ---
    config = {
        "spotify_user_id":    user_id,
        "spotify_playlist_id": playlist_id,
        "spotify_client_id":  args.client_id,
        "spotify_client_secret": args.client_secret,
        "taste_profile":      taste_profile,
    }

    config_path = os.path.join(args.config_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Lock down permissions — config contains secrets
    os.chmod(config_path, 0o600)

    print(f"  ✅ Config saved to {config_path}")


if __name__ == "__main__":
    main()
