# config.py
import os

# Bot Token - هتضيفه في Railway Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Server ID
GUILD_ID = 1487197600456249378

# Member Role ID (للتحقق)
MEMBER_ROLE_ID = "1487292364052500613"

# Channel IDs
CH_RULES = "1487241829752639499"
CH_RATES = "1487243724865011822"
CH_TICKETS = "1487244035516006551"

# Server emojis - غير الـ IDs دي حسب السيرفر بتاعك
# عشان تجيب ID الإيموجي: اكتب \:emoji_name: في ديسكورد
SERVER_EMOJIS = {
    "binance": "<:binance:1488521944436576266>",
    "BTC": "<:BTC:1488522118483148931>",
    "usdt": "<:usdt:123456789012345678>",  # غير الرقم ده
    "ltc": "<:ltc:1488522296246145126>",
    "eth": "<:eth:1488526448514826451>",
    "osrs": "<:osrs:1488535767134244884>",
}

# Payment addresses
PAYMENT_ADDRESSES = {
    "Binance ID": {
        "emoji": SERVER_EMOJIS["binance"],
        "address": "805246428",
        "details": "**Binance ID:**\n```\n805246428\n```\n*Send payment to this ID*"
    },
    "BTC": {
        "emoji": SERVER_EMOJIS["BTC"],
        "address": "139VGYGut17XqR1XjxPx5Hmf3ntZYpBsqF",
        "details": "**BTC Address:**\n```\n139VGYGut17XqR1XjxPx5Hmf3ntZYpBsqF\n```"
    },
    "USDT (TRC20)": {
        "emoji": SERVER_EMOJIS["usdt"],
        "address": "TQ5QS29PDc5xLPXnEeRLCovieWVvRu5D3s",
        "details": "**USDT (TRC20) Address:**\n```\nTQ5QS29PDc5xLPXnEeRLCovieWVvRu5D3s\n```"
    },
    "LTC": {
        "emoji": SERVER_EMOJIS["ltc"],
        "address": "LfktE6o5ZsWHEuphCxzTq8W2Bu5hiABMKh",
        "details": "**Litecoin Address:**\n```\nLfktE6o5ZsWHEuphCxzTq8W2Bu5hiABMKh\n```"
    },
    "ETH (ERC20)": {
        "emoji": SERVER_EMOJIS["eth"],
        "address": "0x1a28069fd2409b323084d2ad62fff6313202ada7",
        "details": "**Ethereum (ERC20) Address:**\n```\n0x1a28069fd2409b323084d2ad62fff6313202ada7\n```"
    },
    "OSRS GP": {
        "emoji": SERVER_EMOJIS["osrs"],
        "details": "**OSRS Gold Payment:**\nContact staff for OSRS GP payment details"
    }
}