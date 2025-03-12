from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging
from dotenv import load_dotenv
import os
from pubmed_crawler import PubMedCrawler
from summarizer import ArticleSummarizer
from storage import ArticleStorage

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
        self.storage = ArticleStorage()
        
        # Initialize the application
        self.application = Application.builder().token(self.telegram_token).build()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a welcome message when the command /start is issued."""
        welcome_message = (
            "👋 Welcome to the Medical Journal Crawler Bot!\n\n"
            "I can help you find and analyze medical research articles from PubMed.\n\n"
            "Available commands:\n"
            "/search <topic> - Search and store medical articles\n"
            "/ask <question> - Ask questions about stored articles\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(welcome_message)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a help message when the command /help is issued."""
        help_message = (
            "🔍 How to use this bot:\n\n"
            "1. First, search for articles on your topic:\n"
            "   /search diabetes treatment 2024\n\n"
            "2. Wait for the bot to crawl and store the articles\n\n"
            "3. Then ask questions about the articles:\n"
            "   /ask what are the latest advances in diabetes treatment?\n\n"
            "The bot will answer based on the stored articles.\n"
            "Your articles remain stored for future questions!"
        )
        await update.message.reply_text(help_message)

    async def search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /search command - crawl and store articles."""
        if not context.args:
            await update.message.reply_text(
                "Please provide a search topic.\n"
                "Example: /search diabetes treatment 2024"
            )
            return

        query = " ".join(context.args)
        status_message = await update.message.reply_text(
            f"🔍 Searching for articles about: {query}\n"
            "This may take a moment..."
        )

        try:
            # Search and store articles with cache disabled to force fresh results
            articles = self.pubmed_crawler.search_articles(query, max_results=10, use_cache=False)
            
            if not articles:
                await status_message.edit_text(
                    "No articles found for your search query. "
                    "Try different keywords or a broader search term."
                )
                return

            # Update status message with results
            response = (
                f"✅ Successfully stored {len(articles)} articles about '{query}'!\n\n"
                "You can now ask questions about these articles using:\n"
                "/ask <your question>\n\n"
                "For example:\n"
                f"/ask what are the main findings about {query}?"
            )
            await status_message.edit_text(response)

        except Exception as e:
            logger.error(f"Error processing search: {str(e)}")
            await status_message.edit_text(
                "Sorry, an error occurred while processing your search. "
                "Please try again later."
            )

    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /ask command - answer questions about stored articles."""
        if not context.args:
            await update.message.reply_text(
                "Please provide a question.\n"
                "Example: /ask what are the main findings?"
            )
            return

        question = " ".join(context.args)
        
        try:
            # Get relevant articles from storage
            articles = self.storage.get_articles_by_query("", limit=10)  # Get recent articles
            
            if not articles:
                await update.message.reply_text(
                    "No articles found in storage. "
                    "Please use /search <topic> to find articles first."
                )
                return

            # Format articles into a literature review style response
            message = self.summarizer.format_telegram_message(articles, question)
            
            # Send the response
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            await update.message.reply_text(
                "Sorry, an error occurred while processing your question. "
                "Please try again later."
            )

    def run(self):
        """Start the bot."""
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("search", self.search))
        self.application.add_handler(CommandHandler("ask", self.ask))

        # Start the bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES) 