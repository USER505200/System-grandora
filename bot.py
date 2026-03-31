# bot.py
import discord
from discord.ext import commands
import config
import os

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    """عند تشغيل البوت"""
    print(f"✅ Prime07 Bot is online as {bot.user}")
    print(f"📊 Connected to {len(bot.guilds)} servers")
    
    # تحميل جميع الكوجات من مجلد cogs
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")

@bot.event
async def on_command_error(ctx, error):
    """معالجة الأخطاء"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Available commands: `!rules`, `!pay`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    else:
        print(f"Error: {error}")
        await ctx.send("❌ An error occurred while executing the command.")

# تشغيل البوت
if __name__ == "__main__":
    if not config.TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file!")
        print("Please create a .env file with DISCORD_TOKEN=your_token_here")
    else:
        bot.run(config.TOKEN)