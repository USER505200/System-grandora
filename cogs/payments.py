# cogs/payments.py
import discord
from discord.ext import commands
import config

class Payments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Image URLs
        self.TOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1489497861350494339/1489723944582910002/word_1.gif?ex=69d1750a&is=69d0238a&hm=e9861e30bd5918e66c2d324e9bf21104bd21d8c18de12fb6cfa00681ce6f51e1&"
        self.BOTTOM_IMAGE_URL = "https://cdn.discordapp.com/attachments/1489497861350494339/1489730355316392088/Untitled-1.gif?ex=69d17b02&is=69d02982&hm=91bba9f3cb622da72a3555f8a9ed89383f533898b0172e271605523595e1ce54&"

    @commands.command(name="pay")
    async def show_payments(self, ctx):
        """Display available payment methods"""
        
        embed = discord.Embed(
            title="💸 Payment Methods",
            description="Choose your preferred payment method:",
            color=0x2b2d31
        )
        
        # Top right image
        embed.set_thumbnail(url=self.TOP_IMAGE_URL)
        
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
        
        # Add security notice
        embed.add_field(
            name="⚠️ IMPORTANT",
            value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
            inline=False
        )
        
        # Bottom image
        embed.set_image(url=self.BOTTOM_IMAGE_URL)
        
        embed.set_footer(text="Grindora — Premier OSRS Services")
        embed.set_timestamp()
        
        await ctx.send(embed=embed)

    @commands.command(name="p", aliases=["P"])
    async def fast_payment(self, ctx, amount: float = None):
        """
        Fast payment card with images
        Usage: !p or !p 500
        """
        PAYMENT_URL = "https://payment.example.com/checkout"
        
        if amount is None:
            amount = 299.00
        
        embed = discord.Embed(
            title="⚡ !p / !P - Fast Payment Request ⚡",
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "**💳 Fast Payment • Quick Checkout**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.gold()
        )
        
        # Top right image
        embed.set_thumbnail(url=self.TOP_IMAGE_URL)
        
        embed.add_field(
            name="💰 Amount Due",
            value=f"**${amount:,.2f} USD**\n*Tax included*",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Payment Link",
            value=f"[Click Here to Pay]({PAYMENT_URL})\n`Shortcut !p or !P generates this card`",
            inline=False
        )
        
        embed.add_field(
            name="✅ Available Payment Methods",
            value="• Credit/Debit Cards (Visa/MasterCard)\n• Cryptocurrency (BTC, ETH, USDT)\n• Bank Transfer",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Security Notice",
            value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always verify staff before sending",
            inline=False
        )
        
        # Bottom image
        embed.set_image(url=self.BOTTOM_IMAGE_URL)
        
        embed.set_footer(
            text="🧾 Shortcut !p or !P | Payment request generated successfully",
            icon_url="https://cdn.discordapp.com/emojis/1487505119661785260.gif"
        )
        
        # Payment button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="💸 Pay Now 💸",
            url=PAYMENT_URL,
            style=discord.ButtonStyle.link,
            emoji="💳"
        ))
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Payments(bot))