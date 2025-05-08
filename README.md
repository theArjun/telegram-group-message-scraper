# Telegram Group Message Scraper

A respectful, rate-limited scraper for collecting messages from Telegram groups. This tool is designed to work within Telegram's terms of service by implementing conservative scraping strategies and appropriate rate limiting.

## Features

- Scrapes messages from specified Telegram groups
- Stores messages in CSV format for easy analysis
- Implements rate limiting to respect Telegram's API constraints
- Handles errors gracefully, including flood control exceptions
- Schedules periodic scraping with random intervals
- Maintains session persistence

## Requirements

- Python 3.8+
- Telegram API credentials (API ID and API Hash)
- A registered Telegram phone number

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/telegram-group-message-scraper.git
   cd telegram-group-message-scraper
   ```

2. Create a virtual environment:
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   uv pip install -r pyproject.toml
   ```

4. Set up your environment variables by copying the example file:
   ```
   cp .env.example .env
   ```

5. Edit `.env` with your Telegram API credentials and group information.

## Configuration

Create a `.env` file with the following variables:

```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE_NUMBER=your_phone_number
TELEGRAM_GROUP_USERNAME=target_group_username
```

You can get your API ID and API hash from [https://my.telegram.org/](https://my.telegram.org/).

## Usage

Run the script:

```
python main.py
```

The first time you run it, you'll need to authenticate with Telegram. The script will guide you through this process.

Messages will be saved to `telegram_messages.csv` in the current directory.

## Customization

You can adjust the scraping parameters in `main.py`:

- `MAX_MESSAGES_PER_BATCH`: Maximum number of messages to fetch per batch
- `MIN_DELAY_BETWEEN_BATCHES` and `MAX_DELAY_BETWEEN_BATCHES`: Random delay range between batches
- `SCRAPE_INTERVAL_MINUTES`: How often to scrape for new messages

## Ethical Considerations

This tool is intended for legitimate data collection purposes like research, archiving, or content analysis. Please use it responsibly:

- Always comply with Telegram's Terms of Service
- Respect the privacy and intellectual property of group members
- Only collect data from groups where you have permission or that are public
- Consider anonymizing sensitive data before analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not affiliated with Telegram. The developers are not responsible for any misuse of this tool or violations of Telegram's Terms of Service.
