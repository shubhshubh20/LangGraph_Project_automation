from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import random

# 🔑 Replace with your bot token
TOKEN = "8281846401:AAEUeXL3PiTVZcLMtY7jZ-gyNXqf-0wowBY"


# ✅ Command to send a job with buttons
async def send_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_id = random.randint(100, 999)  # You can make this dynamic later

    # 👉 Use your local image OR URL
    image_path = "D:\\youtube\\corner_table\\scene2\\s01_e07\\Expressions\\ananya\\Ananya02.png"   # make sure this file exists

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{job_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{job_id}"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # await update.message.reply_photo(
        #     photo=image_bytes,
        #     caption=f"🖼 Job #{job_id}",
        #     reply_markup=reply_markup,
        # )
        await update.message.reply_text(
            f"Job #{job_id} is ready. Please review:",
            reply_markup=reply_markup,
        )
        print(f"[EVENT] Sent job #{job_id} with buttons")
        # print("✅ Sent job with image and buttons")
    except Exception as e:
        print("❌ Error sending image:", e)
        await update.message.reply_text("Failed to send image. Try again.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global CHAT_ID
    CHAT_ID = update.effective_chat.id

    await update.message.reply_text(f'chat id is {CHAT_ID}')

# ✅ Handle button clicks
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        data = query.data
        action, job_id = data.split("_")

        if action == "approve":
            response = f"✅ Job {job_id} approved"
            print(f"[EVENT] Job {job_id} APPROVED")

        else:
            response = f"❌ Job {job_id} rejected"
            print(f"[EVENT] Job {job_id} REJECTED")

        # Delete the image message
        await query.message.delete()

        # await query.edit_message_caption(caption=response)
        # await query.edit_message_text(text=response)
        await query.message.reply_text(response)

    except Exception as e:
        print("❌ Button error:", e)


def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .build()
    )

    # Command: /job → sends buttons
    app.add_handler(CommandHandler("job", send_job))

    app.add_handler(CommandHandler("start", start))

    # Handles button clicks
    app.add_handler(CallbackQueryHandler(handle_button))

    print("🤖 Bot is running...")
    app.run_polling()
    


if __name__ == "__main__":
    main()