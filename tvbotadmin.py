"""
bot_admin.py
------------
Reusable admin command handlers for python-telegram-bot bots.

Requirements in bot_data:
    bot_data["cfg"]           - dict with keys: admin_users (set[int])
    bot_data["allowed_users"] - live-editable set[int] (KEY_ALLOWED_USERS)

Usage:
    from bot_admin import register_admin_handlers, KEY_ALLOWED_USERS

    app.bot_data["cfg"]           = cfg          # must contain "admin_users"
    app.bot_data[KEY_ALLOWED_USERS] = allowed_users

    register_admin_handlers(app)
"""

import logging
from functools import wraps

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

# Shared state key — import this in your bot so both modules use the same string
KEY_ALLOWED_USERS = "allowed_users"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_allowed(context: ContextTypes.DEFAULT_TYPE) -> set[int]:
    return context.bot_data[KEY_ALLOWED_USERS]


def _is_admin(user_id: int, cfg: dict) -> bool:
    return user_id in cfg["admin_users"]

def is_allowed(user_id: int, allowed: set[int]) -> bool:
    return not allowed or user_id in allowed


def admin_only(func):
    """Decorator — rejects non-admins before the handler runs."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not _is_admin(user_id, context.bot_data["cfg"]):
            await update.message.reply_text("⛔ Admin access required.")
            logger.warning(
                f"Unauthorised admin attempt: user_id={user_id} "
                f"username=@{update.effective_user.username}"
            )
            return
        return await func(update, context)
    return wrapper


# ---------------------------------------------------------------------------
# Admin handlers
# ---------------------------------------------------------------------------

@admin_only
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin command reference."""
    cfg     = context.bot_data["cfg"]
    allowed = _get_allowed(context)
    admins  = cfg["admin_users"]

    await update.message.reply_text(
        "🔑 *Admin Menu*\n\n"
        f"👥 Allowed users: {len(allowed) if allowed else 'ALL (open)'}\n"
        f"🛡 Admins: {len(admins)}\n\n"
        "*Commands:*\n"
        "`/adduser <id>` — add user to allow list\n"
        "`/removeuser <id>` — remove user from allow list\n"
        "`/users` — list all allowed users\n"
        "`/status` — bot config + ComfyUI queue\n"
        "`/broadcast <message>` — message all allowed users",
        parse_mode="Markdown",
    )


@admin_only
async def cmd_adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a user ID to the live allow list."""
    args = context.args
    if not args or not args[0].lstrip("-").isdigit():
        await update.message.reply_text(
            "Usage: `/adduser <telegram_user_id>`", parse_mode="Markdown"
        )
        return

    new_id  = int(args[0])
    allowed = _get_allowed(context)
    allowed.add(new_id)
    logger.info(f"Admin {update.effective_user.id} added user {new_id}")
    await update.message.reply_text(
        f"✅ User `{new_id}` added to allow list.", parse_mode="Markdown"
    )


@admin_only
async def cmd_removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a user ID from the live allow list."""
    args = context.args
    if not args or not args[0].lstrip("-").isdigit():
        await update.message.reply_text(
            "Usage: `/removeuser <telegram_user_id>`", parse_mode="Markdown"
        )
        return

    rm_id   = int(args[0])
    allowed = _get_allowed(context)
    cfg     = context.bot_data["cfg"]

    if rm_id in cfg["admin_users"]:
        await update.message.reply_text("⛔ Cannot remove an admin from the allow list.")
        return

    if rm_id in allowed:
        allowed.discard(rm_id)
        logger.info(f"Admin {update.effective_user.id} removed user {rm_id}")
        await update.message.reply_text(
            f"✅ User `{rm_id}` removed.", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"ℹ️ User `{rm_id}` was not in the allow list.", parse_mode="Markdown"
        )


@admin_only
async def cmd_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all currently allowed users."""
    allowed = _get_allowed(context)
    cfg     = context.bot_data["cfg"]

    if not allowed:
        await update.message.reply_text(
            "ℹ️ Allow list is empty — bot is open to all users."
        )
        return

    lines = [
        f"  `{uid}`" + (" 🛡 admin" if uid in cfg["admin_users"] else "")
        for uid in sorted(allowed)
    ]
    await update.message.reply_text(
        f"👥 *Allowed users ({len(allowed)}):*\n" + "\n".join(lines),
        parse_mode="Markdown",
    )


@admin_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot config and live ComfyUI queue status."""
    cfg = context.bot_data["cfg"]

    try:
        import json as _json
        import urllib.request
        url = f"http://{cfg['comfy_host']}:{cfg['comfy_port']}/queue"
        with urllib.request.urlopen(url, timeout=3) as r:
            queue = _json.loads(r.read())
        running = len(queue.get("queue_running", []))
        pending = len(queue.get("queue_pending", []))
        comfy_status = f"✅ Online — running: {running}, pending: {pending}"
    except Exception as e:
        comfy_status = f"❌ Unreachable ({e})"

    allowed = _get_allowed(context)
    await update.message.reply_text(
        "📊 *Bot Status*\n\n"
        f"🤖 Vision model: `{cfg.get('ollama_model', 'N/A')}`\n"
        f"🌐 Ollama host:  `{cfg.get('ollama_host', 'N/A')}`\n"
        f"🎨 ComfyUI:      `{cfg.get('comfy_host', 'N/A')}:{cfg.get('comfy_port', 'N/A')}`\n"
        f"🔧 Workflow:     `{cfg.get('default_workflow', 'N/A')}`\n"
        f"👥 Allowed users: {len(allowed) if allowed else 'ALL'}\n"
        f"🖥 Queue:        {comfy_status}",
        parse_mode="Markdown",
    )


@admin_only
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message to all users in the allow list."""
    if not context.args:
        await update.message.reply_text(
            "Usage: `/broadcast <message>`", parse_mode="Markdown"
        )
        return

    message = " ".join(context.args)
    allowed = _get_allowed(context)

    if not allowed:
        await update.message.reply_text("ℹ️ No users in allow list to broadcast to.")
        return

    sent = failed = 0
    for uid in allowed:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 *Broadcast from admin:*\n\n{message}",
                parse_mode="Markdown",
            )
            sent += 1
        except Exception as e:
            logger.warning(f"Broadcast failed for user {uid}: {e}")
            failed += 1

    await update.message.reply_text(
        f"📢 Broadcast complete: {sent} sent, {failed} failed."
    )


# ---------------------------------------------------------------------------
# Registration helper
# ---------------------------------------------------------------------------

def register_admin_handlers(app: Application) -> None:
    """Register all admin command handlers on the given Application instance."""
    app.add_handler(CommandHandler("admin",      cmd_admin))
    app.add_handler(CommandHandler("adduser",    cmd_adduser))
    app.add_handler(CommandHandler("removeuser", cmd_removeuser))
    app.add_handler(CommandHandler("users",      cmd_users))
    app.add_handler(CommandHandler("status",     cmd_status))
    app.add_handler(CommandHandler("broadcast",  cmd_broadcast))
    logger.info("[+] Admin handlers registered.")