from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
from dotenv import load_dotenv
import os
from pubmed_crawler import PubMedCrawler
from summarizer import ArticleSummarizer

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MedicalJournalBot:
    def __init__(self):
        load_dotenv()
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        self.pubmed_crawler = PubMedCrawler()
        self.summarizer = ArticleSummarizer()
        
        # Initialize the application
        self.application = Application.builder().token(self.telegram_token).build()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a welcome message when the command /start is issued."""
        welcome_message = (
            "👋 Welcome to the Medical Journal Crawler Bot!\n\n"
            "I can help you find and summarize medical research articles from PubMed.\n\n"
            "Available commands:\n"
            "/search <query> - Search for medical articles\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(welcome_message)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a help message when the command /help is issued."""
        help_message = (
            "🔍 How to use this bot:\n\n"
            "1. Use /search followed by your search query to find medical articles\n"
            "   Example: /search AI in cardiology\n\n"
            "2. The bot will provide a literature review style summary with:\n"
            "   • Article titles and authors\n"
            "   • Publication details\n"
            "   • Key findings\n"
            "   • Links to full papers\n\n"
            "3. You can search for any medical topic using keywords\n"
            "   Example: /search diabetes treatment 2024"
        )
        await update.message.reply_text(help_message)

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /search command."""
        if not context.args:
            await update.message.reply_text(
                "Please provide a search query.\n"
                "Example: /search AI in cardiology"
            )
            return

        query = " ".join(context.args)
        await update.message.reply_text(f"🔍 Searching for: {query}")

        try:
            # Search for articles
            articles = self.pubmed_crawler.search_articles(query, max_results=5)
            
            if not articles:
                await update.message.reply_text(
                    "No articles found for your search query. "
                    "Try different keywords or a broader search term."
                )
                return

            # Generate summaries for all articles
            for article in articles:
                article['summary'] = self.summarizer.summarize_article(article)

            # Format all articles into a single literature review style message
            message = self.summarizer.format_telegram_message(articles, query)
            
            # Send the literature review
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )

        except Exception as e:
            logger.error(f"Error processing search: {str(e)}")
            await update.message.reply_text(
                "Sorry, an error occurred while processing your search. "
                "Please try again later."
            )

    def run(self):
        """Start the bot."""
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("search", self.search))

        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES) 