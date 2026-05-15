#!/usr/bin/env python

import argparse
import asyncio
import base64
import logging
import hashlib
import ollama
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from tvbotadmin import register_admin_handlers, KEY_ALLOWED_USERS, admin_only, cmd_admin, cmd_adduser, cmd_broadcast, cmd_status, cmd_users, is_allowed

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import vtquery

# Get environment variables ------------------------------------------------------------
load_dotenv()
# ---------------------------------------------------------------------------------------

# Configure Menus -----------------------------------------------------------------------
OPTION1_TEXT = "Option 1"
OPTION2_TEXT = "Option 2"
OPTION3_TEXT = "Upload an image"
OPTION4_TEXT = "Option 4"
CANCEL_TEXT = "Cancel"

# Enable logging -------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
# ----------------------------------------------------------------------------------------

# Create a menu --------------------------------------------------------------------------
def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(    inline_keyboard = [
        # Row 1
        [
            InlineKeyboardButton(OPTION1_TEXT, callback_data="1"),
            InlineKeyboardButton(OPTION2_TEXT, callback_data="2"),
        ], 
        # Row 2
        [
            InlineKeyboardButton(OPTION3_TEXT, callback_data="3"),
        ],
        # Row 3
        [
        InlineKeyboardButton(OPTION4_TEXT, callback_data="4"),
        ],
        # Row 4
        [
            InlineKeyboardButton(CANCEL_TEXT, callback_data="cancel"),
        ]
    ])
# ----------------------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! What would you like to do?",
        reply_markup=confirm_keyboard(),
    )
    
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Incoming photo from user_id={update.effective_user.id} username=@{update.effective_user.username}")
    cfg     = context.bot_data["cfg"]
    user_id = update.effective_user.id
    # Check if user is allowed
    allowed = KEY_ALLOWED_USERS(context)

    if not is_allowed(user_id, allowed):
        await update.message.reply_text("⛔ You are not authorised to use this bot.")
        return

    # Optionally clear the flag if you set it from button "3"
    context.user_data.pop("awaiting_image_for_prompt", None)
    
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data
    cfg   = context.bot_data["cfg"]

    if data == "1":
        logger.info("[+] Select Backend")
        await query.answer(text="Not yet implemented")
        return

    if data == "2":
        logger.info("[+] Select Workflow")
        await query.answer(text="Not yet implemented")
        return
    
    if data == "3":
        logger.info("[+] Menu button was clicked for Uploading image")
        context.user_data["awaiting_image_for_prompt"] = True
        await query.edit_message_text("🔎 Upload an image for analysis:")
        return
    
    if data == "4":
        logger.info("[+] Option 4")
        await query.answer(text="Not yet implemented")
        return

def parse_args():
    p = argparse.ArgumentParser(description="Telegram threat intel bot")
    p.add_argument("--token",        default=os.getenv("THREAT_INTEL_TOKEN"))
    logger.info("[!] Parser set token")

    p.add_argument("--allowed-users",
                   default=os.getenv("ALLOWED_USERS", ""),
                   help="Comma-separated Telegram user IDs. Empty = allow all.")
    p.add_argument("--admin-users",
                   default=os.getenv("ADMIN_USERS", ""),
                   help="Comma-separated Telegram user IDs with admin access.")
    return p.parse_args()


def main() -> None:
    """Run the bot."""
    args = parse_args()
    if not args.token:
        raise ValueError("TELEGRAM_TOKEN not set. Use --token or set env var.")
    
    # Allow users -------------------------------------------------------------------------
    def parse_ids(s: str) -> set[int]:
        return {int(x.strip()) for x in s.split(",") if x.strip().lstrip("-").isdigit()}

    allowed_users = parse_ids(args.allowed_users)
    admin_users   = parse_ids(args.admin_users)

    # Admins are implicitly allowed
    allowed_users.update(admin_users)
    # -------------------------------------------------------------------------------------------

    cfg = {
        "admin_users":     admin_users,   # immutable at runtime — change in .env and restart
    }
    
    # Create the Application and pass it your bot's token.
    app = Application.builder().token(args.token).build()
    
    # Get config from environment
    app.bot_data["cfg"]              = cfg
    app.bot_data[KEY_ALLOWED_USERS]  = allowed_users  # live-editable via /adduser /removeuser

    # Standard commands
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("help",     cmd_start))

    #app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo)) # triggered when photo is uploaded
    app.add_handler(CallbackQueryHandler(handle_callback)) # for menu button taps
    
    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
