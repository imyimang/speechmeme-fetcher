import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    description="Generate a random speechmeme GIF from speechmeme.com",
    allowed_installs=discord.app_commands.AppInstallationType(guild=True, user=True),
    allowed_contexts=discord.app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
)

CACHE_FILE = "speechmeme_cache.json"
CACHE_DURATION_HOURS = 2

def fetch_speechmeme_data():
    """Fetch speechmeme data"""
    url = "https://firestore.googleapis.com/v1/projects/speechmeme-bf897/databases/(default)/documents:runQuery"
    
    payload = {
        "structuredQuery": {
            "from": [{"collectionId": "posts"}],
            "orderBy": [{"field": {"fieldPath": "createdAt"}, "direction": "DESCENDING"}],
            "limit": 100
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload))
        results = resp.json()
        
        speechmeme_data = []
        for item in results:
            doc = item.get("document")
            if not doc:
                continue
                
            fields = doc.get("fields", {})
            display_name = fields.get("displayName", {}).get("stringValue", "unknown")
            image_url = fields.get("image", {}).get("stringValue")
            avatar_url = fields.get("photoURL", {}).get("stringValue")
            
            if image_url:
                speechmeme_data.append({
                    "display_name": display_name,
                    "image_url": image_url,
                    "avatar_url": avatar_url
                })
        
        return speechmeme_data
    except Exception as e:
        print(f"Error fetching speechmeme data: {e}")
        return []

def load_cached_data():
    """Load cached data if it exists and is still valid"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                print("Using cached data (Cache Hit)")
            cache_time = datetime.fromisoformat(cache_data.get("timestamp", ""))
            time_diff = datetime.now() - cache_time
            hours_passed = time_diff.total_seconds() / 3600

            print(f"Cache time: {cache_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Elapsed time: {hours_passed:.1f} hours")

            if datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS):
                print(f"Cache is still valid ({CACHE_DURATION_HOURS} hour limit)")
                return cache_data.get("data", [])
            else:
                print(f"Cache expired (exceeded {CACHE_DURATION_HOURS} hour limit)")
        else:
            print("Cache file not found")
    except Exception as e:
        print(f"Error loading cached data: {e}")
    
    return None

def save_cached_data(data):
    """Save data to cache"""
    try:
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving cached data: {e}")

def get_speechmeme_data():
    """Get speechmeme data (prefer cache)"""
    cached_data = load_cached_data()
    if cached_data:
        print("Using cached data (Cache Hit)")
        return cached_data

    print("Cache expired or not found, fetching new data from API...")
    fresh_data = fetch_speechmeme_data()
    if fresh_data:
        save_cached_data(fresh_data)
        print("Successfully fetched and updated cache data")
        return fresh_data

    print("Unable to fetch data from API")
    return []

@bot.event
async def on_ready():
    print(f'{bot.user} is logged in and ready!')
    print(f'Bot ID: {bot.user.id}')
    try:
        synced = await bot.tree.sync()
        print(f'Successfully synced {len(synced)} global commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name='speechmeme', description='Random SpeechMeme GIF From speechmeme.com')
@app_commands.allowed_installs(guilds=False, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def speechmeme_gif(interaction: discord.Interaction):
    speechmeme_data = get_speechmeme_data()

    if not speechmeme_data:
        await interaction.response.send_message("❌ Unable to fetch SpeechMeme data, please try again later!", ephemeral=True)
        return

    selected_meme = random.choice(speechmeme_data)

    embed = discord.Embed(
        color=discord.Color.from_rgb(0, 0, 0),
        timestamp=discord.utils.utcnow()
    )

    embed.set_image(url=selected_meme["image_url"])

    if selected_meme.get("avatar_url"):
        embed.set_footer(
            text=f"Author: {selected_meme['display_name']} • SpeechMeme Bot",
            icon_url=selected_meme["avatar_url"]
        )
    else:
        embed.set_footer(
            text=f"Author: {selected_meme['display_name']} • SpeechMeme Bot",
            icon_url=bot.user.display_avatar.url if bot.user else None
        )

    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("DISCORD_BOT_TOKEN not found in .env file. Please check your settings!")
    else:
        bot.run(token)