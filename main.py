from telethon.sync import TelegramClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pandas as pd
import asyncio
import os

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

# Initialize Telegram client
client = TelegramClient("session_name", api_id, api_hash)


async def scrape_messages():
    await client.start(phone)

    # Get the group entity
    group = await client.get_entity(group_username)

    # Load existing messages if file exists
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        existing_message_ids = set(existing_df["message_id"].astype(int))
    else:
        existing_message_ids = set()
        existing_df = pd.DataFrame(
            columns=["message_id", "sender_id", "message", "date"]
        )

    # Scrape new messages
    new_messages = []
    async for message in client.iter_messages(
        group, limit=100
    ):  # Adjust limit as needed
        if message.id not in existing_message_ids and message.text:
            new_messages.append(
                {
                    "message_id": message.id,
                    "sender_id": message.sender_id,
                    "message": message.text,
                    "date": message.date,
                }
            )

    # Append new messages to DataFrame
    if new_messages:
        new_df = pd.DataFrame(new_messages)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        updated_df.to_csv(output_file, index=False)
        print(f"{len(new_messages)} new messages saved to {output_file}")
    else:
        print("No new messages found.")


async def main():
    # Run the scraper immediately on start
    await scrape_messages()

    # Set up scheduler to run periodically
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scrape_messages, "interval", minutes=60)  # Run every 60 minutes
    scheduler.start()

    # Keep the script running
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        scheduler.shutdown()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
