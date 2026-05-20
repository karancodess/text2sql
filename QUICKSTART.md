# Quick Start Guide - Text2SQL Application

## Overview
This is a production-ready, agentic Text-to-SQL application that converts natural language queries into optimized SQL queries using a 5-agent workflow with an LLM orchestrator.

## Prerequisites

### Required
- Python 3.10+
- PostgreSQL 15+ (running and accessible)
- One of:
  - OpenAI API key (ChatGPT-4o/3.5-turbo)
  - Google Gemini API key

### Optional
- Docker & Docker Compose (for containerized deployment)
- Streamlit (for interactive UI)

## Installation

### 1. Clone/Navigate to Project
```bash
cd app
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add:
OPENAI_API_KEY=sk-...  # OR GEMINI_API_KEY=AIz...
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
LLM_PROVIDER=openai  # or 'gemini'
LLM_MODEL=gpt-4o  # or 'gemini-pro'
```

### 5. Set Up Database
```bash
# Option A: Using Docker Compose
docker-compose up -d

# Option B: Manual PostgreSQL
# 1. Create database
createdb text2sql_db

# 2. Load schema
psql -U postgres -d text2sql_db -f sql/seed.sql
```

## Running the Application

### Option 1: REST API (FastAPI)
```bash
# Start API server on http://localhost:8000
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Example request:
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the top 5 customers by order amount"
  }'
```

### Option 2: Interactive Chat UI (Streamlit)
```bash
# Start Streamlit app on http://localhost:8501
streamlit run streamlit_app.py
```

### Option 3: Docker Compose
```bash
# Start entire stack (PostgreSQL + FastAPI + Streamlit)
docker-compose up

# Access:
# - API: http://localhost:8000
# - Streamlit: http://localhost:8501
```

## Testing

### Run Test Suite
```bash
python3 test_application.py
```

### Test Specific Modules
```bash
# Test imports
python3 -c "from agents.llm import get_llm; print('✓ LLM module OK')"

# Test agent initialization
python3 -c "from agents.planner import PlannerAgent; a = PlannerAgent(); print('✓ Agent OK')"

# Test workflow
python3 -c "from graph.workflow import Text2SQLWorkflow; w = Text2SQLWorkflow(); print('✓ Workflow OK')"
```

## Example Queries

Try these natural language queries:

1. **Simple Selection**
   ```
   "Show all products in the 'Classic Cars' product line"
   ```

2. **Aggregation**
   ```
   "What is the total order value by customer?"
   ```

3. **Complex Join**
   ```
   "List employees and the number of customers they manage"
   ```

4. **Filtering & Sorting**
   ```
   "Show me the top 10 products by sales revenue"
   ```

5. **Time-based Query**
   ```
   "How many orders were placed in the last quarter?"
   ```

## Architecture

```
User Query (Natural Language)
        ↓
  [Planner Agent]
  Analyzes query and creates a strategic database access plan
        ↓
  [SQL Generator Agent]
  Converts plan to optimized PostgreSQL query
        ↓
  [Validator Agent]
  Checks SQL syntax, security, and validates against schema
        ↓
  [Executor Agent]
  Executes validated query against PostgreSQL database
        ↓
  [Summarizer Agent]
  Converts database results back to natural language
        ↓
   Answer (Natural Language)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Submit a natural language query |
| `/schema` | GET | Get database schema information |
| `/health` | GET | Check API health |
| `/` | GET | API documentation |

### Example Request
```json
POST /query
{
  "query": "How many customers are from California?"
}
```

### Example Response
```json
{
  "user_query": "How many customers are from California?",
  "plan": "Relevant Tables: customers\nFilter: state = 'CA'\nAggregation: COUNT(*)",
  "sql": "SELECT COUNT(*) as customer_count FROM customers WHERE state = 'CA'",
  "is_valid": true,
  "execution_results": {
    "success": true,
    "row_count": 1,
    "rows": [{"customer_count": 5}]
  },
  "final_answer": "There are 5 customers from California."
}
```

## Configuration

### Environment Variables
```env
# LLM Configuration
LLM_PROVIDER=openai              # 'openai' or 'gemini'
LLM_MODEL=gpt-4o                # Model name
OPENAI_API_KEY=sk-...           # OpenAI key (if using OpenAI)
GEMINI_API_KEY=AIz...           # Google key (if using Gemini)

# Database Configuration
DATABASE_URL=postgresql://...
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=text2sql_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"
**Solution**: Set your API key in `.env` file or environment
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### Issue: Database connection failed
**Solution**: Verify PostgreSQL is running and credentials are correct
```bash
psql -h localhost -U postgres -d text2sql_db
```

### Issue: Port already in use
**Solution**: Use a different port
```bash
uvicorn main:app --port 8080
# or
streamlit run streamlit_app.py --server.port 8502
```

### Issue: Module import errors
**Solution**: Reinstall dependencies
```bash
pip install --upgrade -r requirements.txt
```

## Project Structure

```
.
├── agents/              # Agent implementations
│   ├── planner.py       # Query planning agent
│   ├── sql_generator.py # SQL generation agent
│   ├── validator.py     # SQL validation agent
│   ├── executor.py      # Query execution agent
│   ├── summarizer.py    # Result summarization agent
│   └── llm.py           # LLM wrapper (OpenAI/Gemini)
├── graph/
│   └── workflow.py      # Orchestration workflow
├── tools/
│   └── db_tools.py      # Database utilities
├── prompts/
│   └── __init__.py      # System prompts for agents
├── sql/
│   └── seed.sql         # Database schema & sample data
├── main.py              # FastAPI REST API
├── streamlit_app.py     # Streamlit UI
├── config.py            # Configuration management
├── db.py                # Database connections
└── requirements.txt     # Python dependencies
```

## Performance Notes

- First query may take 3-5 seconds (LLM inference)
- Subsequent queries cached (~2-3 seconds)
- Database queries execute in <100ms
- Plan generation: ~2-3 seconds
- Validation: ~1 second
- Summarization: ~1-2 seconds

## Security Considerations

✅ **Implemented**
- SQL injection prevention via parameterized queries
- Destructive operation detection (DELETE, DROP, etc.)
- Read-only access enforced
- Request validation

⚠️ **Additional Recommendations**
- Use API authentication in production
- Implement rate limiting
- Run in VPC/private network
- Use connection pooling for databases
- Enable query logging/audit trails

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs: `tail -f app.log`
3. Run test suite: `python3 test_application.py`
4. Check database connection: `psql --version`

## License

[Specify your license here]

## Contributors

[List contributors]
