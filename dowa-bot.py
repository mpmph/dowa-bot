import discord
from discord.ext import commands
import re
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # ロール付与に必要

bot = commands.Bot(command_prefix="!", intents=intents)

cool_words = [
    "かっこよ", "ったく", "えぐー", "冗談ですやん","きちー", "ちょ", "落ち着け", "怒んなや", "ｗ"
    "うお", "うぉ",
    "どわ", "どぅわ"
]

# ファイル名
DATA_FILE = "points.json"

# データ読み込み
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        points = json.load(f)
else:
    points = {}

# 保存関数
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=4)

@bot.event
async def on_ready():
    print("起動したよ！")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    detected = False
    user_id = str(message.author.id)

    for word in cool_words:
        if word in message.content:
            detected = True
            break

    if re.search(r"w{2,}", message.content):
        detected = True

    if detected:
        if user_id not in points:
            points[user_id] = 0

        points[user_id] += 1
        save_data()  # ← 保存！

        # ロール付与
        member = message.guild.get_member(message.author.id)

        role_10 = discord.utils.get(message.guild.roles, name="冷笑初心者")
        role_50 = discord.utils.get(message.guild.roles, name="冷笑中級者")
        role_100 = discord.utils.get(message.guild.roles, name="冷笑マスター")

        if points[user_id] == 10 and role_10:
            await member.add_roles(role_10)
        elif points[user_id] == 50 and role_50:
            await member.add_roles(role_50)
        elif points[user_id] == 100 and role_100:
            await member.add_roles(role_100)

        await message.channel.send(
            f"冷笑を検知しました！\nしね！"
            f"\n{message.author.mention}の冷笑回数：{points[user_id]}回"
        )

    await bot.process_commands(message)

@bot.command()
async def point(ctx):
    user_id = str(ctx.author.id)
    score = points.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention} の冷笑回数：{score}回")

@bot.command()
async def rank(ctx):
    if not points:
        await ctx.send("まだ誰も冷笑してないよ！")
        return

    sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 冷笑ランキング\n\n"

    for i, (user_id, score) in enumerate(sorted_points[:10], start=1):
        text += f"{i}位：<@{user_id}>   {score}回\n"

    await ctx.send(text)
    
@bot.command()
async def stop(ctx):
    await ctx.send("Bot停止します")
    await bot.close()    

bot.run(os.getenv("TOKEN"))
