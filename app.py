"""
Hybrid RAG Chatbot for Academic Burnout Detection (MBI-SS)
A professional chatbot powered by Google Gemini that queries PDF knowledge base first, 
then falls back to web search if needed.

Author: Senior Python Developer & AI Solutions Architect
Date: December 2025
"""

import os
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import tempfile

# LangChain Imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document

# Google Generative AI for safety settings
import google.generativeai as genai

# Environment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

class Config:
    """Application configuration constants."""
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    TEMPERATURE: float = 0.3
    MAX_TOKENS_LIMIT: int = 8000
    RELEVANCE_THRESHOLD: float = 0.7


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def initialize_session_state() -> None:
    """Initialize Streamlit session state variables for chat history and vector store."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    if "google_api_key" not in st.session_state:
        st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY", "")
    if "tavily_api_key" not in st.session_state:
        st.session_state.tavily_api_key = os.getenv("TAVILY_API_KEY", "")


def validate_api_keys() -> Tuple[bool, str]:
    """
    Validate that required API keys are configured.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not st.session_state.google_api_key:
        return False, "Google API Key is required. Please enter it in the sidebar."
    if not st.session_state.tavily_api_key:
        return False, "Tavily API Key is required for web search fallback. Please enter it in the sidebar."
    return True, ""


# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

def process_pdf_documents(uploaded_files: List[Any]) -> Optional[Chroma]:
    """
    Process uploaded PDF files and create a vector store with embeddings.
    
    Args:
        uploaded_files: List of uploaded PDF files from Streamlit file uploader
        
    Returns:
        Chroma vector store instance or None if processing fails
    """
    if not uploaded_files:
        return None
    
    try:
        all_documents: List[Document] = []
        
        # Process each uploaded PDF
        with st.spinner("Processing PDF documents..."):
            for uploaded_file in uploaded_files:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                
                # Load and process PDF
                loader = PyPDFLoader(tmp_path)
                documents = loader.load()
                
                # Add source metadata
                for doc in documents:
                    doc.metadata["source_file"] = uploaded_file.name
                
                all_documents.extend(documents)
                
                # Clean up temp file
                os.unlink(tmp_path)
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        splits = text_splitter.split_documents(all_documents)
        
        # Create embeddings and vector store
        with st.spinner("Creating embeddings and vector store..."):
            embeddings = GoogleGenerativeAIEmbeddings(
                model=Config.EMBEDDING_MODEL,
                google_api_key=st.session_state.google_api_key
            )
            
            vector_store = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=Config.CHROMA_PERSIST_DIR
            )
            
            vector_store.persist()
        
        st.success(f"Successfully processed {len(uploaded_files)} PDF file(s) with {len(splits)} chunks.")
        return vector_store
        
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")
        return None


# ============================================================================
# HYBRID SEARCH LOGIC (CORE IMPLEMENTATION)
# ============================================================================

def create_retrieval_tool(vector_store: Chroma) -> Tool:
    """
    Create a LangChain Tool for querying the vector database.
    
    Args:
        vector_store: ChromaDB vector store instance
        
    Returns:
        LangChain Tool for document retrieval
    """
    def search_knowledge_base(query: str) -> str:
        """Search the PDF knowledge base for relevant information."""
        try:
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            docs = retriever.get_relevant_documents(query)
            
            if not docs:
                return "No relevant information found in the knowledge base."
            
            # Format results with source citations
            result = "Information from Knowledge Base:\n\n"
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get("source_file", "Unknown")
                page = doc.metadata.get("page", "N/A")
                result += f"[Source {i}: {source}, Page {page}]\n"
                result += f"{doc.page_content}\n\n"
            
            return result
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    return Tool(
        name="Knowledge_Base_Search",
        func=search_knowledge_base,
        description=(
            "Search the local PDF knowledge base about Academic Burnout (MBI-SS), "
            "psychology research, and coping strategies. Use this FIRST before web search. "
            "Returns relevant excerpts with source citations."
        )
    )


