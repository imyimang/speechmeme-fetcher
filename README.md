# Speechmeme Fetcher

This project is a Discord bot that fetches and displays GIFs from speechmeme.com by reverse-engineering its backend Firestore API.

![alt text](image.png)

[Invite the bot](https://discord.com/oauth2/authorize?client_id=1421194406601691178)
## Features
- Fetches the latest speechmeme posts by directly querying the Firestore backend
- Caches results locally to reduce repeated requests
- Provides a Discord slash command to display random speechmeme GIFs
- Supports user install (can be installed by individual Discord users, not just server admins)
- Supports multiple contexts (guild, DM, private channel)

## Technical Details
- Utilizes requests for HTTP POST calls to the Firestore API endpoint
- Caching is implemented via a local JSON file with expiration logic (default: 2 hours)
- Speechmeme data is fetched by sending a custom query to the Firestore REST API, imitating the website's backend requests
- The bot uses Discord application commands (slash commands) for interaction

## Setup
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file and add your Discord bot token
4. Run the bot: `python bot.py`