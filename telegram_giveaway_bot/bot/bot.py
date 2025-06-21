import logging
import sys # For sys.exit
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from config.settings import TELEGRAM_BOT_TOKEN, LOG_LEVEL, DATABASE_URL #, LOG_FILE
from bot.models import get_db, init_db, User
from bot import giveaway_manager

# Configure logging
if LOG_FILE and LOG_FILE.strip() != '':
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=LOG_LEVEL,
        filename=LOG_FILE,
        filemode='a'  # Append to log file
    )
else:
    # Console logging if LOG_FILE is not set or empty
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=LOG_LEVEL
    )
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext):
    """Sends a welcome message when the /start command is issued."""
    db = next(get_db())
    try:
        user_info = update.effective_user
        giveaway_manager.create_user(
            db,
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )
        await update.message.reply_text(
            "Hello! I am your giveaway bot. Use /create_giveaway to start a new giveaway."
        )
    finally:
        db.close()

async def help_command(update: Update, context: CallbackContext):
    """Sends a help message when the /help command is issued."""
    help_text = (
        'Welcome to the Giveaway Bot! Here\'s how to use me:\n\n'
        'Available commands:\n'
        '/start - Shows a welcome message and registers you.\n'
        '/help - Shows this help message.\n'
        '/create_giveaway <Title> | <Description> | <YYYY-MM-DD HH:MM>\n'
        '    Example: /create_giveaway Awesome Prize | Win a fantastic item! | 2024-12-31 23:59\n'
        '    This command creates a new giveaway. Make sure to use the exact format!\n\n'
        'How to Participate:\n\n'
        'When a giveaway is created, a message will be posted with a "Participate!" button. '
        'Just click it to enter!\n\n'
        'Giveaways are drawn automatically when their end time is reached.'
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def create_giveaway_command(update: Update, context: CallbackContext):
    """Creates a new giveaway."""
    db = next(get_db())
    try:
        user_info = update.effective_user
        # Ensure user exists
        giveaway_manager.create_user(
            db,
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )

        # Example usage: /create_giveaway My Awesome Giveaway | Win cool stuff! | 2023-12-31 23:59
        command_parts = update.message.text.split("|")
        if len(command_parts) != 3: # command itself is part 0, then title, desc, date
            await update.message.reply_text(
                "Usage: /create_giveaway <Title> | <Description> | <YYYY-MM-DD HH:MM>"
            )
            return

        full_command, title, description, end_date_str = command_parts
        title = title.strip()
        description = description.strip()
        end_date_str = end_date_str.strip()

        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            await update.message.reply_text(
                "Invalid date format. Please use YYYY-MM-DD HH:MM"
            )
            return

        if end_date <= datetime.utcnow():
            await update.message.reply_text("End date must be in the future.")
            return

        # Send a message that will house the giveaway info and participation button
        giveaway_message = await update.message.reply_text(
            f"🎉 **New Giveaway!** 🎉\n\n"
            f"**Title:** {title}\n"
            f"**Description:** {description}\n"
            f"**Ends:** {end_date.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            f"Click the button below to participate!",
            parse_mode='Markdown'
        )

        giveaway = giveaway_manager.create_giveaway(
            db, title=title, description=description, end_date=end_date, message_id=giveaway_message.message_id, chat_id=update.effective_chat.id
        )

        keyboard = [[InlineKeyboardButton("Participate!", callback_data=f"participate_{giveaway.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id, message_id=giveaway_message.message_id, reply_markup=reply_markup)

        await update.message.reply_text(f"Giveaway '{title}' created with ID: {giveaway.id}")

    except Exception as e:
        logger.error(f"Error creating giveaway: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while creating the giveaway.")
    finally:
        db.close()


async def button_callback(update: Update, context: CallbackContext):
    """Handles button presses for participation."""
    query = update.callback_query
    await query.answer() # Acknowledge the button press

    action, giveaway_id_str = query.data.split("_")
    giveaway_id = int(giveaway_id_str)

    db = next(get_db())
    try:
        user_info = query.effective_user
        user = giveaway_manager.create_user(
            db,
            telegram_id=user_info.id,
            username=user_info.username,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )

        if action == "participate":
            giveaway = giveaway_manager.get_giveaway(db, giveaway_id)
            if not giveaway:
                await query.edit_message_text(text="Sorry, this giveaway no longer exists.")
                return

            if giveaway.end_date <= datetime.utcnow():
                await query.edit_message_text(text=f"Sorry, the giveaway '{giveaway.title}' has ended.")
                return

            # Attempt to add participant and get a status
            participation_result = giveaway_manager.add_participant(db, giveaway_id=giveaway_id, user_id=user.id)

            if participation_result == 'SUCCESS':
                await query.message.reply_text(f"@{user_info.username} You have successfully participated in '{giveaway.title}'!")
            elif participation_result == 'ALREADY_PARTICIPATING':
                await query.message.reply_text(f"@{user_info.username} You are already participating in '{giveaway.title}'.")
            elif participation_result == 'GIVEAWAY_ENDED': # This check is somewhat redundant here as it's checked above
                await query.edit_message_text(text=f"Sorry, the giveaway '{giveaway.title}' has already ended.")
            elif participation_result == 'GIVEAWAY_NOT_FOUND': # Also somewhat redundant
                 await query.edit_message_text(text="Sorry, this giveaway no longer exists.")
            else: # Covers 'FAILED' or any other unexpected status from add_participant
                await query.message.reply_text(f"@{user_info.username} An error occurred while trying to participate. Please try again later.")
    except Exception as e:
        logger.error(f"Error during button callback: {e}", exc_info=True)
        await query.message.reply_text("An error occurred processing your participation.")
    finally:
        db.close()

def main() -> None:
    """Start the bot."""
    # Database initialization is now handled by Alembic migrations.
    # Users should run `alembic upgrade head` before starting the bot for the first time
    # or after pulling changes that include new migrations.

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN_FALLBACK':
        logger.error('CRITICAL: TELEGRAM_BOT_TOKEN is not configured or is using the default fallback. Please set the environment variable.')
        print('CRITICAL: TELEGRAM_BOT_TOKEN is not configured. Please set the environment variable.')
        sys.exit(1) # Exit with error code if token is not set

    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("create_giveaway", create_giveaway_command))
        application.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r'/participate_(\d+)'), None)) # Placeholder for direct /participate command if needed
        application.add_handler(CallbackQueryHandler(button_callback))

        # Scheduler setup
        jobstores = {
            'default': SQLAlchemyJobStore(url=DATABASE_URL)
        }
        scheduler = AsyncIOScheduler(jobstores=jobstores)
        scheduler.add_job(check_ended_giveaways, 'interval', seconds=60, args=[application]) # Check every 60 seconds


        logger.info("Bot starting to poll...")
        try:
            scheduler.start()
            logger.info("Scheduler started.")
            application.run_polling()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user (KeyboardInterrupt).")
        finally:
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shutdown complete.")

    except Exception as e:
        logger.critical(f"CRITICAL: Unhandled exception in main execution: {e}", exc_info=True)
        print(f"CRITICAL: An unhandled error occurred. Check '{LOG_FILE}' (if configured) or console logs for details. Error: {e}")
        sys.exit(1) # Exit with error code

