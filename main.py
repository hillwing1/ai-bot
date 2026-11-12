import os
import discord
from flask import Flask
from threading import Thread
from google import genai

# 1. Flask 防休眠微型網頁（讓 Render 保持在線）
app = Flask('')

@app.route('/')
def home():
    return "AI Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# 2. 初始化 Gemini AI（請把雙引號內的文字換成你的 AIza 開頭金鑰）
ai_client = genai.Client(api_key="AIzaSy你剛剛複製的金鑰")

# 3. 設定 Discord Bot 權限
intents = discord.Intents.default()
intents.message_content = True  # 記得在 Discord 開發者後台開啟 Message Content Intent
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"全新純 AI 機器人已成功上線：{bot.user}")

@bot.event
async def on_message(message: discord.Message):
    # 避免機器人自己跟自己對話
    if message.author.bot:
        return  

    # 當機器人被 @ 提及時（排除 @everyone / @here）
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        target_content = ""

        # 情況 A：針對特定訊息按「回覆」並 @ 機器人
        if message.reference and message.reference.message_id:
            try:
                replied_msg = await message.channel.fetch_message(message.reference.message_id)
                target_content = replied_msg.content
            except Exception:
                pass

        # 情況 B：直接打 @機器人，自動抓取頻道裡的上一則訊息
        if not target_content:
            history = [msg async for msg in message.channel.history(limit=2)]
            if len(history) >= 2:
                target_content = history[1].content

        if target_content.strip():
            async with message.channel.typing():
                try:
                    response = ai_client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=f"請針對以下這段話做出簡短、幽默且自然的繁體中文回應：\n\n{target_content}"
                    )
                    await message.reply(response.text)
                except Exception as e:
                    await message.reply(f"模型思考時發生錯誤：`{e}`")
        else:
            await message.reply("前面的訊息沒有文字內容，我沒辦法回應喔！")

# 啟動防休眠網頁與機器人（請把雙引號內的文字換成你新 Bot 的 Token）
keep_alive()
bot.run("AQ.Ab8RN6Kkf4dYshSwNnW4d4DmeSC6xtFQLafqXwtUcueV6pAJHw")