def create_web_search_tool() -> Tool:
    """
    Create a LangChain Tool for web search using Tavily API.
    
    Returns:
        LangChain Tool for web search
    """
    tavily_search = TavilySearchResults(
        api_key=st.session_state.tavily_api_key,
        max_results=3
    )
    
    return Tool(
        name="Web_Search",
        func=lambda query: str(tavily_search.run(query)),
        description=(
            "Search the internet for information when the knowledge base doesn't have the answer. "
            "Use this as a FALLBACK only. Returns web search results with URLs."
        )
    )


def create_hybrid_agent(vector_store: Chroma) -> AgentExecutor:
    """
    Create an agent with hybrid search capability (PDF first, Web fallback).
    
    This is the CORE of the Hybrid RAG implementation. The agent uses:
    1. Knowledge Base Search Tool (Primary)
    2. Web Search Tool (Fallback)
    
    The LLM decides which tool to use based on the conversation context.
    
    Args:
        vector_store: ChromaDB vector store instance
        
    Returns:
        AgentExecutor capable of hybrid search
    """
    # Initialize Gemini LLM with safety settings
    llm = ChatGoogleGenerativeAI(
        model=Config.LLM_MODEL,
        temperature=Config.TEMPERATURE,
        google_api_key=st.session_state.google_api_key,
        convert_system_message_to_human=True,
        # Safety settings to prevent blocking mental health queries
        safety_settings={
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        }
    )
    
    # Create tools
    tools = [
        create_retrieval_tool(vector_store),
        create_web_search_tool()
    ]
    
    # Define agent prompt with clear instructions
    system_prompt = """You are an empathetic and professional counselor assistant specializing in Academic Burnout Detection using the Maslach Burnout Inventory - Student Survey (MBI-SS).

Your role:
- Provide evidence-based, objective guidance on academic burnout, stress management, and mental health
- Be empathetic, supportive, and non-judgmental
- Cite your sources clearly

CRITICAL SEARCH STRATEGY:
1. ALWAYS search the Knowledge_Base_Search tool FIRST for any question
2. Only use Web_Search if the knowledge base explicitly lacks the information
3. When citing sources:
   - For Knowledge Base: Mention the document name and page
   - For Web Search: Include the URL
4. If information comes from both sources, clearly distinguish them

Remember: Most questions about MBI-SS, burnout psychology, and coping strategies should be answered from the knowledge base."""

    # Create agent
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "chat_history"],
        template=system_prompt + "\n\nChat History: {chat_history}\n\nUser Question: {input}\n\n{agent_scratchpad}"
    )
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    return agent_executor


# ============================================================================
# CHAT INTERFACE
# ============================================================================

