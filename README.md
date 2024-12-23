# Discord Custom Keyword Filter

This is a Python-based Discord bot designed to monitor messages in specific channels and forward them to target channels based on defined rules. 

It's current/intended use is to be able to create release channels and monitor discord channels for related embeds and forward them to the relevant channel. 

## Basic Features

- **Add Monitoring Rules**: Set up rules to monitor specific channels for messages containing specified keywords.
- **Remove Rules**: Remove existing monitoring rules for specific channels.
- **View Rules**: Display all currently configured monitoring rules.

## Prerequisites

- Python 3.8+
- `discord.py` library

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tanebufton/discord-custom-keyword.git
   cd ddiscord-custom-keyword
   ```

2. Install dependencies:

   ```bash
   pip install -U discord.py
   ```

3. Create a bot token from the [Discord Developer Portal](https://discord.com/developers/applications) and replace `BOT_TOKEN` in the code with your bot token. **Ensure** that both Message Content Intent and Message Intents are added to your bots permissions to ensure it can read the messages.

4. Run the bot:

   ```bash
   python discord_filter.py
   ```

## Commands

### Slash Commands

#### `/add_rule`
Add a new monitoring rule for a channel.

- **Parameters:**
  - `monitored_channel`: The channel to monitor.
  - `target_channel`: The channel to forward messages to.
  - `include_keywords`: Comma-separated list of keywords to include.
  - `exclude_keywords`: (Optional) Comma-separated list of keywords to exclude.

#### `/remove_rule`
Remove an existing rule for a monitored channel.

- **Parameters:**
  - `monitored_channel`: The channel with the rule.
  - `include_keywords`: Comma-separated list of keywords to match the rule.

#### `/view_rules`
View all currently configured monitoring rules.

## Configuration

The bot uses a JSON file (`channel_config.json`) to store monitoring rules. This ensures that the configuration persists even after the bot restarts - The bot will automaticlaly create this on the first run. 
