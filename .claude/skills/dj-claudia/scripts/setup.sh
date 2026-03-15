#!/bin/bash

# =============================================================================
# DJ Claudia — Setup Script
# Installs dependencies, authenticates with Spotify, pulls taste profile,
# and creates the "DJ Claudia" playlist.
# Run once. Re-run to re-authenticate or reset.
# =============================================================================

set -e

CONFIG_DIR="$HOME/.dj-claudia"
CONFIG_FILE="$CONFIG_DIR/config.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "🎧 DJ Claudia — Setup"
echo "─────────────────────────────────────────"
echo ""

# -----------------------------------------------------------------------------
# Step 1 — Check Python
# -----------------------------------------------------------------------------
echo "Checking Python..."

if ! command -v python3 &>/dev/null; then
  echo "❌ Python 3 not found."
  echo "   Install it from https://www.python.org/downloads/ or via Homebrew:"
  echo "   brew install python"
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info.minor)')
if [ "$PYTHON_VERSION" -lt 8 ]; then
  echo "❌ Python 3.8 or higher is required. Found: $(python3 --version)"
  exit 1
fi

echo "✅ Python $(python3 --version) found."
echo ""

# -----------------------------------------------------------------------------
# Step 2 — Install spotipy
# -----------------------------------------------------------------------------
echo "Checking dependencies..."

if ! python3 -c "import spotipy" &>/dev/null; then
  echo "Installing spotipy..."
  pip3 install spotipy --quiet
  echo "✅ spotipy installed."
else
  echo "✅ spotipy already installed."
fi

echo ""

# -----------------------------------------------------------------------------
# Step 3 — Spotify credentials
# -----------------------------------------------------------------------------
echo "Spotify credentials"
echo "You'll find these at https://developer.spotify.com/dashboard"
echo ""

read -p "  Client ID:     " SPOTIFY_CLIENT_ID
read -s -p "  Client Secret: " SPOTIFY_CLIENT_SECRET
echo ""
echo ""

if [ -z "$SPOTIFY_CLIENT_ID" ] || [ -z "$SPOTIFY_CLIENT_SECRET" ]; then
  echo "❌ Client ID and Client Secret are required."
  exit 1
fi

# -----------------------------------------------------------------------------
# Step 4 — OAuth + taste profile + playlist creation (Python)
# -----------------------------------------------------------------------------
echo "Opening Spotify authorization in your browser..."
echo "After you approve access, you'll be redirected to a localhost page."
echo "Paste the full redirect URL back here when prompted."
echo ""

python3 "$SCRIPT_DIR/setup_spotify.py" \
  --client-id "$SPOTIFY_CLIENT_ID" \
  --client-secret "$SPOTIFY_CLIENT_SECRET" \
  --config-dir "$CONFIG_DIR"

# -----------------------------------------------------------------------------
# Step 5 — Done
# -----------------------------------------------------------------------------
echo ""
echo "─────────────────────────────────────────"
echo "✅ DJ Claudia is ready."
echo ""
echo "Send @claudia <your vibe> on WhatsApp to get your first playlist."
echo "─────────────────────────────────────────"
echo ""
