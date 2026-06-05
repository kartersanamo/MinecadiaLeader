# Minecadia Leader Bot

Discord bot for faction leaders and staff channel management on Minecadia.

## What it does

- Kitmap bundle ticket panel and toggle
- Faction leader tools and admin list
- Channel lock, close, rename, purge, and edit
- Thread listing and staff request commands

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # add DISCORD_TOKEN, DB_*
python main.py
```

## Config

- `.env` — token and database
- `assets/config.json` — presence and bot settings