def display_chat_history() -> None:
    """Display the chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_query: str, agent_executor: AgentExecutor) -> str:
    """
    Process user input and generate response using the hybrid agent.
    
    Args:
        user_query: User's question
        agent_executor: Hybrid agent executor
        
    Returns:
        Generated response string
    """
    try:
        # Format chat history for context
        chat_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in st.session_state.messages[-6:]  # Last 3 exchanges
        ])
        
        # Invoke agent
        response = agent_executor.invoke({
            "input": user_query,
            "chat_history": chat_history
        })
        
        return response.get("output", "I apologize, but I couldn't generate a response.")
        
    except Exception as e:
        return f"An error occurred: {str(e)}. Please try rephrasing your question."


# ============================================================================
# STREAMLIT UI
# ============================================================================

def apply_custom_css() -> None:
    """Apply custom CSS for professional, corporate styling."""
    st.markdown("""
    <style>
    /* Professional Color Scheme */
    :root {
        --primary-color: #1E3A8A;
        --secondary-color: #3B82F6;
        --text-color: #1F2937;
        --background-color: #F9FAFB;
    }
    
    /* Main Container */
    .main {
        background-color: var(--background-color);
    }
    
    /* Headers */
    h1 {
        color: var(--primary-color);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
        border-bottom: 3px solid var(--secondary-color);
        padding-bottom: 10px;
    }
    
    h2, h3 {
        color: var(--text-color);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F3F4F6;
        border-right: 2px solid #E5E7EB;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--secondary-color);
        color: white;
        border-radius: 6px;
        border: none;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-color);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #D1D5DB;
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #D1D5DB;
        border-radius: 8px;
        padding: 20px;
        background-color: white;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: #D1FAE5;
        color: #065F46;
        border-radius: 6px;
    }
    
    .stError {
        background-color: #FEE2E2;
        color: #991B1B;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys Section
        st.subheader("API Keys")
        
        google_key = st.text_input(
            "Google API Key",
            type="password",
            value=st.session_state.google_api_key,
            help="Required for Gemini embeddings and LLM (Free tier available)"
        )
        if google_key:
            st.session_state.google_api_key = google_key
            os.environ["GOOGLE_API_KEY"] = google_key
        
        tavily_key = st.text_input(
            "Tavily API Key",
            type="password",
            value=st.session_state.tavily_api_key,
            help="Required for web search fallback"
        )
        if tavily_key:
            st.session_state.tavily_api_key = tavily_key
            os.environ["TAVILY_API_KEY"] = tavily_key
        
        st.divider()
        
        # Document Upload Section
        st.subheader("📄 Knowledge Base")
        
        uploaded_files = st.file_uploader(
            "Upload PDF Documents",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload MBI-SS instruments, psychology journals, or coping modules"
        )
        
        if st.button("Process Documents", type="primary"):
            if not st.session_state.google_api_key:
                st.error("Please enter your Google API Key first.")
            elif uploaded_files:
                vector_store = process_pdf_documents(uploaded_files)
                if vector_store:
                    st.session_state.vector_store = vector_store
                    st.session_state.documents_loaded = True
            else:
                st.warning("Please upload at least one PDF file.")
        
        # Status Indicator
        if st.session_state.documents_loaded:
            st.success("✓ Knowledge Base Ready")
        else:
            st.info("ℹ️ No documents loaded yet")
        
        st.divider()
        
        # Clear Chat Button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Information Section
        st.subheader("ℹ️ About")
        st.markdown("""
        **Hybrid RAG Chatbot**
        
        This system:
        - Searches PDFs first
        - Falls back to web if needed
        - Provides cited responses
        
        **Version:** 2.0  
        **Model:** Gemini 1.5 Flash  
        **Cost:** Free Tier
        """)


def main() -> None:
    """Main application entry point."""
    # Page Configuration
    st.set_page_config(
        page_title="Academic Burnout Assistant | MBI-SS",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply Custom Styling
    apply_custom_css()
    
    # Initialize Session State
    initialize_session_state()
    
    # Render Sidebar
    render_sidebar()
    
    # Main Content Area
    st.title("Academic Burnout Detection Assistant")
    st.markdown("""
    <p style='font-size: 1.1em; color: #6B7280;'>
    Professional counseling support powered by AI. Ask questions about academic burnout, 
    MBI-SS assessment, coping strategies, and mental health.
    </p>
    """, unsafe_allow_html=True)
    
    # Validation Check
    is_valid, error_msg = validate_api_keys()
    if not is_valid:
        st.warning(error_msg)
        st.stop()
    
    if not st.session_state.documents_loaded:
        st.info("👈 Please upload PDF documents in the sidebar to begin.")
        st.stop()
    
    # Display Chat History
    display_chat_history()
    
    # Chat Input
    if user_input := st.chat_input("Ask me about academic burnout, stress management, or MBI-SS..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Create agent executor
                agent_executor = create_hybrid_agent(st.session_state.vector_store)
                
                # Get response
                response = handle_user_input(user_input, agent_executor)
                
                # Display response
                st.markdown(response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update chat
        st.rerun()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
