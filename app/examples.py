"""
Example Usage - Text-to-SQL Agent

This module demonstrates how to use the Text-to-SQL agent
programmatically in your own applications.
"""

import logging
import asyncio
import json
from typing import Dict, Any
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Using the Workflow Directly (Python)
# ============================================================================

def example_direct_workflow():
    """
    Use the workflow directly in Python without HTTP.
    Best for: Server-side applications, batch processing.
    """
    from graph.workflow import Text2SQLWorkflow
    
    # Initialize workflow
    workflow = Text2SQLWorkflow()
    
    # Sample queries
    queries = [
        "What are the top 5 customers by total order amount?",
        "Which products are out of stock?",
        "How many orders were placed in each month of 2023?",
        "List all employees in the Paris office with their job titles.",
        "What is the average order value per customer?",
    ]
    
    for query in queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        result = workflow.run(query)
        
        print(f"\n✓ Generated SQL:\n{result['sql']}")
        print(f"\n✓ Valid: {result['is_valid']}")
        print(f"\n✓ Answer:\n{result['final_answer']}")
        
        if result['error']:
            print(f"\n⚠ Error: {result['error']}")


# ============================================================================
# Example 2: Using the FastAPI REST API
# ============================================================================

def example_rest_api():
    """
    Use the REST API to query the agent over HTTP.
    Best for: External applications, microservices.
    """
    
    BASE_URL = "http://localhost:8000"
    
    # Example queries
    queries = [
        "What are the top 5 customers by total order amount?",
        "Which products are out of stock?",
        "List all employees with their contact information.",
    ]
    
    for query in queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        # Send POST request
        response = requests.post(
            f"{BASE_URL}/query",
            json={"query": query},
            timeout=120,
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Generated SQL:")
            print(result['sql'])
            
            print(f"\n✓ Valid: {result['is_valid']}")
            
            print(f"\n✓ Answer:")
            print(result['final_answer'])
            
            print(f"\n✓ Execution Results ({result['execution_results']['row_count']} rows):")
            for row in result['execution_results']['rows'][:3]:  # Show first 3 rows
                print(f"  {row}")
        
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)


# ============================================================================
# Example 3: Batch Processing
# ============================================================================

