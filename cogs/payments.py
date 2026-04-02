# cogs/payments.py
import discord
from discord.ext import commands
import config

class Payments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pay", aliases=["p", "P"])
    async def show_payments(self, ctx):
        """عرض طرق الدفع المتاحة"""
        
        embed = discord.Embed(
            title="💸 Payment Methods",
            description="Choose your preferred payment method:",
            color=0x2b2d31
        )
        
        # إضافة الصورة في أعلى اليمين (thumbnail)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1487311776256098414/1489130417838882916/HHHHHHHHHHHHHHHHHHHHHH.gif")
        
        for method, info in config.PAYMENT_ADDRESSES.items():
            emoji = info.get("emoji", "")
            address = info.get("address")
            
            if address:
                value = f"{emoji} **{method}**\n```\n{address}\n```"
            else:
                value = f"{emoji} **{method}**\n{info.get('details', '')}"
            embed.add_field(
                name=f"**{method}**",
                value=value,
                inline=False
            )
        
        embed.set_footer(text="Grindora — Premier OSRS Services")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Payments(bot))