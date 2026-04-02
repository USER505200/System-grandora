# cogs/feedback.py
import discord
from discord import app_commands
from discord.ext import commands
import config
import json
import os
from datetime import datetime

# ==========================================
# ملف لحفظ الإعدادات
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
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                config.WORKER_ROLE_ID = settings.get("worker_role_id")
                config.FEEDBACK_CHANNEL_ID = settings.get("feedback_channel_id")
        except:
            pass

# ==========================================
# HELPER FUNCTIONS
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
        # جلب الـ Workers الموجودين في الشانل (للتحقق فقط)
        workers_in_channel = get_workers_in_channel(self.channel)
        
        # التحقق من وجود Workers في التكت
        if not workers_in_channel:
            await interaction.response.send_message(
                "❌ No workers found in this channel/ticket. Make sure you have set the correct worker role and there are workers in this channel.",
                ephemeral=True
            )
            return
        
        # إنشاء الإمبيد
        embed = discord.Embed(
            title="⭐ Feedback Received ⭐",
            color=discord.Color.from_rgb(184, 92, 26)
        )
        
        # إضافة الصورة (thumbnail) في امبيد التقييم
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1487311776256098414/1489130417838882916/HHHHHHHHHHHHHHHHHHHHHH.gif")
        
        # إضافة الـ Review داخل backticks
        review_text = f"```{self.description.value}```"
        embed.add_field(name="📝 Review", value=review_text, inline=False)
        
        # إضافة اسم العميل مع النجوم تحته
        if self.customer_name.value and self.customer_name.value.strip():
            customer_value = f"**{self.customer_name.value}**\n\n⭐⭐⭐⭐⭐"
        else:
            customer_value = f"*hidden*\n\n⭐⭐⭐⭐⭐"
        
        embed.add_field(name="👤 Customer", value=customer_value, inline=True)
        
        # إضافة الوقت
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        embed.set_footer(text=f"Submitted • {current_time}")
        
        # إرسال إلى شانل التقييمات
        if config.FEEDBACK_CHANNEL_ID:
            feedback_channel = interaction.guild.get_channel(config.FEEDBACK_CHANNEL_ID)
            if feedback_channel:
                # إرسال الإمبيد مع الصورة
                await feedback_channel.send(embed=embed)
                
                # إضافة رسالة تأكيد للمستخدم مع صورة
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
# BUTTON VIEW TO OPEN MODAL
# ==========================================
class FeedbackButton(discord.ui.View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="📝 Submit Review", style=discord.ButtonStyle.primary, custom_id="feedback_button", emoji="⭐")
    async def feedback_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FeedbackModal(self.channel))

# ==========================================
# MAIN VIEW WITH BOTH BUTTONS
# ==========================================
class MainFeedbackView(discord.ui.View):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(timeout=None)
        # Add the feedback button
        self.add_item(FeedbackButton(channel).children[0])
        # Add the Sythe vouches button as a link button
        sythe_button = discord.ui.Button(
            label="Sythe Vouches",
            style=discord.ButtonStyle.link,
            url="https://www.sythe.org/threads/prime07-official-vouches/",
            emoji="📜"
        )
        self.add_item(sythe_button)

# ==========================================
# FEEDBACK COG
# ==========================================
class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # تحميل الإعدادات المحفوظة عند بدء التشغيل
        load_settings()

    # ==========================================
    # SLASH COMMAND: /feedback
    # ==========================================
    @app_commands.command(name="feedback", description="Start a review submission")
    async def slash_feedback(self, interaction: discord.Interaction):
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
    # PREFIX COMMAND: !feedback
    # ==========================================
    @commands.command(name="feedback", aliases=["f"])
    async def prefix_feedback(self, ctx):
        """!feedback, !f command to start review."""
        
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
    # COMMAND: !commands - عرض كل الأوامر
    # ==========================================
    @commands.command(name="commands", aliases=["menu", "cmds", "helpme"])
    async def commands_help(self, ctx):
        """!commands - عرض جميع الأوامر المتاحة"""
        
        embed = discord.Embed(
            title="📋 Review Bot - Help Menu",
            description="Here are all available commands for the review system.",
            color=discord.Color.blue()
        )
        
        # أوامر التقييم
        embed.add_field(
            name="📝 **Review Commands**",
            value=(
                "`/feedback` - Start review (slash command)\n"
                "`!feedback` - Start review\n"
                "`!f` - Shortcut for review"
            ),
            inline=False
        )
        
        # أوامر الإعدادات (للأدمن)
        embed.add_field(
            name="⚙️ **Admin Commands**",
            value=(
                "`!roleworker <id>` - Set worker role by ID\n"
                "`!setreviewchannel <id>` - Set review channel (leave empty for current channel)\n"
                "`!reviewsettings` - Show current settings\n"
                "`!commands` - Show this help menu"
            ),
            inline=False
        )
        
        # الحالة الحالية
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
    # COMMAND: SET WORKER ROLE
    # ==========================================
    @commands.command(name="roleworker")
    async def set_worker_role(self, ctx, role_id: str):
        """!roleworker <role_id> - لتحديد رتبة Worker باستخدام ID"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
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
                await ctx.send(f"❌ Role with ID `{role_id}` not found. Please check the ID and try again.")
        except ValueError:
            await ctx.send("❌ Please provide a valid numeric role ID.")

    # ==========================================
    # COMMAND: SET REVIEW CHANNEL
    # ==========================================
    @commands.command(name="setreviewchannel")
    async def set_review_channel(self, ctx, channel_id: str = None):
        """!setreviewchannel <channel_id> - لتحديد شانل التقييمات"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
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
    # COMMAND: SHOW SETTINGS
    # ==========================================
    @commands.command(name="reviewsettings")
    async def show_settings(self, ctx):
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
    # COMMAND: SAY (لإرسال رسالة الترحيب)
    # ==========================================
    @commands.command(name="say")
    async def say_message(self, ctx, channel_id: str = None):
        """!say <channel_id> - إرسال رسالة الترحيب مع الأزرار (للاستخدام مرة واحدة)"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
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
# SETUP FUNCTION
# ==========================================
async def setup(bot):
    await bot.add_cog(Feedback(bot))
    print("✅ Feedback cog loaded successfully!")