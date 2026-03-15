# DJ Claudia 🎧

A personal DJ agent for [NanoClaw](https://github.com/qwibitai/nanoclaw). Send a WhatsApp message describing your mood, activity, or moment — Claudia curates an eclectic 8-10 track playlist and pushes it live to your Spotify.

> "Long day at work, gym incoming, leg day, give me some energy"
> → Spotify refreshed. 🎧

---

## Philosophy

Claudia doesn't pick the obvious track. She blends genres, crosses eras, and pulls from different cultural wells — think Trinix, not The Chainsmokers. Your taste profile anchors the vibe without locking her into a formula.

---

## Requirements

- [NanoClaw](https://github.com/qwibitai/nanoclaw) installed and running
- Python 3.8+
- A Spotify account (free or premium)
- A Spotify Developer app ([create one here](https://developer.spotify.com/dashboard))

---

## Installation

### 1. Copy the skill into your NanoClaw repo

```bash
mkdir -p ~/nanoclaw/.claude/skills/dj-claudia/scripts

cp SKILL.md ~/nanoclaw/.claude/skills/dj-claudia/
cp scripts/setup.sh ~/nanoclaw/.claude/skills/dj-claudia/scripts/
cp scripts/setup_spotify.py ~/nanoclaw/.claude/skills/dj-claudia/scripts/
cp scripts/update_playlist.py ~/nanoclaw/.claude/skills/dj-claudia/scripts/

chmod +x ~/nanoclaw/.claude/skills/dj-claudia/scripts/setup.sh
```

### 2. Create a Spotify Developer app

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a new app — name it anything you like
3. Set the Redirect URI to: `http://127.0.0.1:8888/callback`
4. Check **Web API** under API/SDKs
5. Copy your **Client ID** and **Client Secret**

> ⚠️ Spotify apps start in Development Mode. Go to **User Management** in your app dashboard and add your Spotify account email so you can authorize it.

### 3. Run setup

Inside your NanoClaw directory, open Claude Code:

```bash
cd ~/nanoclaw
claude
```

Then run:

```
/dj-claudia-setup
```

This will:
- Install `spotipy` if not already present
- Ask for your Client ID and Client Secret
- Open Spotify authorization in your browser
- Pull your taste profile (top artists + genres, last 6 months + all-time blend)
- Create a private **"DJ Claudia"** playlist in your Spotify account
- Save config to `~/.dj-claudia/config.json`

---

## Usage

Send a WhatsApp message to your NanoClaw number starting with `@claudia`:

```
@claudia long day, need something to cook dinner to, lowkey but not sleepy
@claudia gym time, legs, give me energy
@claudia sunday morning, slow, coffee, make it feel like buenos aires
@claudia driving at night, highway, something cinematic
```

Claudia will reply on WhatsApp and your Spotify playlist will be refreshed within seconds.

---

## What gets stored

All credentials and personal data are stored locally on your machine at `~/.dj-claudia/` and are never committed to any repo.

```
~/.dj-claudia/
  config.json         ← Spotify credentials, playlist ID, taste profile
  .spotify_cache      ← OAuth token cache (auto-refreshed by spotipy)
```

`config.json` is created with `chmod 600` — only your user can read it.

---

## Re-authentication

If your tokens expire or you want to connect a different Spotify account, just re-run setup:

```
/dj-claudia-setup
```

---

## Sharing this skill

This skill is designed to be shared. Each person runs their own setup — credentials and taste profiles are always personal and local. Nothing in this repo contains any user data.

To share: point friends to this repo and have them follow the installation steps above.

---

## Troubleshooting

**"Config not found. Run setup.sh first."**
Run `/dj-claudia-setup` in Claude Code inside your NanoClaw directory.

**"Only found N tracks this time"**
Claudia searched Spotify and came up short. Try again with a bit more context in your message, or rephrase the vibe.

**Playlist not updating**
Check that your Spotify Developer app has `http://127.0.0.1:8888/callback` as a Redirect URI and that your account email is added under User Management.

**spotipy install fails**
Try manually: `pip3 install spotipy` — then re-run setup.

---

## License

MIT
