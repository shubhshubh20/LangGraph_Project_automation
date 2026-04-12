import asyncio
from collections import deque
import time
from core.state import JobState
from graph.flow import event_queue
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from demo_logger.json_logger import log_event

# 🔑 TOKEN
TOKEN = "8281846401:AAEUeXL3PiTVZcLMtY7jZ-gyNXqf-0wowBY"

# ✅ Global queues
request_queue = deque()   # <-- THIS is your Telegram request queue
active_request = None


# 📌 Store chat_id after /start
CHAT_ID = 6607871483


# ✅ Background worker (VERY IMPORTANT)
async def telegram_worker(app):
    global CHAT_ID, active_request

    while True:
        await asyncio.sleep(1)

        if CHAT_ID is None:
            continue
        
        #one request is currently showed to user
        if active_request is not None:
            continue

        if request_queue:
            job = request_queue.popleft()
            active_request = job
            await send_to_telegram(job=job, app=app)
            # keyboard = [[
            #     InlineKeyboardButton("✅ Approve", callback_data=f"approve_{job['job_id']}"),
            #     InlineKeyboardButton("❌ Reject", callback_data=f"reject_{job['job_id']}")
            # ]]

            # reply_markup = InlineKeyboardMarkup(keyboard)

            # await app.bot.send_message(
            #     chat_id=CHAT_ID,
            #     text=f"🧾 Job: {job['name']}",
            #     reply_markup=reply_markup
            # )

async def send_to_telegram(job, app):

    
    keyboard = [[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve_{job['job_id']}"),
        InlineKeyboardButton("❌ Reject", callback_data=f"reject_{job['job_id']}")
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(job["output_path"], "rb") as f:
            image_bytes = f.read()

        isImage = job["isImage"]

        if isImage:
            await app.bot.send_photo(
                chat_id=CHAT_ID,
                photo=image_bytes,
                caption=f"🖼 Job #{job['name']}",
                reply_markup=reply_markup,
            )
        else:
            await app.bot.send_video(
                chat_id=CHAT_ID,
                video=image_bytes,
                caption=f"🖼 Job #{job['name']}",
                reply_markup=reply_markup,
            )
    except Exception as e:
        print("❌ Error loading image:", e)
        # await update.message.reply_text("Failed to send image")

    

    # await app.bot.send_message(
    #     chat_id=CHAT_ID,
    #     text=f"🧾 Job: {job['name']}",
    #     reply_markup=reply_markup
    # )

# ✅ Handle approve/reject
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_request
    query = update.callback_query
    await query.answer()

    action, job_id = query.data.split("_")

    log_event(f"[EVENT] {action.upper()} for job {job_id}")

    if action == "approve":
        response = f"✅ Job {job_id} approved"
        event_queue.put({
            "type": "TELEGRAM_APPROVE_EVENT",
            "payload": {
                "job_id": job_id
            }
        })
        log_event(f"[EVENT] Job {job_id} APPROVED")
    else:        
        response = f"❌ Job {job_id} rejected"
        event_queue.put({
            "type": "TELEGRAM_REJECT_EVENT",
            "payload": {
                "job_id": job_id
            }
        })
        log_event(f"[EVENT] Job {job_id} REJECTED")

    # 🧹 remove message
    try:
        await query.message.delete()
        active_request = None
        # await query.message.reply_text(response)
    except:
        pass


# ✅ OPTIONAL: keep your message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    await update.message.reply_text(f"Received: {user_message}")


# 🚀 THIS is what YOU will call from anywhere
def send_approval_request(job_id: str, name: str, output_path: str, isImage=False):
    request_queue.append({
        "job_id": job_id,
        "name": name,
        "output_path": output_path,
        "isImage": isImage
    })



# 🚀 Main
def main(episode_number:str, server_name:str, staging_location:str):

    event_queue.put({
        "type": "INITIALIZE",
        "payload": {
            "episode_number": episode_number, 
            "server_name": server_name,
            "staging_location": staging_location
        }
    })

    # print("initialized state, starting Telegram bot...")

    app = (
        Application.builder()
        .token(TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))

    # 🔥 Start background worker
    async def post_init(app):
        asyncio.get_running_loop().create_task(telegram_worker(app))

    app.post_init = post_init
    # app.post_init = lambda app: asyncio.create_task(telegram_worker(app))

    log_event("🤖 Bot running...")
    app.run_polling()

    

