"""
Hybrid RAG Chatbot - SIMPLE & CLEAN VERSION
No sidebar, minimalist design, professional layout
"""

import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Import modules
from ingest import initialize_vector_store
from chain import create_rag_chain
from ui_simple import (
    get_custom_css,
    render_message,
    render_welcome_message,
    render_status_indicator
)


# ==================== CONFIG ====================
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==================== FUNCTIONS ====================

def load_environment() -> tuple[Optional[str], Optional[str]]:
    """Load API keys"""
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not groq_key and hasattr(st, "secrets"):
        try: groq_key = st.secrets.get("GROQ_API_KEY")
        except: pass
    
    if not tavily_key and hasattr(st, "secrets"):
        try: tavily_key = st.secrets.get("TAVILY_API_KEY")
        except: pass
    
    return groq_key, tavily_key


def init_session():
    """Initialize session state"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False


def setup_app() -> bool:
    """Setup application"""
    groq_key, tavily_key = load_environment()
    
    if not groq_key or not tavily_key:
        st.error("**API Keys tidak ditemukan!**")
        st.markdown("""
        ### Setup API Keys:
        1. Buat file `.env` di root folder
        2. Tambahkan:
        ```
        GROQ_API_KEY=your_key
        TAVILY_API_KEY=your_key
        ```
        
        **Dapatkan Keys (GRATIS):**
        - Groq: https://console.groq.com/keys
        - Tavily: https://tavily.com/
        """)
        return False
    
    if st.session_state.vectorstore is None:
        with st.spinner("Memuat dokumen..."):
            vectorstore = initialize_vector_store(force_rebuild=False)
            st.session_state.vectorstore = vectorstore
            if vectorstore is None:
                st.warning("Tidak ada dokumen di folder `data/`. Chatbot akan menggunakan web search saja.")
    
    if st.session_state.rag_chain is None:
        try:
            with st.spinner("Menginisialisasi sistem..."):
                rag_chain = create_rag_chain(
                    vectorstore=st.session_state.vectorstore,
                    groq_api_key=groq_key,
                    tavily_api_key=tavily_key,
                    model_name="llama-3.3-70b-versatile"
                )
                st.session_state.rag_chain = rag_chain
                st.success("Sistem siap!")
                return True
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False
    
    return True


def process_query(query: str):
    """Process user query"""
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    
    try:
        with st.spinner("AI sedang berpikir..."):
            result = st.session_state.rag_chain.ask(query)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "sources": result["sources"]
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Maaf, terjadi kesalahan: {str(e)}",
            "sources": []
        })


# ==================== MAIN ====================

def main():
    """Main application"""
    
    # Inject CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize
    init_session()
    
    # Setup
    if not st.session_state.initialized:
        success = setup_app()
        if success:
            st.session_state.initialized = True
        else:
            st.stop()
    
    # HEADER
    st.markdown(f"""
    <div class="app-header">
        <div class="header-content">
            <div>
                <div class="app-title">Hybrid RAG Chatbot</div>
                <div class="app-subtitle">Powered by Llama 3.3 (70B) • ChromaDB • Tavily Search</div>
            </div>
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-label">Messages</div>
                    <div class="stat-value">{len(st.session_state.messages)}</div>
                </div>
                <div class="status-badge">
                    <span class="status-dot"></span>
                    <span>Online</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add control buttons in header
    col1, col2, col3 = st.columns([1, 1, 10])
    with col1:
        if st.button("🔄 Reset", key="reset"):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("📥 Reload", key="reload"):
            with st.spinner("Reloading..."):
                st.session_state.vectorstore = initialize_vector_store(force_rebuild=True)
                groq_key, tavily_key = load_environment()
                st.session_state.rag_chain = create_rag_chain(
                    vectorstore=st.session_state.vectorstore,
                    groq_api_key=groq_key,
                    tavily_api_key=tavily_key,
                    model_name="llama-3.3-70b-versatile"
                )
                st.success("Reloaded!")
                st.rerun()
    
    # CHAT CONTAINER
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.markdown(render_welcome_message(), unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            st.markdown(
                render_message(
                    msg["role"],
                    msg["content"],
                    msg.get("sources", [])
                ),
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add spacing for fixed input
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    
    # INPUT AREA (Fixed at bottom)
    st.markdown('<div class="input-area"><div class="input-wrapper">', unsafe_allow_html=True)
    
    col_input, col_button = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            key="user_input",
            placeholder="Ketik pertanyaan Anda di sini...",
            label_visibility="collapsed"
        )
    with col_button:
        send = st.button("Send", use_container_width=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Process
    if send and user_input:
        process_query(user_input)
        st.rerun()


if __name__ == "__main__":
    main()
