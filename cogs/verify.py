# cogs/verify.py
import discord
from discord import EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle
from discord.ext import commands
from discord import Permissions
import config

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rules")
    @commands.has_permissions(administrator=True)
    async def send_rules(self, ctx):
        """إرسال Embed التحقق (للأدمن فقط)"""
        
        embed = discord.Embed(
            color=0x2b2d31,
            title="<a:vip:1487505119661785260>  Grindora — PREMIER OSRS SERVICES  <a:vip:1487505119661785260>",
            description=(
                "Welcome to **Prime07**, the premium standard for Old School RuneScape account progression. "
                "We turn your goals into progress—without the grind, using secure, hand-played expertise.\n"
                "━━━━━━━━━━━━━━━━━━"
            )
        )
        
        embed.add_field(
            name="💠 WHAT WE OFFER",
            value=(
                "⚡ **Skilling & Powerleveling:** 1–99 in any skill, including the new Sailing content.\n"
                "📜 **Questing & Diaries:** Full Quest Cape and Elite Diary completions.\n"
                "⚔️ **PvM & Raids:** Specialized teams for (ToB, HMT CoX (CM), and ToA (500s).\n"
                "🏆 **Elite Unlocks:** Inferno Capes, Colosseum Quivers, Combat Achievements, and Blood Torva."
            ),
            inline=False
        )
        
        embed.add_field(name="━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
        
        embed.add_field(
            name="🛡️ WHY CHOOSE PRIME07",
            value=(
                "✔ **Verified Grinders:** Hand-picked and deposit-verified for accountability.\n"
                "✔ **Account Integrity:** No macros, no bots — 100% hand-played or your money back.\n"
                "✔ **Rapid Delivery:** Strict, deadline-driven scheduling.\n"
                "✔ **Professional Support:** 24/7 oversight on every ticket."
            ),
            inline=False
        )
        
        embed.add_field(name="━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
        
        embed.add_field(
            name="🚀 GET STARTED",
            value=(
                f"📖 Read our <#{config.CH_RULES}> for safety protocols.\n"
                f"💰 Browse rates in <#{config.CH_RATES}>\n"
                f"🔥 Ready to get started? Open a ticket in <#{config.CH_TICKETS}>"
            ),
            inline=False
        )
        
        embed.add_field(name="━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
        
        embed.add_field(
            name="⚠️ SECURITY ADVISORY",
            value="**Grindora staff will NEVER DM you first or use external middlemen.\nAlways verify roles before sending GP/payment.**",
            inline=False
        )
        
        embed.add_field(name="━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
        
        embed.add_field(
            name="✅ VERIFY",
            value="Press the button below to accept the rules and gain access to the server as a **Member**.",
            inline=False
        )
        
        embed.set_footer(text="Grindora — Premier OSRS Services")
        embed.set_timestamp()
        
        button = ActionRowBuilder().add_component(
            ButtonBuilder(
                custom_id="prime07_verify",
                label="✅  Verify — I Accept the Rules",
                style=ButtonStyle.success
            )
        )
        
        await ctx.send(embed=embed, components=[button])
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        """معالجة زر التحقق"""
        if interaction.type != discord.InteractionType.component:
            return
        
        if interaction.data.get("custom_id") != "prime07_verify":
            return
        
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.user
        guild = interaction.guild
        role = guild.get_role(int(config.MEMBER_ROLE_ID))
        
        if not role:
            return await interaction.followup.send(
                "❌ Member role not found! Contact an admin.",
                ephemeral=True
            )
        
        if role in member.roles:
            return await interaction.followup.send(
                "⚠️ You are already a verified Member!",
                ephemeral=True
            )
        
        try:
            await member.add_roles(role)
            await interaction.followup.send(
                f"✅ **Welcome to Prime07, {member.display_name}!**\n"
                f"You have been granted the **{role.name}** role.\n\n"
                f"📖 Check <#{config.CH_RULES}> for safety protocols.\n"
                f"💰 Browse rates in <#{config.CH_RATES}>.\n"
                f"🎟️ Open a ticket in <#{config.CH_TICKETS}> when ready!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error adding role: {e}")
            await interaction.followup.send(
                "❌ Failed to add the role. Make sure the bot's role is **above** the Member role in the server settings.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Verify(bot))