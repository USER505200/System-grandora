# bot.py - الملف الرئيسي المتكامل
import discord
from discord import app_commands
from discord.ext import commands
import config
import json
import os
from datetime import datetime

# ==========================================
# BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ==========================================
# إعدادات الفيدباك
# ==========================================
SETTINGS_FILE = "settings.json"

def save_settings():
    settings = {
        "worker_role_id": config.WORKER_ROLE_ID,
        "feedback_channel_id": config.FEEDBACK_CHANNEL_ID
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                config.WORKER_ROLE_ID = settings.get("worker_role_id")
                config.FEEDBACK_CHANNEL_ID = settings.get("feedback_channel_id")
        except:
            pass

def get_workers_in_channel(channel: discord.TextChannel):
    workers = []
    if config.WORKER_ROLE_ID:
        worker_role = channel.guild.get_role(config.WORKER_ROLE_ID)
        if worker_role:
            for member in channel.members:
                if worker_role in member.roles and not member.bot:
                    workers.append(member)
    return workers

# ==========================================
# MODAL FOR FEEDBACK SUBMISSION
# ==========================================
class FeedbackModal(discord.ui.Modal, title="Submit Feedback"):
    description = discord.ui.TextInput(
        label="Review",
        placeholder="Write your review here...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    customer_name = discord.ui.TextInput(
        label="Your Name (Optional)",
        placeholder="Leave empty to keep hidden",
        required=False,
        max_length=100
    )

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        workers_in_channel = get_workers_in_channel(self.channel)
        
        if not workers_in_channel:
            await interaction.response.send_message(
                "❌ No workers found in this channel/ticket. Make sure you have set the correct worker role.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="⭐ Feedback Received ⭐",
            color=discord.Color.from_rgb(184, 92, 26)
        )
        
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1487311776256098414/1489130417838882916/HHHHHHHHHHHHHHHHHHHHHH.gif")
        
        review_text = f"```{self.description.value}```"
        embed.add_field(name="📝 Review", value=review_text, inline=False)
        
        if self.customer_name.value and self.customer_name.value.strip():
            customer_value = f"**{self.customer_name.value}**\n\n⭐⭐⭐⭐⭐"
        else:
            customer_value = f"*hidden*\n\n⭐⭐⭐⭐⭐"
        
        embed.add_field(name="👤 Customer", value=customer_value, inline=True)
        
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        embed.set_footer(text=f"Submitted • {current_time}")
        
        if config.FEEDBACK_CHANNEL_ID:
            feedback_channel = interaction.guild.get_channel(config.FEEDBACK_CHANNEL_ID)
            if feedback_channel:
                await feedback_channel.send(embed=embed)
                
                confirm_embed = discord.Embed(
                    title="✅ Review Submitted Successfully!",
                    description="**Thank you for your feedback!**\nYour review has been recorded and appreciated.",
                    color=discord.Color.green()
                )
                confirm_embed.set_thumbnail(url="https://media.discordapp.net/attachments/1487311776256098414/1489130417838882916/HHHHHHHHHHHHHHHHHHHHHH.gif")
                confirm_embed.set_footer(text="Grindora Services ⭐")
                
                await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Feedback channel not found.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Feedback channel not set. Use `!setreviewchannel` to set it first.", ephemeral=True)

# ==========================================
# BUTTON VIEWS FOR FEEDBACK
# ==========================================
class FeedbackButton(discord.ui.View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="📝 Submit Review", style=discord.ButtonStyle.primary, custom_id="feedback_button", emoji="⭐")
    async def feedback_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FeedbackModal(self.channel))

