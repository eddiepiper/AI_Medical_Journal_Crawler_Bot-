from telegram_bot import MedicalJournalBot
import logging

def main():
    """Main entry point for the application."""
    try:
        # Initialize and run the bot
        bot = MedicalJournalBot()
        logging.info("Starting Medical Journal Crawler Bot...")
        bot.run()
    except Exception as e:
        logging.error(f"Error starting bot: {str(e)}")
        raise

if __name__ == "__main__":
    main() 