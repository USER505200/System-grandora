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
    
    # إنشاء زر التحقق
    verify_button = discord.ui.Button(
        custom_id="Grindora_verify",
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


# ==============================
# أمر !pay - نظام الدفع بالقائمة المنسدلة (Select Menu)
# ==============================

@bot.command(name="pay")
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
    
    # ===== القائمة المنسدلة للدفع =====
    # الـ Select Menu هيتعامل معاه كلاس PaymentSelect تلقائياً
    # مش محتاج نضيف حاجة هنا عشان الـ callback شغال جوه الكلاس


# ==============================
# معالجة الأخطاء
# ==============================



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