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
# كلاسات أزرار الدفع (Payment Buttons)
# ==============================

class PaymentButton(ui.Button):
    """Button for each payment method"""
    
    def __init__(self, name: str, emoji: str):
        super().__init__(
            label=name,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
            custom_id=f"payment_{name.replace(' ', '_').replace('(', '').replace(')', '')}"
        )
        self.payment_name = name
    
    async def callback(self, interaction: discord.Interaction):
        """When button is clicked"""
        payment_data = config.PAYMENT_ADDRESSES[self.payment_name]
        
        embed = discord.Embed(
            title=f"{payment_data.get('emoji', '💰')} {self.payment_name} - Payment Details",
            description=payment_data["details"],
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="⚠️ Important",
            value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PaymentButtonsView(ui.View):
    """View containing all payment method buttons"""
    
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add a button for each payment method
        for name, data in config.PAYMENT_ADDRESSES.items():
            self.add_item(PaymentButton(name, data.get("emoji", "💰")))


# ==============================
# حدث تشغيل البوت
# ==============================

@bot.event
async def on_ready():
    """عند تشغيل البوت"""
    print(f"✅ Prime07 Bot is online as {bot.user}")
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
    
    # إنشاء زر التحقق
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


# ==============================
# أمر !pay - نظام الدفع بالأزرار
# ==============================

@bot.command(name="pay")
@has_allowed_role()
async def show_payments(ctx):
    """عرض طرق الدفع المتاحة (لأصحاب الرتب المحددة)"""
    
    embed = discord.Embed(
        title="💳 PRIME07 — PAYMENT METHODS",
        description="We currently accept the following:",
        color=discord.Color.gold()
    )
    
    # Display all payment methods
    methods = []
    for name, data in config.PAYMENT_ADDRESSES.items():
        methods.append(f"{data.get('emoji', '💰')} **{name}**")
    
    embed.add_field(
        name="🪙 Payment Methods",
        value="\n".join(methods),
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Important",
        value="• We NEVER DM first\n• Payments are ONLY done inside tickets\n• Always confirm staff before sending\n\n📌 After payment, send screenshot in this ticket",
        inline=False
    )
    
    embed.set_footer(text="Click any button below to see payment details")
    
    view = PaymentButtonsView()
    await ctx.send(embed=embed, view=view)


# ==============================
# حدث تفاعل زر التحقق
# ==============================

@bot.event
async def on_interaction(interaction):
    """معالجة جميع الأزرار"""
    
    # التأكد من أن التفاعل هو زر (Button)
    if not interaction.type == discord.InteractionType.component:
        return
    
    if not hasattr(interaction, 'data') or not interaction.data:
        return
    
    custom_id = interaction.data.get("custom_id")
    
    # ===== زر التحقق =====
    if custom_id == "prime07_verify":
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
    
    # ===== أزرار الدفع =====
    elif custom_id.startswith("payment_"):
        # الـ callback بتاع الزر هيتعامل معاه كلاس PaymentButton
        # بس لازم نعرف إن الزر معمول من الـ View بتاعنا
        pass


# ==============================
# معالجة الأخطاء
# ==============================

@bot.event
async def on_command_error(ctx, error):
    """معالجة الأخطاء"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Available commands: `!rules`, `!pay`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need **Administrator** permissions to use `!rules`.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use `!pay`. This command is only available for authorized roles.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")


# ==============================
# تشغيل البوت
# ==============================

if __name__ == "__main__":
    if not config.TOKEN:
        print("❌ Error: DISCORD_TOKEN not found!")
        print("Please add DISCORD_TOKEN in Railway Environment Variables")
    else:
        print("🚀 Starting Prime07 Bot...")
        bot.run(config.TOKEN)