class MainFeedbackView(discord.ui.View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.add_item(FeedbackButton(channel).children[0])
        sythe_button = discord.ui.Button(
            label="Sythe Vouches",
            style=discord.ButtonStyle.link,
            url="https://www.sythe.org/threads/prime07-official-vouches/",
            emoji="📜"
        )
        self.add_item(sythe_button)

# ==========================================
# دالة التحقق من الصلاحية لـ !pay (نفس الكود القديم)
# ==========================================
def has_allowed_role():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        for role_id in config.ALLOWED_PAY_ROLES:
            role = ctx.guild.get_role(role_id)
            if role and role in ctx.author.roles:
                return True
        return False
    return commands.check(predicate)

# ==========================================
# كلاس القائمة المنسدلة للدفع (نفس الكود القديم)
# ==========================================
class PaymentSelect(ui.Select):
    def __init__(self):
        options = []
        for name, data in config.PAYMENT_ADDRESSES.items():
            options.append(
                discord.SelectOption(
                    label=name,
                    emoji=data.get("emoji", "💰"),
                    description=f"Click to view {name} payment details"
                )
            )
        super().__init__(
            placeholder="💰 Select a payment method...",
            options=options,
            custom_id="payment_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0]
        payment_data = config.PAYMENT_ADDRESSES[selected]
        
        embed = discord.Embed(
            title=f"{payment_data.get('emoji', '💰')} {selected} - Payment Details",
            description=payment_data["details"],
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="⚠️ IMPORTANT",
            value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PaymentView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentSelect())

# ==========================================
# كلاس زر التحقق (نفس الكود القديم)
# ==========================================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Verify — I Accept the Rules", style=discord.ButtonStyle.success, custom_id="Grindora_verify")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.user
        guild = interaction.guild
        role = guild.get_role(int(config.MEMBER_ROLE_ID))
        
        if not role:
            return await interaction.followup.send("❌ Member role not found! Contact an admin.", ephemeral=True)
        
        if role in member.roles:
            return await interaction.followup.send("⚠️ You are already a verified Member!", ephemeral=True)
        
        try:
            await member.add_roles(role)
            await interaction.followup.send(
                f"✅ **Welcome to Grindora, {member.display_name}!**\n"
                f"You have been granted the **{role.name}** role.\n\n"
                f"📖 Check <#{config.CH_RULES}> for safety protocols.\n"
                f"💰 Browse rates in <#{config.CH_RATES}>.\n"
                f"🎟️ Open a ticket in <#{config.CH_TICKETS}> when ready!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error adding role: {e}")
            await interaction.followup.send(
                "❌ Failed to add the role. Make sure the bot's role is **above** the Member role.",
                ephemeral=True
            )

# ==============================
# أمر !rules - نظام التحقق (نفس الكود القديم)
# ==============================
@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def send_rules(ctx):
    """إرسال Embed التحقق (للأدمن فقط)"""
    
    embed = discord.Embed(
        color=0x2b2d31,
        title="<a:vip:1487505119661785260>  Grindora — PREMIER OSRS SERVICES  <a:vip:1487505119661785260>",
        description=(
            "Welcome to **Grindora**, the premium standard for Old School RuneScape account progression. "
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
        name="🛡️ WHY CHOOSE Grindora",
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
    
    view = VerifyView()
    await ctx.send(embed=embed, view=view)
    
    try:
        await ctx.message.delete()
    except:
        pass

# ==============================
# أمر !pay - نظام الدفع (نفس الكود القديم)
# ==============================
@bot.command(name="pay")
@has_allowed_role()
async def pay_command(ctx):
    """Send payment methods embed with select menu (لأصحاب الرتب المحددة)"""
    
    embed = discord.Embed(
        title="💳 Grindora — PAYMENT METHODS",
        description="We currently accept the following:",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="",
        value=f"{config.PAYMENT_ADDRESSES['OSRS GP'].get('emoji', '⚔️')} **OSRS GP** - Contact staff for details",
        inline=False
    )
    
    embed.add_field(
        name="🪙 Crypto",
        value="• BTC / LTC / USDT (TRC20) / ETH (ERC20) / Binance",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Important",
        value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
        inline=False
    )
    
    embed.set_footer(text="Select a payment method from the menu below to see details")
    
    view = PaymentView()
    await ctx.send(embed=embed, view=view)

# ==========================================
# أوامر الفيدباك: !feedback , !f , !F
# ==========================================
@bot.command(name="feedback", aliases=["f", "F"])
async def feedback_command(ctx):
    """!feedback or !f or !F - Start review submission"""
    
    full_description = """**Your order has been successfully delivered!** :white_check_mark:

🔒 **Account Safety Reminder:**
• Change your account password immediately
• Log out of all active Jagex Launcher sessions

For full protection, we highly recommend completing these steps now.

---

💬 **Need more support or want another service?**
We're always here to help you maximize your account's potential.

🛒 **Explore all services:** <#1487243724865011822>
🎫 **Start a new order:** <#1487244035516006551>"""
    
    embed = discord.Embed(
        title="💎 Order Completed — Grindora Services 💎",
        description=full_description,
        color=discord.Color.from_rgb(184, 92, 26)
    )
    
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1487311776256098414/1489130417838882916/HHHHHHHHHHHHHHHHHHHHHH.gif")
    
    view = MainFeedbackView(ctx.channel)
    await ctx.send(embed=embed, view=view)

# ==========================================
# أوامر إعدادات الفيدباك (Admin)
# ==========================================
@bot.command(name="roleworker")
async def set_worker_role(ctx, role_id: str):
    """!roleworker <role_id> - Set worker role"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions.")
        return
    
    try:
        role_id_int = int(role_id)
        role = ctx.guild.get_role(role_id_int)
        
        if role:
            config.WORKER_ROLE_ID = role_id_int
            save_settings()
            
            embed = discord.Embed(
                title="✅ Worker Role Set",
                description=f"Worker role set to: {role.mention} (ID: `{role_id_int}`)",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Role with ID `{role_id}` not found.")
    except ValueError:
        await ctx.send("❌ Please provide a valid numeric role ID.")

@bot.command(name="setreviewchannel")
async def set_review_channel(ctx, channel_id: str = None):
    """!setreviewchannel <channel_id> - Set review channel"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions.")
        return
    
    if channel_id is None:
        channel = ctx.channel
        config.FEEDBACK_CHANNEL_ID = channel.id
        save_settings()
        
        embed = discord.Embed(
            title="✅ Review Channel Set",
            description=f"Review channel set to: {channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        channel_id_int = int(channel_id)
        channel = ctx.guild.get_channel(channel_id_int)
        
        if channel and isinstance(channel, discord.TextChannel):
            config.FEEDBACK_CHANNEL_ID = channel_id_int
            save_settings()
            
            embed = discord.Embed(
                title="✅ Review Channel Set",
                description=f"Review channel set to: {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Channel with ID `{channel_id}` not found.")
    except ValueError:
        await ctx.send("❌ Please provide a valid numeric channel ID.")

@bot.command(name="reviewsettings")
async def show_settings(ctx):
    """!reviewsettings - Show current settings"""
    embed = discord.Embed(title="⚙️ Review System Settings", color=discord.Color.blue())
    
    if config.WORKER_ROLE_ID:
        role = ctx.guild.get_role(config.WORKER_ROLE_ID)
        embed.add_field(name="Worker Role", value=role.mention if role else f"ID: {config.WORKER_ROLE_ID}", inline=False)
    else:
        embed.add_field(name="Worker Role", value="❌ Not set", inline=False)
    
    if config.FEEDBACK_CHANNEL_ID:
        channel = ctx.guild.get_channel(config.FEEDBACK_CHANNEL_ID)
        embed.add_field(name="Review Channel", value=channel.mention if channel else f"ID: {config.FEEDBACK_CHANNEL_ID}", inline=False)
    else:
        embed.add_field(name="Review Channel", value="❌ Not set", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="say")
async def say_message(ctx, channel_id: str = None):
    """!say <channel_id> - Send feedback panel (Admin only)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions.")
        return
    
    if channel_id:
        try:
            channel_id_int = int(channel_id)
            target_channel = ctx.guild.get_channel(channel_id_int)
            if not target_channel:
                await ctx.send(f"❌ Channel not found.")
                return
        except ValueError:
            await ctx.send("❌ Please provide a valid channel ID.")
            return
    else:
        target_channel = ctx.channel
    
    full_description = """**Your order has been successfully delivered!** :white_check_mark:

🔒 **Account Safety Reminder:**
• Change your account password immediately
• Log out of all active Jagex Launcher sessions

---

💬 **Need more support or want another service?**
We're always here to help you.

🛒 **Explore all services:** <#1487243724865011822>
🎫 **Start a new order:** <#1487244035516006551>"""
    
    embed = discord.Embed(
        title="💎 Order Completed — Grindora Services 💎",
        description=full_description,
        color=discord.Color.from_rgb(184, 92, 26)
    )
    
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1487311776256098414/1489130417838882916/HHHHHHHHHHHHHHHHHHHHHH.gif")
    
    view = MainFeedbackView(target_channel)
    await target_channel.send(embed=embed, view=view)
    await ctx.send(f"✅ Message sent to {target_channel.mention}")

@bot.command(name="commands", aliases=["menu", "cmds", "helpme"])
async def commands_help(ctx):
    """!commands - Show all available commands"""
    
    embed = discord.Embed(
        title="📋 Grindora Bot - Help Menu",
        description="Here are all available commands.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="✅ **Verification**",
        value="`!rules` - Send verify panel (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name="💳 **Payment**",
        value="`!pay` - Show payment methods",
        inline=False
    )
    
    embed.add_field(
        name="📝 **Feedback**",
        value="`!feedback` or `!f` or `!F` - Start review submission",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **Admin Commands**",
        value=(
            "`!roleworker <id>` - Set worker role\n"
            "`!setreviewchannel <id>` - Set review channel\n"
            "`!reviewsettings` - Show settings\n"
            "`!say <channel_id>` - Send feedback panel\n"
            "`!commands` - Show this menu"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed)

# ==========================================
# EVENT: READY
# ==========================================
@bot.event
async def on_ready():
    load_settings()
    print(f"✅ Grindora Bot is online as {bot.user}")
    print(f"📊 Connected to {len(bot.guilds)} servers")
    print("------")
    print("🎯 Commands loaded:")
    print("   • !rules - Verify panel")
    print("   • !pay - Payment methods")
    print("   • !feedback / !f / !F - Review system")
    print("   • !roleworker - Set worker role")
    print("   • !setreviewchannel - Set review channel")
    print("   • !reviewsettings - Show settings")
    print("   • !say - Send feedback panel")
    print("   • !commands - Show all commands")

# ==========================================
# RUN THE BOT
# ==========================================
if __name__ == "__main__":
    if not config.TOKEN:
        print("❌ Error: DISCORD_TOKEN not found!")
        print("Please add DISCORD_TOKEN in Environment Variables")
    else:
        print("🚀 Starting Grindora Bot...")
        bot.run(config.TOKEN)