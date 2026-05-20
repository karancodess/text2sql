# Text-to-SQL Agent - Implementation Guide

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                     │
│  ┌──────────────────────┐          ┌─────────────────────────┐  │
│  │  Streamlit Chat UI   │          │    FastAPI REST API     │  │
│  │  (port 8501)         │          │    (port 8000)          │  │
│  └──────────────────────┘          └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Workflow Orchestration                      │
│              (LangGraph State Machine / Graph)                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐ │
│  │ Planner  │ → │Generator │ → │Validator  │ → │Executor  │ │
│  └──────────┘    └──────────┘    └───────────┘    └──────────┘ │
│       ↓              ↓                ↑ (retry)         ↓        │
│    [Plan]       [SQL Query]      [Valid?]        [Results]      │
│                                                      ↓            │
│                                             ┌──────────────┐     │
│                                             │  Summarizer  │     │
│                                             └──────────────┘     │
│                                                    ↓              │
│                                           [Natural Language]     │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Data & Tools Layer                           │
│  ┌────────────────────┐              ┌───────────────────────┐  │
│  │  Database Tools    │              │   LLM Integration     │  │
│  │  (SQLAlchemy)      │              │  (OpenAI/Gemini)      │  │
│  └────────────────────┘              └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌────────────────────┐              ┌───────────────────────┐  │
│  │  PostgreSQL DB     │              │  OpenAI / Gemini API  │  │
│  │  (port 5432)       │              │  (REST APIs)          │  │
│  └────────────────────┘              └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Agents Module (`agents/`)

#### Planner Agent (`planner.py`)
**Responsibility:** Analyze user query and create strategic database access plan

**Key Functions:**
- Identifies relevant tables from schema
- Determines necessary JOINs
- Identifies WHERE clause conditions
- Notes special requirements (GROUP BY, aggregations, etc.)

**Flow:**
```
User Query → LLM Analysis → Strategic Plan
```

**Example Output:**
```
Relevant Tables: orders, customers, orderdetails
Join Conditions: orders.customerNumber = customers.customerNumber
                orderdetails.orderNumber = orders.orderNumber
Filter Conditions: orderDate > '2023-01-01'
Aggregations: SUM(priceEach * quantityOrdered)
Sorting: ORDER BY total_amount DESC
Special: DISTINCT customer names, LIMIT 10
```

#### SQL Generator Agent (`sql_generator.py`)
**Responsibility:** Generate PostgreSQL queries from plans

**Key Features:**
- Proper quoting of identifiers (handles camelCase)
- Optimized query structure
- Clear formatting for readability
- PostgreSQL-specific syntax

**Important Details:**
- Quotes all column names: `SELECT "customerNumber" FROM customers`
- Uses explicit JOINs for clarity
- Includes table aliases for readability
- Handles NULL comparisons correctly

#### Validator Agent (`validator.py`)
**Responsibility:** Validate SQL syntax and security

**Validation Checks:**
1. **Syntax Check**: Valid PostgreSQL syntax
2. **Destructive Operations**: Blocks DELETE, UPDATE, INSERT, DROP, ALTER, CREATE
3. **Security Check**: No dangerous patterns

**Retry Loop:**
- If validation fails, error feedback is sent back to Generator
- Generator attempts to fix the query
- Maximum 3 retries to prevent infinite loops

#### Executor Agent (`executor.py`)
**Responsibility:** Execute validated queries safely

**Safety Features:**
- 30-second query timeout
- Connection pooling
- Error handling and reporting
- Results returned as JSON

#### Summarizer Agent (`summarizer.py`)
**Responsibility:** Convert raw results to natural language

**Process:**
1. Takes original user query (for context)
2. Analyzes database results
3. Generates friendly, informative response
4. Handles empty results gracefully

### 2. Workflow (`graph/workflow.py`)

**Design Pattern:** LangGraph State Machine

**State Object:**
```python
WorkflowState = {
    "user_query": str,
    "plan": str,
    "sql": str,
    "is_valid": bool,
    "execution_results": Dict,
    "final_answer": str,
    "error": str,
    "retry_count": int
}
```

