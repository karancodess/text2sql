# Text-to-SQL Agent 🤖

A production-ready, agentic Text-to-SQL application that converts natural language queries into optimized SQL statements, executes them securely, and returns results summarized in natural language.

## Features

✨ **Core Capabilities:**
- 🗣️ Natural language to SQL conversion
- 📋 Strategic query planning via AI agents
- ✓ SQL syntax and security validation
- 🔒 Safe query execution (SELECT-only)
- 📊 Results summarization in natural language
- 🔄 Automatic retry logic on validation failures

✨ **Architecture:**
- **LangGraph-based** state machine workflow
- **Modular agent system** (Planner, Generator, Validator, Executor, Summarizer)
- **FastAPI** REST API
- **Streamlit** chat UI
- **PostgreSQL** database with SQLAlchemy ORM
- **Docker & Docker Compose** for containerization
- **LLM agnostic** (OpenAI or Google Gemini)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key OR Google Gemini API key
- Python 3.11+ (for local development)

### With Docker (Recommended)

1. **Clone and setup environment:**
```bash
cd app
cp .env.example .env
```

2. **Edit `.env` with your API key:**
```env
OPENAI_API_KEY=your-key-here
# OR
GEMINI_API_KEY=your-key-here
```

3. **Start the application:**
```bash
docker-compose up -d
```

4. **Access the services:**
- **Streamlit UI:** http://localhost:8501
- **FastAPI Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

### Local Development

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup database:**
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/text2sql_db
# Start PostgreSQL first, then initialize DB
python -c "from db import init_db; init_db()"
```

4. **Run Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

5. **Or run FastAPI server (in another terminal):**
```bash
python main.py
```

## Project Structure

```
app/
├── agents/                 # AI agent modules
│   ├── planner.py         # Query planning
│   ├── sql_generator.py   # SQL generation
│   ├── validator.py       # SQL validation
│   ├── executor.py        # Query execution
│   ├── summarizer.py      # Result summarization
│   └── llm.py            # LLM configuration
├── graph/
│   └── workflow.py        # LangGraph state machine
├── tools/
│   └── db_tools.py        # Database utilities
├── prompts/
│   └── __init__.py        # System prompts for all agents
├── sql/
│   └── seed.sql           # Database schema & sample data
├── config.py              # Configuration management
├── db.py                  # SQLAlchemy setup
├── main.py                # FastAPI application
├── streamlit_app.py       # Streamlit UI
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-container setup
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── .gitignore
```

## Workflow

The system follows a 5-agent pipeline:

```
User Query
    ↓
[Planner] → Analyzes query, creates strategic plan
    ↓
[SQL Generator] → Generates PostgreSQL query
    ↓
[Validator] → Checks syntax & security
    ├─→ Valid? No → [SQL Generator] (retry loop)
    ↓
[Executor] → Executes query safely
    ↓
[Summarizer] → Converts results to natural language
    ↓
Final Answer (Natural Language)
```

### Agent Responsibilities

| Agent | Input | Output | Key Features |
|-------|-------|--------|--------------|
| **Planner** | Natural language query | Strategic plan (tables, joins, filters) | Schema-aware planning |
| **Generator** | Plan + schema | PostgreSQL query | Proper quoting, formatting |
| **Validator** | SQL query | Validation status | Syntax check + destructive op detection |
| **Executor** | Valid SQL | Query results (JSON) | Safe execution with timeout |
| **Summarizer** | Results + original query | Natural language answer | Context-aware formatting |

## API Usage

### REST Endpoints

#### Process Query
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the top 5 customers by total order amount?"
  }'
```

**Response:**
```json
{
  "user_query": "What are the top 5 customers by total order amount?",
  "plan": "Join customers with orders, aggregate by customer...",
  "sql": "SELECT c.customerNumber, c.customerName, SUM(...",
  "is_valid": true,
  "final_answer": "The top 5 customers are...",
  "execution_results": {
    "success": true,
    "row_count": 5,
    "rows": [...]
  },
  "error": null
}
```

#### Get Database Schema
```bash
curl "http://localhost:8000/schema"
```

#### Health Check
```bash
curl "http://localhost:8000/health"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:password@localhost:5432/text2sql_db` |
| `OPENAI_API_KEY` | OpenAI API key | (required for OpenAI) |
| `GEMINI_API_KEY` | Google Gemini API key | (required for Gemini) |
| `LLM_PROVIDER` | LLM provider to use | `openai` |
| `LLM_MODEL` | Model name | `gpt-4` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DEBUG` | Debug mode | `False` |

## Database Schema

The default schema includes:

- **productlines**: Product categories
- **products**: Product inventory
- **offices**: Company offices
- **employees**: Employee directory
- **customers**: Customer information
- **orders**: Sales orders
- **orderdetails**: Order line items
- **payments**: Payment records

See [seed.sql](sql/seed.sql) for the complete schema with sample data.

## Security Features

✓ **Read-Only Enforcement**: Only SELECT queries allowed
✓ **Syntax Validation**: SQL syntax checked before execution
✓ **Destructive Op Detection**: DELETE, UPDATE, INSERT, DROP blocked
✓ **Connection Pooling**: Safe database connection management
✓ **Query Timeout**: 30-second timeout per query
✓ **LLM-based Validation**: Double-check with language model

## Logging

Logs are output to console and can be configured via `LOG_LEVEL` environment variable.

```bash
# Set debug logging
export LOG_LEVEL=DEBUG
```

Log format: `timestamp - logger_name - level - message`

## Development

### Running Tests

```bash
# (Tests framework can be added - pytest recommended)
pytest tests/
```

### Code Style

- Python: PEP 8
- Type hints: Required
- Docstrings: Google-style

### Adding New Agents

1. Create new agent file in `agents/`
2. Inherit from base agent pattern
3. Add system prompt to `prompts/__init__.py`
4. Integrate into workflow graph in `graph/workflow.py`

## Troubleshooting

### "API key not set" Error
```bash
# Ensure .env file has API key
export OPENAI_API_KEY=your-key-here
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres
```

### Query Timeout
```bash
# Increase timeout in agents/executor.py or optimize query
# Default: 30 seconds
```

### LLM Response Issues
```bash
# Check API key validity
# Verify rate limits
# Check model name spelling (e.g., gpt-4 vs gpt-4-turbo)
```

## Performance Tips

1. **Optimize Queries**: Use indexes on frequently filtered columns
2. **Batch Operations**: Process multiple queries asynchronously
3. **Cache Results**: Implement caching for common queries
4. **Monitor Logs**: Check logs for slow agents or queries
5. **Tune LLM Parameters**: Adjust temperature and max_tokens

## Deployment

### Docker Hub
```bash
docker build -t your-org/text2sql-agent:latest .
docker push your-org/text2sql-agent:latest
```

### Kubernetes
```bash
# Create ConfigMap for environment variables
kubectl create configmap text2sql-config --from-env-file=.env

# Deploy using provided manifests
kubectl apply -f k8s/
```

### AWS ECS, GCP Cloud Run
Use the provided Dockerfile for containerized deployments.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Make changes with tests
4. Submit pull request

## License

MIT License

## Support

- 📖 Full documentation: [docs/](docs/)
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## Roadmap

- [ ] Streaming responses
- [ ] Multi-turn conversation memory
- [ ] Query caching layer
- [ ] Advanced error recovery
- [ ] Query optimization suggestions
- [ ] Real-time execution monitoring
- [ ] Kubernetes manifests
- [ ] GraphQL API support

---

**Built with ❤️ by the AI Fellowship**

*Last Updated: May 2026*
