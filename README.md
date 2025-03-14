# Medical Journal Crawler Bot 🤖

A Telegram bot that provides comprehensive literature reviews from PubMed articles using GPT-4 and semantic search. The bot crawls medical journals, generates summaries, and delivers them in an easy-to-read format.

## ✨ Features

- 🔍 **Smart PubMed Search**: Search medical research articles using natural language queries
- 🤖 **AI-Powered Analysis**: Comprehensive analysis of research findings using GPT-4
- 📚 **Semantic Search**: Find relevant articles using natural language understanding
- 🔄 **Real-time Updates**: Get the latest research as soon as it's published
- 🌐 **Direct Paper Links**: Quick access to full papers on PubMed
- 🛡️ **Rate Limiting**: Compliant with PubMed API guidelines
- 🐳 **Docker Support**: Easy deployment with containerization
- 💾 **Caching System**: Efficient storage and retrieval of article data
- 🔎 **Advanced Filtering**: Filter results by date, journal, and relevance

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
     /ask <question> - Ask questions about the search results
     ```
   - Example searches:
     ```
     /search lymphoma treatment advances 2024
     /search immunotherapy cancer
     /search diabetes management
     /ask what are the main findings about lymphoma?
     ```

## 📝 Example Output

```
🔍 Search Results: Lymphoma Treatment

1. *Lymphoma: The Added Value of Radiomics, Volumes and Global Disease Assessment*
   Chauvie et al. (2024) - PET clinics
   Key findings:
   - Focuses on three prevalent subtypes: Hodgkin lymphoma, diffuse large B-cell lymphomas, and follicular lymphoma
   - Emphasizes identifying high-risk individuals for personalized treatment
   [Read Paper](https://pubmed.ncbi.nlm.nih.gov/38910057/)

2. *Lymphoma for the acute physician: diagnostic challenges and initial treatment decisions*
   Henderson et al. (2024) - British journal of hospital medicine
   Key findings:
   - Covers emergency presentations and novel treatment options
   - Discusses tumor lysis syndrome and mediastinal mass management
   [Read Paper](https://pubmed.ncbi.nlm.nih.gov/38941979/)
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
├── telegram_bot.py        # Telegram bot implementation
├── vector_store.py        # Vector database for semantic search
└── test_crawler.py        # Test suite for crawler functionality
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
- [Sentence Transformers](https://www.sbert.net/)

## 📞 Support

If you encounter any issues or have questions, please:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include logs and steps to reproduce the problem 