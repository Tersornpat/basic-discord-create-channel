from dotenv import load_dotenv
import os
import discord
from discord.ext import commands

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv('TOKEN')

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if str(payload.emoji) == "🔥":  # ตรวจสอบอิโมจิที่ถูกใช้
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            guild = await bot.fetch_guild(payload.guild_id)

        user = guild.get_member(payload.user_id)
        if user is None:
            user = await guild.fetch_member(payload.user_id)

        # ตรวจสอบการตั้งค่า Categories
        category = discord.utils.get(guild.categories, name="Private Channels")
        if not category:
            category = await guild.create_category("Private Channels")

        # ตรวจสอบว่าช่องทางที่มีชื่อเดียวกันมีอยู่แล้วหรือไม่
        existing_channel = discord.utils.get(
            guild.text_channels, name=f"channel-{user.name}"
        )
        if existing_channel:
            await existing_channel.send(
                f"Welcome back, {user.mention}! You already have a private channel."
            )
            return

        # Get the role object
        role_id = 1258100615871987804
        role = guild.get_role(role_id)
        if role is None:
            role = await guild.fetch_role(role_id)

        # สร้างช่องทางใหม่
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),  # Add the role to the private channel
        }
        channel_name = f"channel-{user.name}"
        channel = await guild.create_text_channel(
            channel_name, overwrites=overwrites, category=category
        )
        new_role = 1258100574533058672
        try:
            await user.add_roles(new_role)
        except discord.Forbidden:
            print("Missing Permissions: Cannot add role")
        except Exception as e:
            print(f"An error occurred: {e}")

        await channel.send(f"Welcome, {user.mention} to your private channel!")

bot.run(TOKEN)