**Node Flow:**
```
START
  ↓
[PLANNER] → plan the query
  ↓
[GENERATOR] → generate SQL
  ↓
[VALIDATOR] ← conditional branch
  ├─ is_valid=True → [EXECUTOR]
  └─ is_valid=False → [GENERATOR] (retry)
  ↓
[EXECUTOR] → run query
  ↓
[SUMMARIZER] → generate answer
  ↓
END
```

### 3. Database Layer

#### Configuration (`config.py`)
- Pydantic-based settings management
- Environment variable loading
- Support for multiple LLM providers

#### Database Setup (`db.py`)
- SQLAlchemy engine creation
- Connection pooling
- Session management
- Database initialization from seed.sql

#### Database Tools (`tools/db_tools.py`)
**Key Functions:**
- `execute_query()`: Execute SQL safely with timeout
- `get_database_schema()`: Retrieve schema metadata
- `validate_query_syntax()`: Check SQL syntax
- `check_destructive_operations()`: Security check

### 4. LLM Integration (`agents/llm.py`)

**Factory Pattern:** Singleton LLM instance

**Supported Providers:**
- OpenAI (gpt-4, gpt-3.5-turbo, etc.)
- Google Gemini (gemini-pro, etc.)

**Configuration:**
```python
llm = get_llm()  # Returns initialized LLM
```

### 5. System Prompts (`prompts/__init__.py`)

**Five Core Prompts:**
1. **PLANNER_SYSTEM_PROMPT**: Strategic analysis
2. **SQL_GENERATOR_SYSTEM_PROMPT**: SQL generation rules
3. **VALIDATOR_SYSTEM_PROMPT**: Validation criteria
4. **EXECUTOR_SYSTEM_PROMPT**: Execution guidelines
5. **SUMMARIZER_SYSTEM_PROMPT**: Natural language formatting

**Prompt Design:**
- Schema context included in all prompts
- Clear instructions and examples
- Expected output format specified
- Security constraints highlighted

### 6. User Interfaces

#### FastAPI (`main.py`)
- **`POST /query`**: Process a natural language query
- **`GET /schema`**: Retrieve database schema
- **`GET /health`**: Health check
- **`GET /`**: API information

**Request Example:**
```bash
POST /query
{
  "query": "What are the top 5 customers by order count?"
}
```

**Response Example:**
```json
{
  "user_query": "What are the top 5 customers by order count?",
  "plan": "Join customers with orders...",
  "sql": "SELECT c.customerNumber, c.customerName, COUNT(...)",
  "is_valid": true,
  "final_answer": "The top 5 customers are...",
  "execution_results": {...},
  "error": null
}
```

#### Streamlit (`streamlit_app.py`)
- **Chat Tab**: Input queries and see results
- **Results Tab**: View detailed execution results
- **History Tab**: Browse past queries
- **Sidebar**: Configuration and information

**Features:**
- Real-time chat interface
- Expandable execution details
- Query history with replay
- Results displayed as dataframes

### 7. Containerization

#### Dockerfile
```dockerfile
FROM python:3.11-slim
# - Multi-stage build optimized
# - Health checks configured
# - Minimal attack surface
```

#### Docker Compose
```yaml
services:
  postgres:
    - PostgreSQL 15 Alpine
    - Auto-initialization with seed.sql
    - Health checks
    - Volume persistence
  
  app:
    - Python application
    - Both Streamlit and FastAPI
    - Environment variable injection
    - Depends on postgres (healthcheck)
```

## Design Decisions

### 1. **State Machine Approach**
**Why LangGraph?**
- Explicit state management
- Clear retry logic
- Easy to visualize execution
- Production-ready error handling

### 2. **Agent Separation**
**Why split into 5 agents?**
- Single Responsibility Principle
- Each agent can be tested independently
- Easy to replace individual agents
- Clear error attribution
- Reusable prompts

### 3. **PostgreSQL Quoting**
**Why quote identifiers?**
- Database schema uses camelCase (`customerNumber`)
- PostgreSQL lowercases unquoted identifiers
- Quoting preserves case and handles special chars

### 4. **Read-Only Enforcement**
**Why block destructive operations?**
- Safety first - prevent accidental data loss
- Security - prevent malicious queries
- Multi-layer validation (regex + LLM)

