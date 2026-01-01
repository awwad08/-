import discord
from discord.ext import commands
import os
from flask import Flask  # لإضافة خادم ويب بسيط لـ Render

# إعداد البوت
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# إضافة خادم ويب للحفاظ على التشغيل (مطلوب لـ Render)
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل!"

@bot.event
async def on_ready():
    print(f'البوت جاهز: {bot.user}')

@bot.command()
async def check_messages(ctx, role_name: str, threshold: int = 1500):
    # نفس الكود السابق (انظر الرسائل السابقة للتفاصيل الكاملة)
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"الدور '{role_name}' غير موجود.")
        return
    
    await ctx.send(f"جاري فحص الرسائل للدور '{role_name}'...")
    
    message_counts = {}
    for channel in ctx.guild.text_channels:
        try:
            async for message in channel.history(limit=None):
                author = message.author
                if not author.bot and role in author.roles:
                    message_counts[author] = message_counts.get(author, 0) + 1
        except discord.Forbidden:
            continue
    
    low_message_users = [user for user, count in message_counts.items() if count < threshold]
    
    if low_message_users:
        response = f"المستخدمون الذين لديهم الدور '{role_name}' وأقل من {threshold} رسالة:\n"
        for user in low_message_users[:10]:
            response += f"- {user.mention}: {message_counts[user]} رسالة\n"
        if len(low_message_users) > 10:
            response += f"... و {len(low_message_users) - 10} آخرين."
    else:
        response = f"لا يوجد مستخدمون لديهم الدور '{role_name}' وأقل من {threshold} رسالة."
    
    await ctx.send(response)

# تشغيل البوت و الخادم
if __name__ == "__main__":
    from threading import Thread
    # تشغيل الخادم في thread منفصل
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))).start()
    # تشغيل البوت
    bot.run(os.getenv('DISCORD_TOKEN'))  # استخدم متغير البيئة للتوكن