async def announce_winner(bot, chat_id: int, giveaway: giveaway_manager.Giveaway, winner: User):
    """Announces the winner of a giveaway."""
    winner_username = f"@{winner.username}" if winner.username else winner.first_name
    announcement_text = (
        f"🎉 The giveaway '{giveaway.title}' has ended! 🎉\n\n"
        f"Congratulations to {winner_username} for winning: {giveaway.description}!"
    )
    await bot.send_message(chat_id=chat_id, text=announcement_text)

    # Update the original giveaway message
    if giveaway.message_id:
        try:
            original_message_text = (
                f"🎉 **Giveaway Ended!** 🎉\n\n"
                f"**Title:** {giveaway.title}\n"
                f"**Description:** {giveaway.description}\n"
                f"**Ended:** {giveaway.end_date.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                f"🏆 **Winner:** {winner_username} 🏆"
            )
            await bot.edit_message_text(
                text=original_message_text,
                chat_id=chat_id, # Assuming giveaway message is in the same chat
                message_id=giveaway.message_id,
                reply_markup=None, # Remove the "Participate" button
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error updating original giveaway message {giveaway.message_id}: {e}")


async def check_ended_giveaways(application: Application):
    """Periodically checks for giveaways that have ended and selects a winner."""
    db = next(get_db())
    try:
        logger.info("Checking for ended giveaways...")
        # Fetch giveaways that have ended and no winner is selected yet
        ended_giveaways = db.query(giveaway_manager.Giveaway).filter(
            giveaway_manager.Giveaway.end_date <= datetime.utcnow(),
            giveaway_manager.Giveaway.winner_id == None
        ).all()

        if not ended_giveaways:
            logger.info("No ended giveaways found needing a winner.")
            return

        for giveaway in ended_giveaways:
            logger.info(f"Processing ended giveaway ID: {giveaway.id} - Title: {giveaway.title}")
            winner = giveaway_manager.select_winner(db, giveaway.id)
            if winner:
                logger.info(f"Winner selected for giveaway ID {giveaway.id}: User ID {winner.id}")
                # Assuming the giveaway was created in a chat, we need the chat_id.
                # This is a simplification. In a real bot, you'd store chat_id with the giveaway.
                # For now, we'll try to get it from the context if the bot is part of a group,
                # or we'd need a way to know where to announce it.
                # This example assumes the announcement is made in a pre-defined chat or the chat where command was issued.
                # We don't have direct access to 'chat_id' here without it being stored.
                # This is a conceptual placeholder. The giveaway message_id implies a chat_id.
                # We need to fetch the chat_id associated with giveaway.message_id
                # This part is tricky as APScheduler jobs don't have direct access to 'update.effective_chat.id'
                # A robust solution would be to store chat_id when the giveaway is created.
                # For now, we can't directly send a message without a chat_id.
                # Let's assume we will log it for now and figure out announcement channel later.

                # To properly announce, we need the chat_id where the giveaway message was sent.
                # This information should ideally be stored with the giveaway.
                # For now, we'll log. A practical implementation would need to resolve this.
                # If the bot is only used in one group, you could hardcode it or get from config.

                # A simplified approach: If we have context, we might get a chat_id.
                # However, application.bot does not directly give a chat_id.
                # We need to have stored the chat_id with the giveaway.
                # Let's assume for now that we will just log the winner.
                # A proper implementation would be:
                if giveaway.chat_id:
                    await announce_winner(application.bot, giveaway.chat_id, giveaway, winner)
                else:
                    logger.error(f"Cannot announce winner for giveaway {giveaway.id} because chat_id is missing.")

            else:
                logger.info(f"No winner could be selected for giveaway ID {giveaway.id} (e.g., no participants).")
                # Optionally, announce that no winner was chosen if there were no participants
                if giveaway.chat_id and giveaway.message_id:
                    try:
                        no_winner_text = (
                            f"😕 **Giveaway Ended** 😕\n\n"
                            f"**Title:** {giveaway.title}\n"
                            f"**Description:** {giveaway.description}\n"
                            f"**Ended:** {giveaway.end_date.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
                            f"No participants joined, so no winner could be selected."
                        )
                        await application.bot.edit_message_text(
                            text=no_winner_text,
                            chat_id=giveaway.chat_id,
                            message_id=giveaway.message_id,
                            reply_markup=None,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error updating giveaway message {giveaway.message_id} for no winner: {e}")
        db.commit()
    except Exception as e:
        logger.error(f"Error in check_ended_giveaways: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
