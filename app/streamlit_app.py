"""
Streamlit Chat UI: User-facing interface for the Text-to-SQL agent.
"""
import streamlit as st
import json
import logging
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from graph.workflow import Text2SQLWorkflow

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(
    page_title="Text-to-SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 20px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "workflow" not in st.session_state:
        st.session_state.workflow = Text2SQLWorkflow()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def format_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format result for display."""
    return {
        "Query": result.get("user_query"),
        "Plan": result.get("plan", "N/A")[:200] + "...",
        "SQL": result.get("sql", "N/A"),
        "Valid": "✓" if result.get("is_valid") else "✗",
        "Answer": result.get("final_answer", "N/A"),
        "Error": result.get("error", "None"),
    }


def main():
    """Main Streamlit application."""
    initialize_session_state()
    
    # Header
    st.title("🤖 Text-to-SQL Agent")
    st.markdown(
        "Convert natural language queries to SQL and execute them against your database.",
        unsafe_allow_html=True,
    )
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("LLM Provider")
        st.info(f"Provider: {settings.llm_provider.upper()}")
        st.info(f"Model: {settings.llm_model}")
        
        st.subheader("Database")
        st.info(f"Status: 🟢 Connected")
        
        st.divider()
        
        st.subheader("About")
        st.markdown(
            """
            This is a production-ready agentic Text-to-SQL system that:
            
            1. **Plans** the database access strategy
            2. **Generates** SQL based on the plan
            3. **Validates** SQL syntax and security
            4. **Executes** the query safely
            5. **Summarizes** results in natural language
            
            Only SELECT queries are allowed for security.
            """
        )
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Results", "📚 History"])
    
    with tab1:
        st.subheader("Ask a Question About Your Data")
        
        # Query input
        query = st.text_area(
            "Enter your natural language query:",
            placeholder="e.g., What are the top 5 customers by total order amount?",
            height=100,
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            submit_button = st.button("🚀 Execute", use_container_width=True)
        
        with col2:
            st.markdown("")  # Spacing
        
        if submit_button and query.strip():
            with st.spinner("Processing your query..."):
                try:
                    # Execute workflow
                    result = st.session_state.workflow.run(query)
                    
                    # Store in session state
                    st.session_state.last_result = result
                    st.session_state.chat_history.append(
                        {"query": query, "result": result}
                    )
                    
                    # Display results
                    st.success("Query executed successfully!")
                    
                    # Show answer
                    st.markdown("### Answer:")
                    st.markdown(
                        f"**{result.get('final_answer', 'No answer generated')}**"
                    )
                    
                    # Show execution details in expander
                    with st.expander("📋 Execution Details"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Plan:**")
                            st.code(result.get("plan", "N/A")[:500], language="text")
                        
                        with col2:
                            st.markdown("**Generated SQL:**")
                            st.code(result.get("sql", "N/A"), language="sql")
                        
                        st.markdown("**Validation Status:**")
                        status = "✓ Valid" if result.get("is_valid") else "✗ Invalid"
                        st.info(status)
                        
                        if result.get("error"):
                            st.error(f"Error: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    logger.exception("Error in query execution")
        
        elif submit_button:
            st.warning("Please enter a query")
    
    with tab2:
        st.subheader("Query Results")
        
        if st.session_state.last_result:
            result = st.session_state.last_result
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Rows Returned", result.get("execution_results", {}).get("row_count", 0))
            
            with col2:
                valid_status = "✓ Valid" if result.get("is_valid") else "✗ Invalid"
                st.metric("SQL Valid", valid_status)
            
            st.divider()
            
            # Show raw execution results
            if result.get("execution_results", {}).get("rows"):
                st.markdown("### Raw Results:")
                
                rows = result["execution_results"]["rows"]
                
                # Try to display as DataFrame for better formatting
                try:
                    import pandas as pd
                    df = pd.DataFrame(rows)
                    st.dataframe(df, use_container_width=True)
                except Exception:
                    st.json(rows)
            else:
                st.info("No rows returned from the query.")
            
            # Show full details
            with st.expander("🔍 Full Details"):
                st.json(result)
        
        else:
            st.info("Execute a query to see results here.")
    
    with tab3:
        st.subheader("Query History")
        
        if st.session_state.chat_history:
            for i, item in enumerate(reversed(st.session_state.chat_history), 1):
                with st.expander(f"Query #{len(st.session_state.chat_history) - i + 1}: {item['query'][:50]}..."):
                    result = item["result"]
                    st.markdown("**Query:**")
                    st.code(item["query"])
                    
                    st.markdown("**Answer:**")
                    st.markdown(result.get("final_answer", "N/A"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Rows: {result.get('execution_results', {}).get('row_count', 0)}")
                    with col2:
                        st.write(f"Valid: {'✓' if result.get('is_valid') else '✗'}")
        
        else:
            st.info("No queries executed yet.")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: gray; font-size: 12px;">
        <p>Text-to-SQL Agent | Production-Ready Agentic Workflow</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
