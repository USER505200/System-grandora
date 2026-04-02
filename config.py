# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token
TOKEN = os.getenv("DISCORD_TOKEN")

# Server ID
GUILD_ID = 1487197600456249378

# Member Role ID (للتحقق - من نظام !rules)
MEMBER_ROLE_ID = 1487292364052500613

# Channel IDs
CH_RULES = "1487241829752639499"
CH_RATES = "1487243724865011822"
CH_TICKETS = "1487244035516006551"

# الرتب المسموح لها باستخدام أمر !pay
ALLOWED_PAY_ROLES = [
    1487299732215697469,  # رتبة 1
    1487298785913606317   # رتبة 2
]

# إعدادات نظام التقييم (Feedback)
WORKER_ROLE_ID = None  # هيتحدد تلقائي من settings.json
FEEDBACK_CHANNEL_ID = None  # هيتحدد تلقائي من settings.json

# Payment addresses (لنظام !pay)
PAYMENT_ADDRESSES = {
    "Binance ID": {
        "emoji": "<:binance:1488521944436576266>",
        "address": "805246428",
        "details": "**Binance ID:**\n```\n805246428\n```\n*Send payment to this Binance ID*"
    },
    "BTC": {
        "emoji": "<:BTC:1488522118483148931>",
        "address": "139VGYGut17XqR1XjxPx5Hmf3ntZYpBsqF",
        "details": "**BTC Address:**\n```\n139VGYGut17XqR1XjxPx5Hmf3ntZYpBsqF\n```"
    },
    "USDT (TRC20)": {
        "emoji": "<:usdt:1488522296246145126>",
        "address": "TQ5QS29PDc5xLPXnEeRLCovieWVvRu5D3s",
        "details": "**USDT (TRC20) Address:**\n```\nTQ5QS29PDc5xLPXnEeRLCovieWVvRu5D3s\n```"
    },
    "LTC": {
        "emoji": "<:ltc:1488522472704970893>",
        "address": "LfktE6o5ZsWHEuphCxzTq8W2Bu5hiABMKh",
        "details": "**Litecoin Address:**\n```\nLfktE6o5ZsWHEuphCxzTq8W2Bu5hiABMKh\n```"
    },
    "ETH (ERC20)": {
        "emoji": "<:eth:1488526448514826451>",
        "address": "0x1a28069fd2409b323084d2ad62fff6313202ada7",
        "details": "**Ethereum (ERC20) Address:**\n```\n0x1a28069fd2409b323084d2ad62fff6313202ada7\n```"
    },
    "OSRS GP": {
        "emoji": "<:osrs:1488535767134244884>",
        "details": "**OSRS Gold Payment:**\nContact staff for OSRS GP payment details"
    }
}