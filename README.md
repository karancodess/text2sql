# Text2SQL - Natural Language to Database Query Generator

A production-ready agentic Text-to-SQL application that converts natural language questions into executable SQL queries using AI agents and large language models.

## ✨ Features

- **5-Agent Workflow**: Planning → SQL Generation → Validation → Execution → Summarization
- **Multi-LLM Support**: OpenAI (GPT-3.5/GPT-4) or Google Gemini
- **FastAPI REST API**: Modern async API with comprehensive endpoints
- **PostgreSQL Database**: Full SQL support with Docker Compose
- **Web Interface**: Interactive HTML/CSS/JavaScript client
- **Docker Ready**: Complete containerization for easy deployment
- **Pydantic v2**: Modern Python configuration management
- **Production-Grade**: Error handling, logging, and validation

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- API Key (OpenAI or Google Gemini)

### Setup with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/karancodess/text2sql.git
cd text2sql

# Copy environment template and add your API key
cp app/.env.example app/.env
# Edit app/.env and add your OPENAI_API_KEY or GEMINI_API_KEY

# Start services
cd app
docker-compose up -d

# Access the application
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Streamlit UI: http://localhost:8501
```

### Local Development

```bash
# Install dependencies
pip install -r requirements-app.txt

# Set up environment
cp app/.env.example app/.env
# Edit app/.env with your API keys

# Run FastAPI server
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 API Endpoints

### Health Check
```bash
GET /health
```

### Submit Query
```bash
POST /query
Content-Type: application/json

{
  "query": "Show me all customers from France"
}
```

### Get Database Schema
```bash
GET /schema
```

### Interactive API Docs
```
http://localhost:8000/docs
```

## 🏗️ Architecture

The application implements a 5-agent workflow:

1. **Planner Agent** - Analyzes natural language query and creates execution plan
2. **SQL Generator** - Converts plan to optimized PostgreSQL query
3. **Validator Agent** - Validates SQL syntax and checks for destructive operations
4. **Executor Agent** - Safely executes query on database
5. **Summarizer Agent** - Formats results back to natural language

## 📁 Project Structure

```
text2sql/
├── app/                          # Main application
│   ├── agents/                   # 5 agent implementations
│   │   ├── llm.py               # LLM factory (OpenAI/Gemini)
│   │   ├── planner.py           # Planning agent
│   │   ├── sql_generator.py     # SQL generation
│   │   ├── validator.py         # SQL validation
│   │   ├── executor.py          # Query execution
│   │   └── summarizer.py        # Result summarization
│   ├── graph/
│   │   └── workflow.py          # Workflow orchestration
│   ├── tools/
│   │   └── db_tools.py          # Database utilities
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Pydantic v2 config
│   ├── db.py                    # Database initialization
│   ├── Dockerfile               # Container image
│   ├── docker-compose.yml       # PostgreSQL + App
│   └── requirements.txt         # Python dependencies
├── client.html                  # Web UI
├── test_application.py          # Test suite
├── QUICKSTART.md               # Quick start guide
├── PROJECT_SUMMARY.md          # Detailed overview
└── DEPLOYMENT.md               # Production deployment
```

## 🔧 Configuration

Create `app/.env` from template:

```env
# LLM Provider Configuration
LLM_PROVIDER=openai                    # or 'gemini'
LLM_MODEL=gpt-3.5-turbo               # OpenAI model
OPENAI_API_KEY=your_openai_key        # Required if using OpenAI
GEMINI_API_KEY=your_gemini_key        # Required if using Gemini

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/text2sql_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=text2sql_db

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_application.py

# Test API endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many customers do we have?"}'

# Check API health
curl http://localhost:8000/health
```

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Get running in 5 minutes
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - Complete technical overview
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide

## 🔐 Security

⚠️ **Important:**
- Never commit `.env` files with API keys
- Use environment variables for sensitive credentials
- Always enable the validator agent to prevent SQL injection
- Implement rate limiting in production
- Use HTTPS/SSL in production environments

## 🛠️ Technology Stack

| Component | Tech |
|-----------|------|
| **API Framework** | FastAPI 0.104.1 |
| **LLM Integration** | OpenAI API, Google Gemini |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy |
| **Config** | Pydantic v2.5.0 |
| **Containerization** | Docker & Docker Compose |
| **Web Frontend** | HTML5, CSS3, JavaScript |

## 💻 System Requirements

- **OS**: Linux, macOS, or Windows (WSL)
- **Docker**: v20.10+
- **Docker Compose**: v2.0+
- **Python**: 3.11+ (for local development)
- **Memory**: 2GB minimum, 4GB+ recommended
- **Disk**: 2GB free space

## 🚢 Deployment

### Docker Compose (Local/Development)
```bash
cd app
docker-compose up -d
```

### Production Checklist
- [ ] Set `DEBUG=false` in `.env`
- [ ] Configure production API keys
- [ ] Set up PostgreSQL backups
- [ ] Enable SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Use secrets management (not .env files)
- [ ] Configure CORS appropriately

## 📊 Example Usage

**Query**: "What are the top 5 products by revenue?"

**Workflow**:
```
1. Planner: Creates plan to fetch products sorted by revenue
2. SQL Generator: SELECT * FROM products ORDER BY revenue DESC LIMIT 5;
3. Validator: Checks syntax and safety ✓
4. Executor: Runs query, gets 5 products
5. Summarizer: Formats as natural language response
```

**Response**:
```json
{
  "final_answer": "The top 5 products by revenue are: 
    1. Classic Car Collection - $125,000
    2. Motorcycle Series - $98,500
    3. Vintage Trucks - $87,300
    4. Ships Collection - $76,200
    5. Trains Set - $65,100"
}
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE for details.

## 📞 Support & Issues

- **Bug Reports**: Open an issue on [GitHub Issues](https://github.com/karancodess/text2sql/issues)
- **Documentation**: See [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- **Quick Help**: Check [QUICKSTART.md](./QUICKSTART.md)

## 🎯 Roadmap

- [ ] Multi-database support (MySQL, Snowflake, BigQuery)
- [ ] Query optimization and performance analysis
- [ ] Caching layer for frequently used queries
- [ ] Advanced authentication and RBAC
- [ ] Web dashboard for query history
- [ ] Multi-turn conversation support
- [ ] Explain query functionality

---

**Built with ❤️ for making SQL accessible to everyone via natural language**

**Repository**: https://github.com/karancodess/text2sql

