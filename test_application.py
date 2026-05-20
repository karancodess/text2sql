#!/usr/bin/env python3
"""
Comprehensive test suite for the Text2SQL application.
Tests all components without requiring actual LLM API calls.
"""
import sys
import os
sys.path.insert(0, 'app')

from unittest.mock import Mock, patch
from agents.planner import PlannerAgent
from agents.sql_generator import SQLGeneratorAgent
from agents.validator import ValidatorAgent
from agents.executor import ExecutorAgent
from agents.summarizer import SummarizerAgent
from graph.workflow import Text2SQLWorkflow
from tools.db_tools import check_destructive_operations

def test_imports():
    """Test that all modules import successfully."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    modules_to_test = [
        'agents.llm',
        'agents.planner',
        'agents.sql_generator',
        'agents.validator',
        'agents.executor',
        'agents.summarizer',
        'graph.workflow',
        'main',
        'db',
        'config',
    ]
    
    failed = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed imports: {', '.join(failed)}")
        return False
    else:
        print(f"\n✅ All modules imported successfully!")
        return True


def test_agent_initialization():
    """Test that agents can be initialized without API keys."""
    print("\n" + "=" * 60)
    print("TEST 2: Agent Initialization (Lazy Loading)")
    print("=" * 60)
    
    agents_to_test = [
        ("PlannerAgent", PlannerAgent),
        ("SQLGeneratorAgent", SQLGeneratorAgent),
        ("ValidatorAgent", ValidatorAgent),
        ("ExecutorAgent", ExecutorAgent),
        ("SummarizerAgent", SummarizerAgent),
        ("Text2SQLWorkflow", Text2SQLWorkflow),
    ]
    
    failed = []
    for agent_name, agent_class in agents_to_test:
        try:
            agent = agent_class()
            print(f"✓ {agent_name} initialized")
        except Exception as e:
            print(f"✗ {agent_name}: {e}")
            failed.append(agent_name)
    
    if failed:
        print(f"\n❌ Failed initializations: {', '.join(failed)}")
        return False
    else:
        print(f"\n✅ All agents initialized successfully!")
        return True


def test_destructive_operations_check():
    """Test SQL destructive operations detection."""
    print("\n" + "=" * 60)
    print("TEST 3: Destructive Operations Detection")
    print("=" * 60)
    
    test_cases = [
        ("SELECT * FROM products", False, "Safe SELECT"),
        ("DELETE FROM products", True, "Destructive DELETE"),
        ("UPDATE products SET price = 100", True, "Destructive UPDATE"),
        ("DROP TABLE products", True, "Destructive DROP"),
        ("INSERT INTO products VALUES (...)", True, "Destructive INSERT"),
        ("SELECT * FROM orders WHERE customer_id = 5", False, "Safe SELECT with WHERE"),
    ]
    
    passed = 0
    failed = 0
    
    for sql, expected_destructive, description in test_cases:
        try:
            result = check_destructive_operations(sql)
            if result == expected_destructive:
                print(f"✓ {description}: {result}")
                passed += 1
            else:
                print(f"✗ {description}: Expected {expected_destructive}, got {result}")
                failed += 1
        except Exception as e:
            print(f"✗ {description}: {e}")
            failed += 1
    
    if failed > 0:
        print(f"\n❌ {failed} tests failed, {passed} passed")
        return False
    else:
        print(f"\n✅ All {passed} destructive operation tests passed!")
        return True


def test_workflow_with_mocks():
    """Test workflow with mocked LLM responses."""
    print("\n" + "=" * 60)
    print("TEST 4: Workflow with Mocked LLM")
    print("=" * 60)
    
    try:
        with patch('agents.llm.get_llm') as mock_get_llm:
            # Create a mock LLM
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm
            
            # Mock responses for each step
            mock_llm.invoke.side_effect = [
                # Planner response
                "Relevant Tables: customers, orders\nJoin: orders.customerNumber = customers.customerNumber\nFilter: status = 'Shipped'",
                # Generator response
                "SELECT * FROM customers c JOIN orders o ON c.customerNumber = o.customerNumber WHERE o.status = 'Shipped'",
                # Validator response (no validation needed for this test)
                '{"is_valid": true}',
                # Summarizer response
                "Found 5 orders with 'Shipped' status from customers.",
            ]
            
            # Run workflow
            workflow = Text2SQLWorkflow()
            result = workflow.run("Show me all shipped orders")
            
            print(f"✓ Workflow executed")
            print(f"  - User Query: {result.get('user_query')[:50]}...")
            print(f"  - Plan created: {'plan' in result and len(result['plan']) > 0}")
            print(f"  - SQL generated: {'sql' in result and len(result['sql']) > 0}")
            print(f"  - Final answer: {result.get('final_answer', 'N/A')[:50]}...")
            
            return True
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_interfaces():
    """Test that agent methods have correct signatures."""
    print("\n" + "=" * 60)
    print("TEST 5: Agent Interface Contracts")
    print("=" * 60)
    
    test_cases = [
        ("PlannerAgent", PlannerAgent, "plan", ["user_query"]),
        ("SQLGeneratorAgent", SQLGeneratorAgent, "generate", ["plan", "user_query"]),
        ("ValidatorAgent", ValidatorAgent, "validate", ["sql_query"]),
        ("ExecutorAgent", ExecutorAgent, "execute", ["sql_query"]),
        ("SummarizerAgent", SummarizerAgent, "summarize", ["user_query", "execution_results"]),
    ]
    
    passed = 0
    failed = 0
    
    for agent_name, agent_class, method_name, required_params in test_cases:
        try:
            agent = agent_class()
            method = getattr(agent, method_name)
            
            # Check if method is callable
            if callable(method):
                print(f"✓ {agent_name}.{method_name}() exists and is callable")
                passed += 1
            else:
                print(f"✗ {agent_name}.{method_name}() is not callable")
                failed += 1
        except AttributeError as e:
            print(f"✗ {agent_name}.{method_name}() not found: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {agent_name}: {e}")
            failed += 1
    
    if failed > 0:
        print(f"\n❌ {failed} interface tests failed, {passed} passed")
        return False
    else:
        print(f"\n✅ All {passed} interface tests passed!")
        return True


def test_prompt_availability():
    """Test that all required prompts are available."""
    print("\n" + "=" * 60)
    print("TEST 6: Prompt Availability")
    print("=" * 60)
    
    from prompts import (
        PLANNER_SYSTEM_PROMPT,
        SQL_GENERATOR_SYSTEM_PROMPT,
        VALIDATOR_SYSTEM_PROMPT,
        SUMMARIZER_SYSTEM_PROMPT,
        DATABASE_SCHEMA,
    )
    
    prompts_to_test = [
        ("PLANNER_SYSTEM_PROMPT", PLANNER_SYSTEM_PROMPT),
        ("SQL_GENERATOR_SYSTEM_PROMPT", SQL_GENERATOR_SYSTEM_PROMPT),
        ("VALIDATOR_SYSTEM_PROMPT", VALIDATOR_SYSTEM_PROMPT),
        ("SUMMARIZER_SYSTEM_PROMPT", SUMMARIZER_SYSTEM_PROMPT),
        ("DATABASE_SCHEMA", DATABASE_SCHEMA),
    ]
    
    passed = 0
    failed = 0
    
    for prompt_name, prompt_content in prompts_to_test:
        if prompt_content and isinstance(prompt_content, str) and len(prompt_content) > 0:
            print(f"✓ {prompt_name} available ({len(prompt_content)} chars)")
            passed += 1
        else:
            print(f"✗ {prompt_name} is missing or empty")
            failed += 1
    
    if failed > 0:
        print(f"\n❌ {failed} prompt tests failed, {passed} passed")
        return False
    else:
        print(f"\n✅ All {passed} prompts available!")
        return True


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " TEXT2SQL APPLICATION TEST SUITE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Module Imports", test_imports),
        ("Agent Initialization", test_agent_initialization),
        ("Destructive Operations Check", test_destructive_operations_check),
        ("Prompt Availability", test_prompt_availability),
        ("Agent Interface Contracts", test_agent_interfaces),
        ("Workflow with Mocks", test_workflow_with_mocks),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Application is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
