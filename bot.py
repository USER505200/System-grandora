# bot.py
import discord
from discord import app_commands
from discord.ext import commands
from discord import ButtonStyle, ui
import config
import json
import os
from datetime import datetime

# ==========================================
# BOT SETUP
# ==========================================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class Prime07Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.synced = False

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=config.GUILD_ID))
        print("✅ Commands synced.")

bot = Prime07Bot()

# ==========================================
# ملف لحفظ إعدادات التقييم
# ==========================================
SETTINGS_FILE = "settings.json"

def save_settings():
    """حفظ الإعدادات في ملف"""
    settings = {
        "worker_role_id": config.WORKER_ROLE_ID,
        "feedback_channel_id": config.FEEDBACK_CHANNEL_ID
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_settings():
    """تحميل الإعدادات من الملف"""
    global worker_role_id, feedback_channel_id
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                config.WORKER_ROLE_ID = settings.get("worker_role_id")
                config.FEEDBACK_CHANNEL_ID = settings.get("feedback_channel_id")
        except:
            pass


# ==========================================
# دالة التحقق من الصلاحية لـ !pay
# ==========================================

def has_allowed_role():
    """التحقق من أن العضو عنده واحدة من الرتب المسموحة"""
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
# HELPER FUNCTIONS للتقييم
# ==========================================

def get_workers_in_channel(channel: discord.TextChannel):
    """جلب كل الأعضاء اللي معاهم رتبة Worker في الشانل المحدد"""
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
                "❌ No workers found in this channel/ticket. Make sure you have set the correct worker role and there are workers in this channel.",
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
                await interaction.response.send_message("❌ Feedback channel not found. Please contact an admin.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Feedback channel not set. Use `!setreviewchannel` to set it first.", ephemeral=True)


# ==========================================
# BUTTON VIEW FOR FEEDBACK
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
# كلاس القائمة المنسدلة للدفع (Select Menu)
# ==========================================

class PaymentSelect(ui.Select):
    """Dropdown menu for selecting payment method"""
    
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
# EVENT: ON_READY
# ==========================================

@bot.event
async def on_ready():
    load_settings()
    
    print(f"✅ Prime07 Bot is online as {bot.user}")
    print(f"📊 Connected to {len(bot.guilds)} servers")
    print(f"📝 Command prefix: !")
    print(f"🎯 Commands loaded: {[cmd.name for cmd in bot.commands]}")
    print(f"👥 Worker Role ID: {config.WORKER_ROLE_ID}")
    print(f"📢 Review Channel ID: {config.FEEDBACK_CHANNEL_ID}")
    print("------")


# ==========================================
# COMMAND: !rules (نظام التحقق)
# ==========================================

@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def send_rules(ctx):
    """إرسال Embed التحقق (للأدمن فقط)"""
    
    embed = discord.Embed(
        color=0x2b2d31,
        title="<a:vip:1487505119661785260>  PRIME07 — PREMIER OSRS SERVICES  <a:vip:1487505119661785260>",
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
        value="**Prime07 staff will NEVER DM you first or use external middlemen.\nAlways verify roles before sending GP/payment.**",
        inline=False
    )
    
    embed.add_field(name="━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
    
    embed.add_field(
        name="✅ VERIFY",
        value="Press the button below to accept the rules and gain access to the server as a **Member**.",
        inline=False
    )
    
    embed.set_footer(text="Prime07 — Premier OSRS Services")
    
    verify_button = discord.ui.Button(
        custom_id="prime07_verify",
        label="✅ Verify — I Accept the Rules",
        style=ButtonStyle.success
    )
    
    view = discord.ui.View()
    view.add_item(verify_button)
    
    await ctx.send(embed=embed, view=view)
    
    try:
        await ctx.message.delete()
    except:
        pass


# ==========================================
# COMMAND: !pay (نظام الدفع)
# ==========================================

@bot.command(name="pay")
@has_allowed_role()
async def pay_command(ctx):
    """Send payment methods embed with select menu"""
    
    embed = discord.Embed(
        title="💳 PRIME07 — PAYMENT METHODS",
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
# COMMAND: /feedback (سلاش كوماند)
# ==========================================

@bot.tree.command(name="feedback", description="Start a review submission")
async def slash_feedback(interaction: discord.Interaction):
    """Sends an embed with a button to open the review modal."""
    
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
    
    view = MainFeedbackView(interaction.channel)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


# ==========================================
# COMMAND: !feedback, !f
# ==========================================

@bot.command(name="feedback", aliases=["f", "F"])
async def prefix_feedback(ctx):
    """!feedback, !f, or F command to start review."""
    
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
# COMMAND: !commands (عرض كل الأوامر)
# ==========================================

@bot.command(name="commands", aliases=["menu", "cmds", "helpme"])
async def commands_help(ctx):
    """!commands - عرض جميع الأوامر المتاحة"""
    
    embed = discord.Embed(
        title="📋 Prime07 Bot - Help Menu",
        description="Here are all available commands.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📝 **Review Commands**",
        value=(
            "`/feedback` - Start review (slash command)\n"
            "`!feedback` - Start review\n"
            "`!f` - Shortcut for review\n"
            "`F` - Shortcut for review (just type F)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="💰 **Payment Commands**",
        value=(
            "`!pay` - Show payment methods (Authorized roles only)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ **Admin Commands**",
        value=(
            "`!rules` - Send verification embed\n"
            "`!roleworker <id>` - Set worker role by ID\n"
            "`!setreviewchannel <id>` - Set review channel\n"
            "`!reviewsettings` - Show current settings\n"
            "`!say <channel_id>` - Send welcome message\n"
            "`!commands` - Show this help menu"
        ),
        inline=False
    )
    
    worker_status = "❌ Not set"
    if config.WORKER_ROLE_ID:
        role = ctx.guild.get_role(config.WORKER_ROLE_ID)
        if role:
            worker_status = f"{role.mention} (ID: `{config.WORKER_ROLE_ID}`)"
        else:
            worker_status = f"ID: `{config.WORKER_ROLE_ID}` (Role not found)"
    
    channel_status = "❌ Not set"
    if config.FEEDBACK_CHANNEL_ID:
        channel = ctx.guild.get_channel(config.FEEDBACK_CHANNEL_ID)
        if channel:
            channel_status = f"{channel.mention} (ID: `{config.FEEDBACK_CHANNEL_ID}`)"
        else:
            channel_status = f"ID: `{config.FEEDBACK_CHANNEL_ID}` (Channel not found)"
    
    embed.add_field(
        name="🔧 **Current Settings**",
        value=(
            f"**Worker Role:** {worker_status}\n"
            f"**Review Channel:** {channel_status}"
        ),
        inline=False
    )
    
    embed.set_footer(text="Use !reviewsettings for detailed settings")
    await ctx.send(embed=embed)


# ==========================================
# COMMAND: !roleworker
# ==========================================

@bot.command(name="roleworker")
async def set_worker_role(ctx, role_id: str):
    """!roleworker <role_id> - لتحديد رتبة Worker"""
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
                description=f"Worker role has been set to: {role.mention} (ID: `{role_id_int}`)",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Role with ID `{role_id}` not found.")
    except ValueError:
        await ctx.send("❌ Please provide a valid numeric role ID.")


# ==========================================
# COMMAND: !setreviewchannel
# ==========================================

@bot.command(name="setreviewchannel")
async def set_review_channel(ctx, channel_id: str = None):
    """!setreviewchannel <channel_id> - لتحديد شانل التقييمات"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions.")
        return
    
    if channel_id is None:
        channel = ctx.channel
        config.FEEDBACK_CHANNEL_ID = channel.id
        save_settings()
        
        embed = discord.Embed(
            title="✅ Review Channel Set",
            description=f"Review channel has been set to: {channel.mention} (ID: `{channel.id}`)",
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
                description=f"Review channel has been set to: {channel.mention} (ID: `{channel_id_int}`)",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Channel with ID `{channel_id}` not found or is not a text channel.")
    except ValueError:
        await ctx.send("❌ Please provide a valid numeric channel ID.")


# ==========================================
# COMMAND: !reviewsettings
# ==========================================

@bot.command(name="reviewsettings")
async def show_settings(ctx):
    """!reviewsettings - عرض الإعدادات الحالية"""
    embed = discord.Embed(
        title="⚙️ Review System Settings",
        color=discord.Color.blue()
    )
    
    if config.WORKER_ROLE_ID:
        role = ctx.guild.get_role(config.WORKER_ROLE_ID)
        if role:
            embed.add_field(name="👥 Worker Role", value=f"{role.mention} (ID: `{config.WORKER_ROLE_ID}`)", inline=False)
        else:
            embed.add_field(name="👥 Worker Role", value=f"ID: `{config.WORKER_ROLE_ID}` (Role not found)", inline=False)
    else:
        embed.add_field(name="👥 Worker Role", value="❌ Not set", inline=False)
    
    if config.FEEDBACK_CHANNEL_ID:
        channel = ctx.guild.get_channel(config.FEEDBACK_CHANNEL_ID)
        if channel:
            embed.add_field(name="📢 Review Channel", value=f"{channel.mention} (ID: `{config.FEEDBACK_CHANNEL_ID}`)", inline=False)
        else:
            embed.add_field(name="📢 Review Channel", value=f"ID: `{config.FEEDBACK_CHANNEL_ID}` (Channel not found)", inline=False)
    else:
        embed.add_field(name="📢 Review Channel", value="❌ Not set", inline=False)
    
    embed.set_footer(text="Use !roleworker <id> and !setreviewchannel <id> to set these")
    await ctx.send(embed=embed)


# ==========================================
# COMMAND: !say
# ==========================================

@bot.command(name="say")
async def say_message(ctx, channel_id: str = None):
    """!say <channel_id> - إرسال رسالة الترحيب مع الأزرار"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions.")
        return
    
    if channel_id:
        try:
            channel_id_int = int(channel_id)
            target_channel = ctx.guild.get_channel(channel_id_int)
            if not target_channel:
                await ctx.send(f"❌ Channel with ID `{channel_id}` not found.")
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
    
    view = MainFeedbackView(target_channel)
    await target_channel.send(embed=embed, view=view)
    await ctx.send(f"✅ Message sent to {target_channel.mention}")


# ==========================================
# EVENT: INTERACTION (لزر التحقق)
# ==========================================

@bot.event
async def on_interaction(interaction):
    """معالجة جميع التفاعلات"""
    
    if not interaction.type == discord.InteractionType.component:
        return
    
    if not hasattr(interaction, 'data') or not interaction.data:
        return
    
    custom_id = interaction.data.get("custom_id")
    
    # زر التحقق من !rules
    if custom_id == "prime07_verify":
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.user
        guild = interaction.guild
        role = guild.get_role(config.MEMBER_ROLE_ID)
        
        if not role:
            return await interaction.followup.send(
                "❌ Member role not found! Please contact an administrator.",
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
                "❌ Failed to add the role. Make sure the bot's role is **above** the Member role.",
                ephemeral=True
            )


# ==========================================
# ERROR HANDLER
# ==========================================

@bot.event
async def on_command_error(ctx, error):
    """معالجة الأخطاء"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Available commands: `!commands`, `!rules`, `!pay`, `!feedback`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need **Administrator** permissions to use this command.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use `!pay`.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")


# ==========================================
# RUN THE BOT
# ==========================================

if __name__ == "__main__":
    if not config.TOKEN:
        print("❌ Error: DISCORD_TOKEN not found!")
        print("Please add DISCORD_TOKEN in Railway Environment Variables")
    else:
        print("🚀 Starting Prime07 Bot...")
        bot.run(config.TOKEN)