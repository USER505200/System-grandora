# bot.py
import discord
from discord.ext import commands
from discord import ButtonStyle, ui
import config

# إعدادات البوت
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


# ==============================
# دالة التحقق من الصلاحية لـ !pay
# ==============================

def has_allowed_role():
    """التحقق من أن العضو عنده واحدة من الرتب المسموحة"""
    async def predicate(ctx):
        # لو أدمن، يسمح له
        if ctx.author.guild_permissions.administrator:
            return True
        
        # التحقق من الرتب
        for role_id in config.ALLOWED_PAY_ROLES:
            role = ctx.guild.get_role(role_id)
            if role and role in ctx.author.roles:
                return True
        return False
    return commands.check(predicate)


# ==============================
# كلاس القائمة المنسدلة للدفع (Select Menu)
# ==============================

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
        """When user selects a payment method"""
        selected = self.values[0]
        payment_data = config.PAYMENT_ADDRESSES[selected]
        
        # Create embed with payment details
        embed = discord.Embed(
            title=f"{payment_data.get('emoji', '💰')} {selected} - Payment Details",
            description=payment_data["details"],
            color=discord.Color.gold()
        )
        
        # Add important information
        embed.add_field(
            name="⚠️ IMPORTANT",
            value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
            inline=False
        )
        
        # Send ephemeral message (only visible to the user)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PaymentView(ui.View):
    """View containing the payment select menu"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentSelect())


# ==============================
# حدث تشغيل البوت
# ==============================

@bot.event
async def on_ready():
    """عند تشغيل البوت"""
    print(f"✅ Grindora Bot is online as {bot.user}")
    print(f"📊 Connected to {len(bot.guilds)} servers")
    print(f"📝 Command prefix: !")
    print(f"🎯 Commands loaded: {[cmd.name for cmd in bot.commands]}")


# ==============================
# أمر !rules - نظام التحقق
# ==============================

@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def send_rules(ctx):
    """إرسال Embed التحقق (للأدمن فقط)"""
    
    # روابط الصور
    LEFT_SMALL_IMAGE_URL = "https://cdn.discordapp.com/attachments/1488235109650796786/1495178588738293982/Comp_1.gif?ex=69f12a92&is=69efd912&hm=83176a70a6937c8b291dcb266a041efc00dfa4f3d885ca43acb64414f2773a74&"
    RIGHT_TOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1488235109650796786/1495178589958836346/Untitled-1.gif?ex=69f12a92&is=69efd912&hm=dedca0c215b363bd42b2d8ca0ec0b998b7349d99062e5f69f99c0a2a3d0dc0ad&"
    BOTTOM_IMAGE_URL = "https://cdn.discordapp.com/attachments/1488235109650796786/1495178588738293982/Comp_1.gif?ex=69f12a92&is=69efd912&hm=83176a70a6937c8b291dcb266a041efc00dfa4f3d885ca43acb64414f2773a74&"
    
    # إنشاء Embed باللون المطلوب #dd7222
    embed = discord.Embed(
        color=0xdd7222,
        description="────────**We do the Grind You keep the Chill**────────"
    )

    # ✅ صورة صغيرة جنب كلمة WELCOME فوق خالص
    embed.set_author(
        name="WELCOME TO GRINDORA — PREMIER OSRS SERVICES",
        icon_url=LEFT_SMALL_IMAGE_URL
    )

    # ✅ الصورة الصغيرة على اليمين (thumbnail)
    embed.set_thumbnail(url=LEFT_SMALL_IMAGE_URL)

    # ✅ الصورة الكبيرة في الأعلى
    embed.set_image(url=RIGHT_TOP_IMAGE_URL)
    
    # ✅✅✅ إضافة الصورة اللي كانت تحت في الأعلى (نفس الصورة)
    embed.add_field(
        name="\u200b",
        value=f"-# [‎ ]({BOTTOM_IMAGE_URL})",
        inline=False
    )
    
    # ACCESS TEXT
    embed.add_field(
        name="**ACCESS**",
        value="\u200b",
        inline=False
    )
    
    # GRINDORA SERVICES & SKILLING
    embed.add_field(
        name="**GRINDORA SERVICES**",
        value="**SKILLING**",
        inline=False
    )
    
    # Grindora – Premier OSRS Services
    embed.add_field(
        name="**Grindora – Premier OSRS Services**",
        value="\u200b",
        inline=False
    )
    
    # خط فاصل
    embed.add_field(name="──────────────────────────────────", value="\u200b", inline=False)
    
    # WHAT WE OFFER
    embed.add_field(
        name="⚔️ WHAT WE OFFER",
        value=(
            "• **Skilling:** 1–99 in all skills (including Sailing prep).\n"
            "• **Questing:** Full Quest Cape & Elite Diaries.\n"
            "• **PvM & Raids:** ToB (HMT), CoX (CM) / Megascale, & ToA.\n"
            "• **Elite Unlocks:** Inferno, Quivers, Combat Achievements, & Blood Torva."
        ),
        inline=False
    )
    
    embed.add_field(name="──────────────────────────────────", value="\u200b", inline=False)
    
    # WHY CHOOSE GRINDORA
    embed.add_field(
        name="🛡️ WHY CHOOSE GRINDORA?",
        value=(
            "**✅ TRUSTED** — $300+ Sythe Donor & Multi-Billion GP Deposits.\n"
            "**✅ INTEGRITY** — 100% Hand-played. No bots. No scripts.\n"
            "**✅ SPEED** — Strict, deadline-driven scheduling.\n"
            "**✅ SUPPORT** — 24/7 ticket oversight and daily progress."
        ),
        inline=False
    )
    
    embed.add_field(name="──────────────────────────────────", value="\u200b", inline=False)
    
    # GET STARTED
    embed.add_field(
        name="📜 GET STARTED",
        value=(
            f"1. Read our **Safety Protocols** in <#{config.CH_RULES}>\n"
            f"2. Browse our rates in <#{config.CH_RATES}>\n"
            f"3. Open a ticket in <#{config.CH_TICKETS}> to begin."
        ),
        inline=False
    )
    
    embed.add_field(name="──────────────────────────────────", value="\u200b", inline=False)
    
    # SECURITY ADVISORY
    embed.add_field(
        name="⚠️ SECURITY ADVISORY",
        value="*Grindora staff will **NEVER** DM you first or use external middlemen. Always verify roles before sending payment.*",
        inline=False
    )
    
    embed.add_field(name="──────────────────────────────────", value="\u200b", inline=False)
    
    # VERIFY BUTTON TEXT
    embed.add_field(
        name="👇 PRESS THE BUTTON BELOW TO GAIN FULL ACCESS",
        value="\u200b",
        inline=False
    )
    
    # ✅✅✅ إضافة نفس الصورة تحت خالص في الفوتر
    embed.set_footer(text="Grindora — Premier OSRS Services", icon_url=BOTTOM_IMAGE_URL)
    
    # إنشاء زر التحقق
    verify_button = discord.ui.Button(
        custom_id="Grindora_verify",
        label="✅ Verify",
        style=ButtonStyle.success
    )
    
    view = discord.ui.View()
    view.add_item(verify_button)
    
    await ctx.send(embed=embed, view=view)
    
    try:
        await ctx.message.delete()
    except:
        pass


# ==============================
# أمر !vouch - نظام الـ Vouches
# ==============================

@bot.command(name="vouch")
@commands.has_permissions(administrator=True)
async def send_vouch(ctx):
    """إرسال Embed الـ Vouch (للأدمن فقط)"""
    
    # روابط الصور
    LEFT_IMAGE_URL = "https://media.discordapp.net/attachments/1489083566800240752/1489337660152615013/Comp_1.gif?ex=69f102c8&is=69efb148&hm=35640dd034c88a7775d1bbfdd240e6ca02ba5a17de9b160df4d46b2a2ac948b5&width=150&height=150&"
    RIGHT_IMAGE_URL = "https://media.discordapp.net/attachments/1489083566800240752/1489337660152615013/Comp_1.gif?ex=69f102c8&is=69efb148&hm=35640dd034c88a7775d1bbfdd240e6ca02ba5a17de9b160df4d46b2a2ac948b5&"
    BOTTOM_IMAGE_URL = "https://media.discordapp.net/attachments/1489083566800240752/1489229189398921378/Untitled-1.gif?ex=69f14683&is=69eff503&hm=8d0d6cc84d1047359e9fa2ef9dce1d1fa06bcf9f6e458bca32673c7ca8d7a16f&width=813&height=113&"
    
    # Sythe Vouch Link
    SYTHE_VOUCH_LINK = "https://www.sythe.org/threads/grindora-services"
    
    # إنشاء Embed
    embed = discord.Embed(
        color=0xdd7222,
        title="# Grindora — Sythe Vouch Thread",
        description=(
            "If we've completed a service for you, please leave your honest vouch on our official Sythe thread below:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    )
    
    # وضع الصورة على الشمال (thumbnail)
    embed.set_thumbnail(url=LEFT_IMAGE_URL)
    
    # وضع الصورة في الأعلى
    embed.set_image(url=RIGHT_IMAGE_URL)
    
    # Vouch Message Field
    embed.add_field(
        name="📝 **Already vouched on Sythe?**",
        value=(
            "Feel free to drop a copy here as well — we truly appreciate your support ❤️\n\n"
            "**Bonus:** Receive +3% off your next order (stacks with Grindora Ranks)"
        ),
        inline=False
    )
    
    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
    
    # Thank you message
    embed.add_field(
        name="🙏 Thank you for choosing Grindora Services!",
        value="\u200b",
        inline=False
    )
    
    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", value="\u200b", inline=False)
    
    # Footer مع الصورة
    embed.set_footer(text="Sythe Vouch Link", icon_url=BOTTOM_IMAGE_URL)
    
    # إنشاء الأزرار
    view = discord.ui.View()
    
    # زر PAYMENT METHODS
    payment_button = discord.ui.Button(
        label="💰 PAYMENT METHODS",
        style=ButtonStyle.primary,
        custom_id="vouch_payment_button"
    )
    
    # زر GRINDORA SERVICES
    services_button = discord.ui.Button(
        label="⚔️ GRINDORA SERVICES",
        style=ButtonStyle.success,
        custom_id="vouch_services_button"
    )
    
    # زر Sythe Vouch Link
    sythe_button = discord.ui.Button(
        label="📝 Sythe Vouch Link",
        style=ButtonStyle.link,
        url=SYTHE_VOUCH_LINK
    )
    
    view.add_item(payment_button)
    view.add_item(services_button)
    view.add_item(sythe_button)
    
    await ctx.send(embed=embed, view=view)
    
    try:
        await ctx.message.delete()
    except:
        pass


# ==============================
# أمر !pay - نظام الدفع بالقائمة المنسدلة (Select Menu)
# ==============================

@bot.command(name="p")
@has_allowed_role()
async def pay_command(ctx):
    """Send payment methods embed with select menu (for allowed roles)"""
    
    # Image URLs
    TOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1489497861350494339/1489723944582910002/word_1.gif?ex=69d1750a&is=69d0238a&hm=e9861e30bd5918e66c2d324e9bf21104bd21d8c18de12fb6cfa00681ce6f51e1&"
    BOTTOM_IMAGE_URL = "https://cdn.discordapp.com/attachments/1489497861350494339/1489730355316392088/Untitled-1.gif?ex=69d17b02&is=69d02982&hm=91bba9f3cb622da72a3555f8a9ed89383f533898b0172e271605523595e1ce54&"
    
    # Main embed
    embed = discord.Embed(
        title="💳 Grindora — PAYMENT METHODS",
        description="We currently accept the following:",
        color=discord.Color.gold()
    )
    
    # Top right image (thumbnail)
    embed.set_thumbnail(url=TOP_IMAGE_URL)
    
    # OSRS GP Field
    embed.add_field(
        name="",
        value=f"⚔️ **OSRS GP** - Contact staff for details",
        inline=False
    )
    
    # Crypto Field
    embed.add_field(
        name="🪙 Crypto",
        value="• BTC / LTC / USDT (TRC20) / ETH (ERC20) / Binance",
        inline=False
    )
    
    # Important Field
    embed.add_field(
        name="⚠️ Important",
        value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
        inline=False
    )
    
    # Bottom image
    embed.set_image(url=BOTTOM_IMAGE_URL)
    
    # Footer
    embed.set_footer(text="Select a payment method from the menu below to see details")
    
    # Send embed with select menu
    view = PaymentView()
    await ctx.send(embed=embed, view=view)


# ==============================
# Interaction Handler
# ==============================

@bot.event
async def on_interaction(interaction):
    """Handle all interactions (buttons and select menus)"""
    
    # Check if interaction is a component interaction
    if not interaction.type == discord.InteractionType.component:
        return
    
    if not hasattr(interaction, 'data') or not interaction.data:
        return
    
    custom_id = interaction.data.get("custom_id")
    
    # ===== Verify Button =====
    if custom_id == "Grindora_verify":
        await interaction.response.defer(ephemeral=True)
        
        member = interaction.user
        guild = interaction.guild
        
        if not guild:
            return await interaction.followup.send("❌ Error: Could not find server.", ephemeral=True)
        
        role = guild.get_role(int(config.MEMBER_ROLE_ID))
        
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
                f"✅ **Welcome to Grindora, {member.display_name}!**\n"
                f"You have been granted the **{role.name}** role.\n\n"
                f"📖 Check <#{config.CH_RULES}> for safety protocols.\n"
                f"💰 Browse basket here <#{config.CH_RATES}>.\n"
                f"🎟️ Open a ticket in <#{config.CH_TICKETS}> when ready!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error adding role: {e}")
            await interaction.followup.send(
                "❌ Failed to add the role. Make sure the bot's role is **above** the Member role in the server settings.",
                ephemeral=True
            )
    
    # ===== Vouch Buttons =====
    elif custom_id == "vouch_payment_button":
        await interaction.response.send_message(
            f"💰 **Payment Methods**\nPlease visit <#{config.CH_RATES}> for our payment methods and rates!\n\nYou can also use the `!p` command in any channel.",
            ephemeral=True
        )
    
    elif custom_id == "vouch_services_button":
        await interaction.response.send_message(
            f"⚔️ **Grindora Services**\nCheck out <#{config.CH_RULES}> for our complete list of services!\n\nWe offer Skilling, Questing, PvM, Raids, and Elite Unlocks.",
            ephemeral=True
        )


# ==============================
# تشغيل البوت
# ==============================

if __name__ == "__main__":
    if not config.TOKEN:
        print("❌ Error: DISCORD_TOKEN not found!")
        print("Please add DISCORD_TOKEN in Railway Environment Variables")
    else:
        print("🚀 Starting Grindora Bot...")
        bot.run(config.TOKEN)