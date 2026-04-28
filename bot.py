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
# أمر !rules - نظام التحقق (بالصور الجديدة)
# ==============================

@bot.command(name="rules")
@commands.has_permissions(administrator=True)
async def send_rules(ctx):
    """إرسال Embed التحقق (للأدمن فقط) - بالصور الجديدة"""
    
    # روابط الصور الجديدة
    LEFT_SMALL_IMAGE_URL = "https://cdn.discordapp.com/attachments/1488235109650796786/1495178588738293982/Comp_1.gif?ex=69f12a92&is=69efd912&hm=83176a70a6937c8b291dcb266a041efc00dfa4f3d885ca43acb64414f2773a74&"
    RIGHT_TOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1488235109650796786/1495178588008222830/Comp_1_4.gif?ex=69f12a92&is=69efd912&hm=1563487aa33386e3442778b663301da034eb77ce686721ccffa52bb2f21d66f5&"
    BOTTOM_IMAGE_URL = "https://cdn.discordapp.com/attachments/1488235109650796786/1495178589346201650/hello_3.gif?ex=69f12a92&is=69efd912&hm=72a996025e2b3d4937883c26535e4511b51d0fa1c8907c667c33be2a30a35c19&"
    
    # إنشاء Embed باللون المطلوب #dd7222
    embed = discord.Embed(
        color=0xdd7222,  # اللون المطلوب
        title="WELCOME TO GRINDORA — PREMIER OSRS SERVICES",
        description="────────**We do the Grind You keep the Chill**────────"
    )
    
    # وضع الصورة الصغيرة على الشمال (thumbnail)
    embed.set_thumbnail(url=LEFT_SMALL_IMAGE_URL)
    
    # وضع الصورة على اليمين في الأعلى (image في الأعلى)
    embed.set_image(url=RIGHT_TOP_IMAGE_URL)
    
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
    
    # إضافة الصورة الثالثة في الأسفل (Bottom Image)
    # ملاحظة: بما أننا استخدمنا set_image للصورة العلوية، 
    # لإضافة صورة أسفل المحتوى هنستخدم صورة في footer أو نضيفها كـ field
    
    # Footer مع الصورة أو بدون
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