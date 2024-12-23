import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

BOT_TOKEN = "INSERT BOT TOKEN HERE"
CONFIG_FILE = "channel_config.json"

bot = commands.Bot(command_prefix="!", intents=intents)
channel_config = {}
config_lock = asyncio.Lock()


async def save_config():
    async with config_lock:
        with open(CONFIG_FILE, "w") as file:
            json.dump(channel_config, file, indent=4)


async def load_config():
    global channel_config
    async with config_lock:
        try:
            with open(CONFIG_FILE, "r") as file:
                channel_config = json.load(file)
        except FileNotFoundError:
            channel_config = {}


@bot.event
async def on_ready():
    await load_config()
    await bot.tree.sync()
    print(f"Logged in as {bot.user}!")


@bot.tree.command(name="add_rule", description="Add a new rule for a monitored channel.")
async def add_rule(
    interaction: discord.Interaction,
    monitored_channel: discord.TextChannel,
    target_channel: discord.TextChannel,
    include_keywords: str,  # Comma-separated +keywords
    exclude_keywords: str = "",  # Optional, comma-separated -keywords
):
    """
    Adds a monitoring rule with optional exclude keywords.
    """
    include_list = [kw.strip().lower() for kw in include_keywords.split(",") if kw.strip()]
    exclude_list = [kw.strip().lower() for kw in exclude_keywords.split(",") if kw.strip()] if exclude_keywords else []

    if str(monitored_channel.id) not in channel_config:
        channel_config[str(monitored_channel.id)] = []

    channel_config[str(monitored_channel.id)].append({
        "target_channel": target_channel.id,
        "include_keywords": include_list,
        "exclude_keywords": exclude_list,
    })

    await save_config()
    await interaction.response.send_message(
        f"Added rule:\n"
        f"Monitored Channel: `{monitored_channel.name}`\n"
        f"Target Channel: `{target_channel.name}`\n"
        f"+ Keywords: {', '.join(include_list)}\n"
        f"- Keywords: {', '.join(exclude_list) if exclude_list else 'None'}",
    )



@bot.tree.command(name="remove_rule", description="Remove a rule for a monitored channel.")
async def remove_rule(
    interaction: discord.Interaction,
    monitored_channel: discord.TextChannel,
    include_keywords: str,  # Comma-separated +keywords
):
    include_list = [kw.strip().lower() for kw in include_keywords.split(",") if kw.strip()]

    if str(monitored_channel.id) in channel_config:
        original_length = len(channel_config[str(monitored_channel.id)])
        channel_config[str(monitored_channel.id)] = [
            rule for rule in channel_config[str(monitored_channel.id)]
            if rule["include_keywords"] != include_list
        ]

        if len(channel_config[str(monitored_channel.id)]) < original_length:
            await save_config()
            await interaction.response.send_message(
                f"Removed rule for `{monitored_channel.name}` with +keywords `{include_list}`.",
            )
            if not channel_config[str(monitored_channel.id)]:
                del channel_config[str(monitored_channel.id)]
        else:
            await interaction.response.send_message(
                f"No matching rule found for `{monitored_channel.name}` with +keywords `{include_list}`.",
            )
    else:
        await interaction.response.send_message(
            f"No rules found for `{monitored_channel.name}`.",
        )
        
@bot.tree.command(name="view_rules", description="View all current rules.")
async def view_rules(interaction: discord.Interaction):
    """
    Send a reponse with all current monitoring rules.
    """
    if not channel_config:
        await interaction.response.send_message("No rules are currently set.")
        return

    rules_summary = []
    for monitored_channel_id, rules in channel_config.items():
        channel_info = f"Monitored Channel: <#{monitored_channel_id}>"
        for rule in rules:
            target_channel = rule["target_channel"]
            include_keywords = ", ".join(rule["include_keywords"])
            exclude_keywords = ", ".join(rule["exclude_keywords"])
            rule_info = (
                f" → Target Channel: <#{target_channel}>\n"
                f"       Positive Keywords: {include_keywords}\n"
                f"       Negative Keywords: {exclude_keywords}\n"
            )
            rules_summary.append(f"{channel_info} {rule_info}")

    response = "\n".join(rules_summary)
    await interaction.response.send_message(f"**Current Rules:**\n{response}")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself but allows other bots / webhooks / etc
    if message.author == bot.user:
        return
        
    # Check if the channel is being monitored
    if str(message.channel.id) in channel_config:
        print(f"Checking Message in Channel: {message.channel.id}")
        tasks = [] 
        processed_channels = set()  # Track target channels already processed to avoid duplicate pings being matched on keywords and sending to the same channel

        for rule in channel_config[str(message.channel.id)]:
            print(f"Evaluating Rule: {rule}")
            include_keywords = [kw.lower() for kw in rule["include_keywords"]]
            exclude_keywords = [kw.lower() for kw in rule["exclude_keywords"]]

            matched_keywords = []  
            exclude_matches = False

            for embed in message.embeds:
                if embed.title: 
                    title = embed.title.lower()
                    matched_keywords.extend([kw for kw in include_keywords if kw in title])
                    exclude_matches = any(kw in title for kw in exclude_keywords)
                    print(f"Embed Title: {embed.title}, Matched Keywords: {matched_keywords}, Exclude Matches: {exclude_matches}")

                if exclude_matches:
                    break

            target_channel_id = rule["target_channel"]
            if matched_keywords and not exclude_matches and target_channel_id not in processed_channels:
                print(f"Message matches rule: {rule} with keywords: {matched_keywords}")
                target_channel = bot.get_channel(target_channel_id)
                if target_channel:
                    processed_channels.add(target_channel_id)
                    for embed in message.embeds:
                        tasks.append(target_channel.send(embed=embed))

        # Execute all tasks concurrently
        if tasks:
            await asyncio.gather(*tasks)

# Run the bot
bot.run(BOT_TOKEN)


