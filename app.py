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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_core.tools import Tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

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
        return False, "🔑 Google API Key is required. Please enter it in the sidebar."
    if not st.session_state.tavily_api_key:
        return False, "🔑 Tavily API Key is required for web search fallback. Please enter it in the sidebar."
    return True, ""


def test_google_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Test if Google API key is valid by making a simple request.
    
    Args:
        api_key: Google API key to test
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Try to initialize the model
        llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            google_api_key=api_key,
            temperature=0.1
        )
        
        # Make a simple test call
        response = llm.invoke("test")
        
        return True, "✅ API Key is valid!"
    
    except Exception as e:
        error_msg = str(e)
        
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            return False, "⚠️ API Key valid but quota exhausted. Try a different key or wait."
        elif "INVALID_ARGUMENT" in error_msg or "API key" in error_msg:
            return False, "❌ Invalid API Key. Please check your key."
        else:
            return False, f"⚠️ Could not validate API Key: {error_msg[:100]}"


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
        with st.spinner("📄 Processing PDF documents..."):
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
        
        if not all_documents:
            st.warning("⚠️ No content found in the uploaded PDF files.")
            return None
        
        # Split documents into chunks
        st.info(f"📊 Splitting {len(all_documents)} pages into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        splits = text_splitter.split_documents(all_documents)
        
        # Check if too many chunks (may cause quota issues)
        if len(splits) > 500:
            st.warning(f"⚠️ Large document detected ({len(splits)} chunks). This may take longer and consume more API quota.")
        
        # Create embeddings and vector store with aggressive rate limiting
        with st.spinner(f"🔄 Creating embeddings for {len(splits)} chunks... (This will take time due to rate limits)"):
            try:
                import time
                
                embeddings = GoogleGenerativeAIEmbeddings(
                    model=Config.EMBEDDING_MODEL,
                    google_api_key=st.session_state.google_api_key,
                    task_type="retrieval_document"
                )
                
                # AGGRESSIVE RATE LIMITING TO AVOID 429 ERRORS
                # Free tier: 60 requests/minute = 1 request per second
                # Process in very small batches with delays
                batch_size = 10  # Process only 10 chunks at a time
                delay_between_batches = 15  # Wait 15 seconds between batches
                
                st.info(f"⏱️ Processing in batches of {batch_size} with {delay_between_batches}s delays to respect rate limits...")
                st.info(f"📊 Estimated time: ~{(len(splits) / batch_size) * delay_between_batches / 60:.1f} minutes")
                    
                # Create vector store with retry mechanism
                max_retries = 3
                retry_delay = 30  # Start with 30 seconds
                
                # Process in small batches with delays to respect rate limits
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                vector_store = None
                total_batches = (len(splits) + batch_size - 1) // batch_size
                
                for batch_idx in range(0, len(splits), batch_size):
                    batch_num = batch_idx // batch_size + 1
                    batch_docs = splits[batch_idx:batch_idx + batch_size]
                    
                    status_text.text(f"Processing batch {batch_num}/{total_batches} ({len(batch_docs)} chunks)...")
                    
                    # Try to process this batch with retries
                    batch_success = False
                    for attempt in range(max_retries):
                        try:
                            if vector_store is None:
                                # First batch - create new vector store
                                vector_store = Chroma.from_documents(
                                    documents=batch_docs,
                                    embedding=embeddings,
                                    persist_directory=Config.CHROMA_PERSIST_DIR
                                )
                            else:
                                # Subsequent batches - add to existing
                                vector_store.add_documents(batch_docs)
                            
                            batch_success = True
                            break
                            
                        except Exception as embed_error:
                            error_msg = str(embed_error)
                            
                            # Check if it's a rate limit error
                            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                                if attempt < max_retries - 1:
                                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                                    st.warning(f"⏳ Rate limit hit. Waiting {wait_time}s before retry {attempt + 2}/{max_retries}...")
                                    time.sleep(wait_time)
                                else:
                                    # All retries failed
                                    st.error("🚫 **Google Gemini API Rate Limit Exceeded**")
                                    st.markdown("""
                                    **Your API key is hitting rate limits. This means:**
                                    
                                    1. **Per-Minute Limit** ⏱️
                                       - Free tier: 60 requests/minute
                                       - Your API key needs to cool down
                                       - **Solution:** Wait 5-10 minutes, then try again
                                    
                                    2. **Same Project API Key** 🔑
                                       - If new API key is from same project, quota is shared
                                       - **Solution:** Create API key from **different Google Cloud project**
                                       - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
                                       - Create NEW project (not just new key)
                                    
                                    3. **Daily Limit** 📊
                                       - If you used 1,500+ requests today
                                       - **Solution:** Wait until tomorrow or use different project
                                    
                                    **Immediate Actions:**
                                    - ⏰ Wait 10-15 minutes before trying again
                                    - 🔑 Or get API key from **completely new project**
                                    - 📉 Or try uploading just 5 pages as test
                                    
                                    **Current Status:**
                                    ```
                                    Processed: {batch_idx}/{len(splits)} chunks
                                    Failed at: Batch {batch_num}/{total_batches}
                                    ```
                                ```
                                {error_msg[:500]}...
                                ```
                                """)
                                return None
                        else:
                            # Different error, re-raise
                            raise
                    
                    if not batch_success:
                        # Batch failed after all retries
                        return None
                    
                    # Update progress
                    progress = min((batch_idx + batch_size) / len(splits), 1.0)
                    progress_bar.progress(progress)
                    
                    # Delay between batches (except last batch)
                    if batch_idx + batch_size < len(splits):
                        status_text.text(f"⏳ Waiting {delay_between_batches}s before next batch (rate limit protection)...")
                        time.sleep(delay_between_batches)
                
                # Persist the final vector store
                if vector_store:
                    vector_store.persist()
                    status_text.empty()
                    progress_bar.empty()
                
            except Exception as embed_error:
                error_msg = str(embed_error)
                
                # Check for specific error types
                if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                    st.error("🚫 **Google Gemini API Quota Exceeded**")
                    st.markdown("""
                    **Your Google API key has reached its quota limit.**
                    
                    **Quick Fixes:**
                    
                    1. **Wait** ⏰ - Free tier resets daily (1,500 requests/day)
                    2. **New Key** 🔑 - Get another key from [Google AI Studio](https://makersuite.google.com/app/apikey)
                    3. **Smaller Files** 📄 - Upload fewer pages or smaller PDFs
                    4. **Monitor** 📊 - Check [your usage](https://ai.google.dev/gemini-api/docs/quota)
                    
                    **Current Error:**
                    ```
                    Quota exceeded for embedding requests
                    ```
                    """)
                elif "INVALID_ARGUMENT" in error_msg or "API key" in error_msg:
                    st.error("🔑 **Invalid Google API Key**")
                    st.markdown("""
                    Please check:
                    - API key is correct
                    - Gemini API is enabled
                    - Key has embedding permissions
                    
                    Get a valid key: [Google AI Studio](https://makersuite.google.com/app/apikey)
                    """)
                else:
                    st.error(f"❌ **Error creating embeddings:** {error_msg[:300]}")
                
                return None
        
        st.success(f"✅ Successfully processed {len(uploaded_files)} PDF file(s) with {len(splits)} chunks!")
        return vector_store
        
    except Exception as e:
        st.error(f"❌ **Error processing documents:** {str(e)[:500]}")
        st.info("💡 **Tip:** Try uploading smaller PDF files or fewer documents at once.")
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


def create_llm_and_retriever(vector_store: Chroma):
    """
    Create LLM and retriever for hybrid RAG.
    
    Args:
        vector_store: ChromaDB vector store instance
        
    Returns:
        Tuple of (llm, retriever)
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
    
    # Create retriever from vector store
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    
    return llm, retriever


# ============================================================================
# CHAT INTERFACE
# ============================================================================

def display_chat_history() -> None:
    """Display the chat message history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_query: str, llm, retriever, tavily_search) -> str:
    """
    Process user input and generate response using hybrid search (PDF first, Web fallback).
    
    Args:
        user_query: User's question
        llm: Language model
        retriever: Vector store retriever
        tavily_search: Web search tool
        
    Returns:
        Generated response string
    """
    try:
        # Step 1: Retrieve relevant documents from knowledge base
        docs = retriever.get_relevant_documents(user_query)
        
        if docs and any(doc.page_content.strip() for doc in docs):
            # Format context from documents
            context = "\n\n".join([
                f"[Source: {doc.metadata.get('source_file', 'Unknown')}, Page {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
                for doc in docs[:4]
            ])
            
            # Create prompt with context
            prompt = f"""You are an empathetic and professional counselor assistant specializing in Academic Burnout Detection using the Maslach Burnout Inventory - Student Survey (MBI-SS).

Based on the following context from the knowledge base, please answer the question. Cite the sources (document name and page number).

Context:
{context}

Question: {user_query}

Answer:"""
            
            # Get response from LLM
            response = llm.invoke(prompt)
            return response.content
        
        else:
            # Step 2: Fallback to web search if no relevant docs
            try:
                web_results = tavily_search.run(user_query)
                
                prompt = f"""Based on web search results, please answer the question about academic burnout or mental health.

Web Search Results:
{web_results}

Question: {user_query}

Provide a helpful answer and mention that this information comes from web search."""
                
                response = llm.invoke(prompt)
                return response.content + "\n\n*Source: Web Search*"
                
            except Exception as web_error:
                return "I apologize, but I don't have enough information to answer your question. Please try uploading relevant PDF documents or rephrasing your question."
        
    except Exception as e:
        return f"An error occurred: {str(e)}. Please try rephrasing your question."


