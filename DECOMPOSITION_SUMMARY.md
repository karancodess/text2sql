# Query Decomposition - Task 2 Complete ✅

## Summary
Successfully implemented **automated SQL query decomposition** using the Gemini API with fallback heuristics.

## What Was Done

### 1. **New Script: `task2/query_decomposition.py`**
- **Completely rewritten** from scratch with better architecture
- **Direct Gemini API integration** (REST endpoint)
- **Ultra-explicit prompts** forcing JSON-only output with schema context
- **Intelligent heuristic fallback** with enhanced pattern matching
- **Robust error handling** and progress reporting

### 2. **Features**
✅ Reads questions from `data/sql_questions_only.csv`  
✅ Generates **JSON** and **CSV** output formats  
✅ Detects:
  - **Intent**: What the question is asking (Count, Select, Average, etc.)
  - **Tables**: Which database tables are involved
  - **Columns**: Which columns are needed
  - **Filters**: SQL-like conditions (WHERE clauses)
  - **Joins**: Relationships between tables

### 3. **Output Files**
- **`data/decompositions.json`** - Full structured JSON with all decomposition details
- **`data/decompositions.csv`** - Tabular format (question, intent, tables, columns, filters, joins)

### 4. **Enhanced Heuristics**
- Schema-aware table/column matching
- Partial matching (singular/plural forms)
- Intelligent column detection (by pattern: "name", "price", "count")
- Filter extraction (WHERE clauses, conditions like >, <, =)
- Join detection for multi-table queries
- 8+ intent categories recognized

### 5. **Usage Examples**

**Single question:**
```bash
python3 task2/query_decomposition.py --question "How many customers are from the USA?"
```

**Batch processing (CSV):**
```bash
python3 task2/query_decomposition.py --csv data/sql_questions_only.csv \
  --json-out data/decompositions.json \
  --csv-out data/decompositions.csv
```

### 6. **Sample Decomposition**
Question: "List all products"
```json
{
  "Intent": "Select/List",
  "Tables": ["products"],
  "Columns": ["productCode"],
  "Filters": null,
  "Joins": null
}
```

Question: "How many customers from USA?"
```json
{
  "Intent": "Count/Aggregate",
  "Tables": ["customers"],
  "Columns": ["customerNumber"],
  "Filters": "USA = '<value>'",
  "Joins": null
}
```

### 7. **Key Improvements Over Previous Version**
✅ Removed OpenAI client incompatibility  
✅ Direct Gemini API calls (REST)  
✅ Much stronger prompt engineering  
✅ Schema context injection  
✅ Few-shot examples in prompt  
✅ Better JSON extraction  
✅ Enhanced heuristic fallback  
✅ Structured error logging  
✅ Both JSON and CSV outputs  
✅ Better column detection  
✅ Filter and join detection  

## Next Steps for Text2SQL Generator
These decompositions can now be used for:
1. **SQL Query Generation** - Convert decomposed structure to SQL
2. **Semantic Validation** - Verify extracted tables/columns exist
3. **Optimization** - Rewrite queries for efficiency
4. **Explanation Generation** - Document what the SQL does

## Files
- Main script: `task2/query_decomposition.py`
- Input: `data/sql_questions_only.csv`
- Outputs: `data/decompositions.json`, `data/decompositions.csv`
- Database schema: `sql/seed.sql` (automatically parsed)