def example_batch_processing():
    """
    Process multiple queries efficiently.
    Best for: Batch jobs, data analysis pipelines.
    """
    from graph.workflow import Text2SQLWorkflow
    
    workflow = Text2SQLWorkflow()
    
    # Batch of queries to process
    batch_queries = [
        "Count total orders by customer",
        "Find products with low stock",
        "List recent payments",
        "Show employee hierarchy",
    ]
    
    results = []
    
    for i, query in enumerate(batch_queries, 1):
        logger.info(f"Processing query {i}/{len(batch_queries)}: {query}")
        
        result = workflow.run(query)
        
        results.append({
            "query": query,
            "sql": result['sql'],
            "success": not bool(result['error']),
            "row_count": result.get('execution_results', {}).get('row_count', 0),
        })
    
    # Summary
    print("\n" + "="*70)
    print("BATCH PROCESSING SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r['success'])
    total_rows = sum(r['row_count'] for r in results)
    
    print(f"\nProcessed: {len(results)} queries")
    print(f"Successful: {successful}")
    print(f"Total rows returned: {total_rows}")
    
    print("\nResults:")
    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        print(f"  {i}. {status} {result['query'][:40]}... ({result['row_count']} rows)")


# ============================================================================
# Example 4: Error Handling
# ============================================================================

def example_error_handling():
    """
    Demonstrate proper error handling.
    Best for: Production applications.
    """
    from graph.workflow import Text2SQLWorkflow
    
    workflow = Text2SQLWorkflow()
    
    # Test queries that might cause issues
    problematic_queries = [
        "DELETE all customers",  # Should be blocked
        "What is 2+2?",  # Not a database query
        "",  # Empty query
        "Select * from nonexistent_table",  # Table doesn't exist
    ]
    
    for query in problematic_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print('='*70)
        
        try:
            result = workflow.run(query)
            
            if result['error']:
                print(f"⚠ Error occurred:")
                print(f"  {result['error']}")
            else:
                print(f"✓ Query succeeded")
                print(f"  Answer: {result['final_answer'][:100]}...")
        
        except Exception as e:
            print(f"✗ Exception: {e}")


# ============================================================================
# Example 5: Custom Workflow Integration
# ============================================================================

def example_custom_integration():
    """
    Integrate the workflow into a custom application.
    Best for: Building custom interfaces/applications.
    """
    from graph.workflow import Text2SQLWorkflow
    
    class QueryProcessor:
        """Custom query processor with caching."""
        
        def __init__(self):
            self.workflow = Text2SQLWorkflow()
            self.cache = {}
        
        def process(self, query: str) -> Dict[str, Any]:
            """Process a query with caching."""
            
            # Check cache
            if query in self.cache:
                logger.info(f"Cache hit for: {query}")
                return self.cache[query]
            
            # Execute workflow
            logger.info(f"Executing query: {query}")
            result = self.workflow.run(query)
            
            # Cache successful results
            if not result['error']:
                self.cache[query] = result
            
            return result
        
        def get_stats(self) -> Dict[str, Any]:
            """Get processing statistics."""
            return {
                "cached_queries": len(self.cache),
                "cache_size": len(self.cache),
            }
    
    # Use custom processor
    processor = QueryProcessor()
    
    # Process queries
    queries = [
        "List all customers",
        "List all customers",  # Should hit cache
        "Show recent orders",
    ]
    
    for query in queries:
        result = processor.process(query)
        print(f"Query: {query}")
        print(f"  Success: {not bool(result['error'])}")
        print(f"  Rows: {result.get('execution_results', {}).get('row_count', 0)}")
    
    # Show stats
    print(f"\nStats: {processor.get_stats()}")


# ============================================================================
# Example 6: Configuration Management
# ============================================================================

def example_configuration():
    """
    Show how to manage configuration.
    """
    from config import settings
    
    print("Current Configuration:")
    print(f"  Database: {settings.database_url}")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  LLM Model: {settings.llm_model}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  Log Level: {settings.log_level}")


# ============================================================================
# Example 7: Using Database Tools Directly
# ============================================================================

def example_database_tools():
    """
    Use database tools directly without the full workflow.
    Best for: Custom queries, schema inspection.
    """
    from tools.db_tools import (
        execute_query,
        get_database_schema,
        check_destructive_operations,
    )
    
    # Get database schema
    print("\n" + "="*70)
    print("DATABASE SCHEMA")
    print("="*70)
    
    schema = get_database_schema()
    
    if schema.get('success'):
        for table_name, table_info in schema['tables'].items():
            print(f"\nTable: {table_name}")
            print(f"  Columns: {len(table_info['columns'])}")
            for col in table_info['columns'][:3]:
                print(f"    - {col['name']} ({col['type']})")
            if len(table_info['columns']) > 3:
                print(f"    ... and {len(table_info['columns']) - 3} more")
    
    # Check for destructive operations
    print("\n" + "="*70)
    print("SECURITY CHECK")
    print("="*70)
    
    test_queries = [
        "SELECT * FROM customers",  # OK
        "UPDATE customers SET name='test'",  # Not OK
        "DELETE FROM orders WHERE date < '2020-01-01'",  # Not OK
    ]
    
    for query in test_queries:
        is_destructive = check_destructive_operations(query)
        status = "✗ BLOCKED" if is_destructive else "✓ OK"
        print(f"{status}: {query[:50]}...")
    
    # Execute a safe query
    print("\n" + "="*70)
    print("EXECUTE QUERY")
    print("="*70)
    
    result = execute_query("SELECT COUNT(*) as customer_count FROM customers")
    
    if result['success']:
        print(f"✓ Query executed")
        print(f"  Rows: {result['row_count']}")
        print(f"  Result: {result['rows']}")
    else:
        print(f"✗ Query failed: {result['error']}")


# ============================================================================
# Main - Run Examples
# ============================================================================

def main():
    """Run all examples."""
    
    import sys
    
    examples = {
        "1": ("Direct Workflow", example_direct_workflow),
        "2": ("REST API", example_rest_api),
        "3": ("Batch Processing", example_batch_processing),
        "4": ("Error Handling", example_error_handling),
        "5": ("Custom Integration", example_custom_integration),
        "6": ("Configuration", example_configuration),
        "7": ("Database Tools", example_database_tools),
    }
    
    print("\n" + "="*70)
    print("TEXT-TO-SQL AGENT - USAGE EXAMPLES")
    print("="*70)
    print("\nAvailable examples:")
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Exit")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nSelect example (0-7): ").strip()
    
    if choice == "0":
        print("Exiting...")
        return
    elif choice in examples:
        name, func = examples[choice]
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print('='*70)
        
        try:
            func()
        except Exception as e:
            logger.error(f"Error running example: {e}", exc_info=True)
            print(f"\n✗ Error: {e}")
    else:
        print("Invalid selection")


if __name__ == "__main__":
    main()
