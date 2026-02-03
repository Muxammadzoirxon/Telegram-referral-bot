import sqlite3
from telegram.ext import Updater, CommandHandler

# --- Database setup ---
conn = sqlite3.connect("members.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS members (user_id INTEGER PRIMARY KEY, count INTEGER)")
conn.commit()

def get_count(user_id):
    cursor.execute("SELECT count FROM members WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def set_count(user_id, count):
    cursor.execute("INSERT OR REPLACE INTO members (user_id, count) VALUES (?, ?)", (user_id, count))
    conn.commit()

def reset_all():
    cursor.execute("DELETE FROM members")
    conn.commit()

# --- Commands ---
def mymembers(update, context):
    user_id = update.effective_user.id
    count = get_count(user_id)
    update.message.reply_text(f"📊 Siz qo‘shgan odamlar soni: {count}")

def yourmembers(update, context):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        count = get_count(user_id)
        update.message.reply_text(f"📈 {update.message.reply_to_message.from_user.first_name} qo‘shgan odamlar soni: {count}")
    else:
        update.message.reply_text("❗ Bu buyruqni reply orqali ishlating.")

def top_generic(update, context, limit):
    cursor.execute("SELECT user_id, count FROM members ORDER BY count DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    text = f"🏆 Eng ko‘p odam qo‘shgan {limit} talik:\n"
    for i, (user_id, count) in enumerate(rows, 1):
        try:
            user = context.bot.get_chat_member(update.effective_chat.id, user_id).user
            text += f"{i}. {user.first_name} — {count} ta\n"
        except:
            text += f"{i}. UserID {user_id} — {count} ta\n"
    update.message.reply_text(text)

def top10(update, context): top_generic(update, context, 10)
def top20(update, context): top_generic(update, context, 20)
def top30(update, context): top_generic(update, context, 30)
def top40(update, context): top_generic(update, context, 40)

def delson(update, context):
    reset_all()
    update.message.reply_text("🗑 Barcha statistikalar tozalandi!")

def clean(update, context):
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        set_count(user_id, 0)
        update.message.reply_text(f"🧹 {update.message.reply_to_message.from_user.first_name} statistikasi 0 ga tenglashtirildi!")
    else:
        update.message.reply_text("❗ Bu buyruqni reply orqali ishlating.")

def merge(update, context):
    if update.message.reply_to_message and context.args:
        source_id = update.message.reply_to_message.from_user.id
        target_username = context.args[0].replace("@", "")
        try:
            target_user = context.bot.get_chat_member(update.effective_chat.id, target_username).user
            source_count = get_count(source_id)
            target_count = get_count(target_user.id)
            set_count(target_user.id, source_count + target_count)
            set_count(source_id, 0)
            update.message.reply_text(
                f"🔄 {update.message.reply_to_message.from_user.first_name} statistikasi "
                f"{target_user.first_name} ga qo‘shildi!"
            )
        except:
            update.message.reply_text("❗ Target user topilmadi.")
    else:
        update.message.reply_text("❗ Reply va target username bilan ishlating. Masalan: /merge @username")

def plus(update, context):
    if update.message.reply_to_message:
        source_id = update.effective_user.id
        target_id = update.message.reply_to_message.from_user.id
        source_count = get_count(source_id)
        target_count = get_count(target_id)
        set_count(target_id, source_count + target_count)
        set_count(source_id, 0)
        update.message.reply_text(
            f"➕ {update.effective_user.first_name} ballari "
            f"{update.message.reply_to_message.from_user.first_name} ga o‘tkazildi!"
        )
    elif context.args:
        try:
            target_username = context.args[0].replace("@", "")
            target_user = context.bot.get_chat_member(update.effective_chat.id, target_username).user
            source_id = update.effective_user.id
            source_count = get_count(source_id)
            target_count = get_count(target_user.id)
            set_count(target_user.id, source_count + target_count)
            set_count(source_id, 0)
            update.message.reply_text(
                f"➕ {update.effective_user.first_name} ballari {target_user.first_name} ga o‘tkazildi!"
            )
        except:
            update.message.reply_text("❗ Target user topilmadi.")
    else:
        update.message.reply_text("❗ Reply yoki username bilan ishlating. Masalan: /plus @username")

def main():
    updater = Updater("8550532656:AAEUjdGgGKXpPJ9BiOinUOaj99d2Na3OisQ", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("mymembers", mymembers))
    dp.add_handler(CommandHandler("yourmembers", yourmembers))
    dp.add_handler(CommandHandler("top10", top10))
    dp.add_handler(CommandHandler("top20", top20))
    dp.add_handler(CommandHandler("top30", top30))
    dp.add_handler(CommandHandler("top40", top40))
    dp.add_handler(CommandHandler("delson", delson))
    dp.add_handler(CommandHandler("clean", clean))
    dp.add_handler(CommandHandler("merge", merge))
    dp.add_handler(CommandHandler("plus", plus))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()