# ============================================================================
# STREAMLIT UI
# ============================================================================

def apply_custom_css() -> None:
    """Apply custom CSS for professional, corporate styling."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Dark Theme */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Container - Dark Background */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        background-attachment: fixed;
    }
    
    /* Content Block - Dark Semi-Transparent Card */
    .block-container {
        padding: 2rem 3rem;
        background: rgba(15, 23, 42, 0.7);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        margin: 2rem auto;
        max-width: 1200px;
        border: 1px solid rgba(100, 116, 139, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Headers - Gradient Text for Dark Theme */
    h1 {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    h2, h3 {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .subtitle strong {
        color: #cbd5e1;
    }
    
    /* Chat Messages - Dark Cards */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 15px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        border: 1px solid rgba(100, 116, 139, 0.3);
    }
    
    [data-testid="stChatMessageContent"] {
        color: #e2e8f0 !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Sidebar - Dark Theme */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 2px solid rgba(100, 116, 139, 0.3) !important;
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] small {
        color: #94a3b8 !important;
    }
    
    /* Input Fields - Dark Theme */
    .stTextInput > div > div > input,
    .stPasswordInput > div > div > input {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 2px solid #334155 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stPasswordInput > div > div > input:focus {
        background-color: rgba(30, 41, 59, 1) !important;
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2) !important;
        color: #ffffff !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stPasswordInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    /* File Uploader - Dark Theme */
    .stFileUploader {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 2px dashed #475569 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #60a5fa !important;
        background: rgba(96, 165, 250, 0.1) !important;
    }
    
    .stFileUploader label,
    .stFileUploader span {
        color: #94a3b8 !important;
    }
    
    /* Buttons - Gradient for Dark Theme */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.8) !important;
        color: #60a5fa !important;
        border: 2px solid #60a5fa !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(96, 165, 250, 0.2) !important;
        border-color: #8b5cf6 !important;
        color: #a78bfa !important;
    }
    
    /* Chat Input - Dark Theme */
    .stChatInput > div > div > input {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 2px solid #334155 !important;
        border-radius: 25px !important;
        padding: 0.75rem 1.5rem !important;
        color: #e2e8f0 !important;
    }
    
    .stChatInput > div > div > input:focus {
        background-color: rgba(30, 41, 59, 1) !important;
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2) !important;
    }
    
    .stChatInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    /* Success/Error Messages - Dark Theme */
    .stSuccess {
        background: rgba(34, 197, 94, 0.15) !important;
        border-left: 4px solid #22c55e !important;
        color: #86efac !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.15) !important;
        border-left: 4px solid #3b82f6 !important;
        color: #93c5fd !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
        color: #fcd34d !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
        color: #fca5a5 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 2px solid rgba(100, 116, 139, 0.3) !important;
        margin: 1.5rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #60a5fa;
    }
    
    /* Markdown */
    .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Code Blocks */
    code {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #93c5fd !important;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    
    pre {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Links */
    a {
        color: #60a5fa !important;
    }
    
    a:hover {
        color: #93c5fd !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("<small style='color: #64748b;'>Setup your API keys to get started</small>", unsafe_allow_html=True)
        st.markdown("")
        
        # API Keys Section with better UI
        st.markdown("**🔑 API Keys**")
        
        google_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            value=st.session_state.google_api_key,
            placeholder="Enter your Google API key...",
            help="Get your free API key from https://makersuite.google.com/app/apikey"
        )
        if google_key:
            st.session_state.google_api_key = google_key
            os.environ["GOOGLE_API_KEY"] = google_key
        
        tavily_key = st.text_input(
            "Tavily Search API Key",
            type="password",
            value=st.session_state.tavily_api_key,
            placeholder="Enter your Tavily API key...",
            help="Get your free API key from https://tavily.com"
        )
        if tavily_key:
            st.session_state.tavily_api_key = tavily_key
            os.environ["TAVILY_API_KEY"] = tavily_key
        
        # API Key Status
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.google_api_key:
                st.markdown("<small>✅ Google Key</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small>❌ Google Key</small>", unsafe_allow_html=True)
        with col2:
            if st.session_state.tavily_api_key:
                st.markdown("<small>✅ Tavily Key</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small>❌ Tavily Key</small>", unsafe_allow_html=True)
        
        # Warning about quota
        if st.session_state.google_api_key:
            st.markdown("")
            st.markdown("""
            <div style='background: rgba(245, 158, 11, 0.1); padding: 0.75rem; border-radius: 8px; border-left: 3px solid #f59e0b;'>
                <small style='color: #fcd34d;'>
                <strong>⚠️ Quota Limits:</strong><br>
                Free tier: 1,500 requests/day<br>
                Large PDFs may consume quota quickly!
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Document Upload Section with improved UI
        st.markdown("### 📚 Knowledge Base")
        st.markdown("<small style='color: #64748b;'>Upload PDF documents to build your knowledge base</small>", unsafe_allow_html=True)
        st.markdown("")
        
        uploaded_files = st.file_uploader(
            "Upload PDF Documents",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload MBI-SS instruments, psychology journals, or coping modules",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown(f"<small>📎 {len(uploaded_files)} file(s) selected</small>", unsafe_allow_html=True)
        
        if st.button("🚀 Process Documents", type="primary"):
            if not st.session_state.google_api_key:
                st.error("⚠️ Please enter your Google API Key first.")
            elif uploaded_files:
                vector_store = process_pdf_documents(uploaded_files)
                if vector_store:
                    st.session_state.vector_store = vector_store
                    st.session_state.documents_loaded = True
                    st.balloons()
            else:
                st.warning("📄 Please upload at least one PDF file.")
        
        # Status Indicator with better design
        st.markdown("")
        if st.session_state.documents_loaded:
            st.success("✅ Knowledge Base Ready", icon="✅")
        else:
            st.info("⏳ No documents loaded yet", icon="ℹ️")
        
        st.divider()
        
        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("🔄 Clear Cache", type="secondary", use_container_width=True):
                # Clear ChromaDB cache
                import shutil
                if os.path.exists(Config.CHROMA_PERSIST_DIR):
                    shutil.rmtree(Config.CHROMA_PERSIST_DIR)
                st.session_state.documents_loaded = False
                st.session_state.vector_store = None
                st.success("✅ Cache cleared!")
                st.rerun()
        
        st.divider()
        
        # Information Section with better formatting
        st.markdown("### ℹ️ System Info")
        st.markdown("""
        <div style='background: rgba(30, 41, 59, 0.8); padding: 1rem; border-radius: 10px; border-left: 4px solid #60a5fa;'>
            <strong style='color: #60a5fa;'>🤖 Hybrid RAG Chatbot</strong><br><br>
            <small style='color: #cbd5e1;'>
            <strong>Features:</strong><br>
            • 📖 Searches PDFs first<br>
            • 🌐 Falls back to web search<br>
            • 📝 Provides cited responses<br>
            • 💬 Empathetic counseling tone<br><br>
            <strong>Technology:</strong><br>
            • Model: Gemini 1.5 Flash<br>
            • Version: 2.0<br>
            • Cost: Free Tier<br>
            </small>
        </div>
        """, unsafe_allow_html=True)


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
    st.title("🎓 Academic Burnout Detection Assistant")
    st.markdown("""
    <div class='subtitle'>
        <strong>Professional counseling support powered by AI</strong><br>
        Ask questions about academic burnout, MBI-SS assessment, coping strategies, and mental health.
    </div>
    """, unsafe_allow_html=True)
    
    # Validation Check
    is_valid, error_msg = validate_api_keys()
    if not is_valid:
        st.warning(error_msg)
        st.stop()
    
    if not st.session_state.documents_loaded:
        st.markdown("""
        <div style='text-align: center; padding: 3rem 2rem; background: rgba(30, 41, 59, 0.6); 
                    border-radius: 15px; border: 2px dashed rgba(100, 116, 139, 0.5); backdrop-filter: blur(10px);'>
            <h2 style='color: #cbd5e1; font-size: 1.5rem;'>👈 Get Started</h2>
            <p style='color: #94a3b8; font-size: 1.1rem; margin-top: 1rem;'>
                Please upload PDF documents in the sidebar to begin using the chatbot.<br>
                You can upload MBI-SS instruments, psychology journals, or coping strategy guides.
            </p>
            <div style='margin-top: 2rem; padding: 1.5rem; background: rgba(15, 23, 42, 0.8); 
                        border-radius: 10px; display: inline-block; border: 1px solid rgba(96, 165, 250, 0.3);'>
                <strong style='color: #60a5fa;'>📋 Quick Setup:</strong><br>
                <small style='color: #94a3b8;'>
                1. Enter your API keys in the sidebar<br>
                2. Upload PDF documents (start with small files!)<br>
                3. Click "Process Documents"<br>
                4. Start chatting!
                </small>
            </div>
            <div style='margin-top: 1.5rem; padding: 1rem; background: rgba(239, 68, 68, 0.15); 
                        border-radius: 8px; border-left: 3px solid #ef4444; text-align: left; display: inline-block;'>
                <strong style='color: #fca5a5; font-size: 0.9rem;'>⚠️ IMPORTANT: Rate Limit Issues</strong><br>
                <small style='color: #94a3b8;'>
                <strong>If you get quota error even with new API key:</strong><br>
                • Your new key might be from <strong>same project</strong> (quota shared!)<br>
                • Solution: Create key from <strong>DIFFERENT PROJECT</strong><br>
                • Rate limit: 60 requests/minute - processing is SLOW<br>
                • 14 pages ≈ 40-70 chunks ≈ 3-5 minutes processing<br>
                • Use "Clear Cache" button if previous upload failed<br><br>
                <strong>Best practice:</strong> Start with 5-page PDF to test!
                </small>
            </div>
        </div>
        """, unsafe_allow_html=True)
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
                # Create LLM and retriever
                llm, retriever = create_llm_and_retriever(st.session_state.vector_store)
                
                # Create web search tool
                tavily_search = TavilySearchResults(
                    api_key=st.session_state.tavily_api_key,
                    max_results=3
                )
                
                # Get response
                response = handle_user_input(user_input, llm, retriever, tavily_search)
                
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