### 5. **Retry Loop Only in Validator**
**Why not retry elsewhere?**
- Generator is most likely to be incorrect
- Other agents are either data-dependent or deterministic
- Prevents infinite loops with MAX_RETRIES

## Error Handling Flow

```
Error Type          → Handler                 → Recovery
─────────────────────────────────────────────────────────
Planning failed     → Log error, continue     → Generate SQL anyway
SQL syntax error    → Validator catches       → Retry with feedback
Security violation  → Validator catches       → Block & error
DB connection fail  → Executor catches        → Report error
Query timeout       → Executor catches        → Report error
LLM API error       → Agent catches           → Return error
```

## Security Architecture

### Layer 1: Prompt-Level Security
- System prompts explicitly forbid destructive operations
- LLM trained to understand security constraints

### Layer 2: Code-Level Security
- `check_destructive_operations()` regex check
- SQL keywords blocklist: DELETE, UPDATE, INSERT, DROP, ALTER, CREATE

### Layer 3: Validation-Level Security
- LLM-based validator double-checks
- Returns security issues in validation response

### Layer 4: Execution-Level Security
- Connection pooling prevents connection exhaustion
- 30-second query timeout prevents resource hogging
- Read-only database user (recommended in production)

## Performance Considerations

### Query Optimization
- Proper indexing on frequently filtered columns
- JOIN optimization by database planner
- Result pagination for large datasets

### LLM Efficiency
- Caching of prompts when possible
- Batch processing support (future)
- Token usage monitoring (can be added)

### Database Performance
- Connection pooling with NullPool for containers
- Indexes on foreign keys and commonly filtered columns
- ANALYZE table statistics for optimal planning

## Extensibility

### Adding New Agents
1. Create file: `agents/new_agent.py`
2. Add system prompt to `prompts/__init__.py`
3. Implement agent class with `process()` method
4. Add node to `workflow.py` graph

### Adding New Database
1. Modify `seed.sql` with new schema
2. Update schema context in `prompts/__init__.py`
3. Agents automatically adapt to schema changes

### Supporting New LLM Providers
1. Add provider case to `llm.py` factory
2. Implement language model integration
3. Update `config.py` with new environment variables

## Monitoring & Observability

### Logging Strategy
- Each agent logs key decisions
- Workflow logs execution flow
- Database tools log queries and results
- Structured logging format: `timestamp - logger - level - message`

### Debugging
- `DEBUG=True` enables SQL echo and LLM details
- Check `logs/` directory for persistent logs
- Use `docker-compose logs` to view container logs

### Metrics to Monitor
- Query success rate
- Average execution time per agent
- LLM token usage (cost)
- Database connection pool utilization
- Error categories and frequency

## Testing Strategy (Recommended)

### Unit Tests
- Individual agent functionality
- Database tool operations
- Configuration loading

### Integration Tests
- Full workflow execution
- Workflow retry logic
- Error handling

### End-to-End Tests
- API endpoint testing
- Streamlit UI interaction
- Docker compose deployment

## Production Checklist

- [ ] Environment variables properly configured
- [ ] Database backups scheduled
- [ ] API rate limiting implemented
- [ ] Authentication added (if multi-user)
- [ ] HTTPS enabled for API
- [ ] Logging aggregation configured
- [ ] Error alerting setup
- [ ] Database indexes optimized
- [ ] Connection pool sizes tuned
- [ ] LLM API quotas managed
- [ ] Regular security audits
- [ ] Disaster recovery plan documented

## Future Enhancements

1. **Query Caching**: Cache frequent queries
2. **Multi-turn Conversation**: Maintain conversation history
3. **Query Optimization**: Suggest index improvements
4. **Advanced Retry**: Different retry strategies per agent
5. **Streaming Responses**: Stream results as they arrive
6. **GraphQL API**: Add GraphQL interface
7. **Query Explanation**: Explain generated SQL
8. **Performance Analytics**: Query performance metrics
9. **Custom Agents**: Support user-defined agents
10. **Webhook Integrations**: Trigger external systems

---

**Architecture Last Updated: May 2026**
