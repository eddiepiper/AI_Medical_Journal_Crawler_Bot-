# Medical Journal Crawler Bot 🤖

A Telegram bot that provides concise literature reviews from PubMed articles using GPT-4 and BioBERT. The bot crawls medical journals, generates summaries, and delivers them in an easy-to-read format.

## ✨ Features

- 🔍 **Smart PubMed Search**: Search medical research articles using natural language queries
- 🤖 **AI-Powered Summaries**: Concise, one-sentence summaries of key findings using GPT-4
- 📚 **Literature Review Format**: Clean, organized presentation of multiple articles
- 🔄 **Real-time Updates**: Get the latest research as soon as it's published
- 🌐 **Direct Paper Links**: Quick access to full papers on PubMed
- 🛡️ **Rate Limiting**: Compliant with PubMed API guidelines
- 🐳 **Docker Support**: Easy deployment with containerization

## 🚀 Quick Start

1. **Prerequisites**
   - Docker and Docker Compose
   - Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
   - OpenAI API Key
   - PubMed Email and API Key (optional but recommended)

2. **Setup**
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd medical-journal-crawler

   # Configure environment variables
   cp .env.template .env
   # Edit .env with your credentials:
   # - TELEGRAM_BOT_TOKEN
   # - OPENAI_API_KEY
   # - PUBMED_EMAIL
   # - PUBMED_API_KEY

   # Start the bot
   docker-compose up --build
   ```

3. **Usage**
   - Start a chat with your bot on Telegram
   - Available commands:
     ```
     /start - Initialize the bot
     /help  - Show usage instructions
     /search <query> - Search for medical articles
     ```
   - Example searches:
     ```
     /search AI in cardiology 2024
     /search CRISPR cancer therapy
     /search diabetes treatment advances
     ```

## 📝 Example Output

```
📚 Literature Review: AI in cardiology

1. *Title of the First Paper*
   Authors et al. (2024) - Journal Name
   Key finding: One-sentence summary of the main findings.
   [Read Paper](https://pubmed.ncbi.nlm.nih.gov/...)

2. *Title of the Second Paper*
   Authors et al. (2024) - Journal Name
   Key finding: One-sentence summary of the main findings.
   [Read Paper](https://pubmed.ncbi.nlm.nih.gov/...)
```

## 🏗️ Project Structure

```
medical-journal-crawler/
├── Dockerfile              # Container configuration
├── docker-compose.yml      # Docker services setup
├── requirements.txt        # Python dependencies
├── .env.template           # Environment variables template
├── main.py                # Application entry point
├── pubmed_crawler.py      # PubMed API integration
├── summarizer.py          # GPT-4 summarization logic
└── telegram_bot.py        # Telegram bot implementation
```

## 🛠️ Development

1. **Local Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Run locally
   python main.py
   ```

2. **Environment Variables**
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PUBMED_EMAIL`: Your email for PubMed API
   - `PUBMED_API_KEY`: Your PubMed API key (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [PubMed Central API](https://www.ncbi.nlm.nih.gov/pmc/tools/developers/)
- [OpenAI GPT-4](https://openai.com/gpt-4)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [LangChain](https://www.langchain.com/)
- [BioBERT](https://github.com/dmis-lab/biobert)

## 📞 Support

If you encounter any issues or have questions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include logs and steps to reproduce the problem 