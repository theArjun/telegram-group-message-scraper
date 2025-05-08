from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pandas as pd
import asyncio
import os
import random
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram API credentials
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE_NUMBER")
group_username = os.getenv("TELEGRAM_GROUP_USERNAME")

# File to store messages
output_file = "telegram_messages.csv"

# Scraping configuration
MAX_MESSAGES_PER_BATCH = 20  # More conservative limit
MIN_DELAY_BETWEEN_BATCHES = 2  # Seconds
MAX_DELAY_BETWEEN_BATCHES = 5  # Seconds
SCRAPE_INTERVAL_MINUTES = 120  # More conservative interval (2 hours)

# Initialize Telegram client
client = TelegramClient("session_name", api_id, api_hash)


async def random_delay(min_seconds=1, max_seconds=3):
    """Add a random delay to avoid hitting rate limits"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)


async def validate_group():
    """Validate that the group username is valid and accessible"""
    try:
        # Check if group_username is set
        if not group_username:
            print(f"[{datetime.now()}] ERROR: TELEGRAM_GROUP_USERNAME environment variable is not set.")
            return None
            
        # Try to get the group entity
        group = await client.get_entity(group_username)
        return group
    except ValueError as e:
        if "Cannot find any entity corresponding to" in str(e):
            print(f"[{datetime.now()}] ERROR: Could not find group '{group_username}'. Please check if the username is correct.")
        elif "Cannot cast NoneType to any kind of Peer" in str(e):
            print(f"[{datetime.now()}] ERROR: Group username '{group_username}' could not be resolved to a Telegram group.")
        else:
            print(f"[{datetime.now()}] ERROR: Invalid group: {str(e)}")
        return None
    except Exception as e:
        print(f"[{datetime.now()}] ERROR while validating group: {str(e)}")
        return None


async def scrape_messages():
    try:
        # Check if we're already logged in
        if not client.is_connected():
            await client.start(phone)
            
        # Get and validate the group entity
        group = await validate_group()
        if not group:
            print(f"[{datetime.now()}] Skipping scrape due to invalid group.")
            return
        
        # Load existing messages if file exists
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            existing_message_ids = set(existing_df["message_id"].astype(int))
        else:
            existing_message_ids = set()
            existing_df = pd.DataFrame(
                columns=["message_id", "sender_id", "message", "date"]
            )
        
        # Scrape new messages with conservative batching
        new_messages = []
        message_count = 0
        
        print(f"[{datetime.now()}] Starting message scraping...")
        
        async for message in client.iter_messages(group, limit=MAX_MESSAGES_PER_BATCH):
            # Skip messages we've already processed
            if message.id in existing_message_ids:
                continue
                
            # Only process messages with text content
            if message.text:
                new_messages.append(
                    {
                        "message_id": message.id,
                        "sender_id": message.sender_id,
                        "message": message.text,
                        "date": message.date,
                    }
                )
                message_count += 1
                
            # Add small random delay between message processing
            if message_count % 5 == 0:  # Every 5 messages
                await random_delay(0.5, 1.5)
        
        # Append new messages to DataFrame
        if new_messages:
            new_df = pd.DataFrame(new_messages)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df.to_csv(output_file, index=False)
            print(f"[{datetime.now()}] {len(new_messages)} new messages saved to {output_file}")
        else:
            print(f"[{datetime.now()}] No new messages found.")
            
        # Add a longer delay after batch completion
        delay = random.uniform(MIN_DELAY_BETWEEN_BATCHES, MAX_DELAY_BETWEEN_BATCHES)
        print(f"[{datetime.now()}] Waiting {delay:.2f} seconds before next operation...")
        await asyncio.sleep(delay)
        
    except FloodWaitError as e:
        # Handle rate limiting by waiting the required time
        wait_time = e.seconds
        print(f"[{datetime.now()}] Rate limit hit! Waiting for {wait_time} seconds as requested by Telegram")
        await asyncio.sleep(wait_time)
        print(f"[{datetime.now()}] Resuming after rate limit wait")
    except Exception as e:
        print(f"[{datetime.now()}] Error during scraping: {str(e)}")
        await asyncio.sleep(30)  # Wait 30 seconds before retrying


async def main():
    # Run the scraper immediately on start
    await client.start(phone)
    print(f"[{datetime.now()}] Initial scrape starting...")
    
    # First validate the group
    group = await validate_group()
    if not group:
        print(f"[{datetime.now()}] WARNING: Group validation failed. Please check your TELEGRAM_GROUP_USERNAME in .env file.")
        print(f"[{datetime.now()}] The script will continue to run and attempt to scrape, but may fail if the group is invalid.")
    
    await scrape_messages()

    # Set up scheduler to run periodically with a more conservative interval
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scrape_messages, 
        "interval", 
        minutes=SCRAPE_INTERVAL_MINUTES,
        jitter=300  # Add up to 5 minutes of random jitter to avoid patterns
    )
    scheduler.start()
    
    print(f"[{datetime.now()}] Scheduler started. Will scrape every {SCRAPE_INTERVAL_MINUTES} minutes (±5 minutes jitter)")

    # Keep the script running
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        scheduler.shutdown()
        await client.disconnect()
        print(f"[{datetime.now()}] Script terminated by user")


if __name__ == "__main__":
    asyncio.run(main())
