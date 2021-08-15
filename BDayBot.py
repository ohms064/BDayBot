import discord
from discord.ext import commands
from BirthdayCog import BirthdayCog
import os

intents = discord.Intents.default()
intents.members = True
token = os.getenv("bday_bot_key")

bot = commands.Bot(command_prefix="!", intents=intents)
bot.add_cog(BirthdayCog(bot))
bot.run(token)
