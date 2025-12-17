"""
Hybrid RAG Chatbot - FINAL FIX
No Raw HTML Bugs, Responsive Sidebar
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Import modules
from ingest import initialize_vector_store
from chain import create_rag_chain
from ui import get_custom_css, render_message, render_welcome

# ==================== CONFIG ====================
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== LOGIC ====================

def load_environment():
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    # Secrets Fallback
    if not groq_key and hasattr(st, "secrets"):
        try: groq_key = st.secrets.get("GROQ_API_KEY")
        except: pass
    if not tavily_key and hasattr(st, "secrets"):
        try: tavily_key = st.secrets.get("TAVILY_API_KEY")
        except: pass
    return groq_key, tavily_key

def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

def setup_app():
    groq_key, tavily_key = load_environment()
    
    if not groq_key or not tavily_key:
        st.error("API Keys missing! Check .env")
        return False
    
    # 1. Load Vector Store (with indicator in Sidebar)
    if st.session_state.vectorstore is None:
        with st.sidebar:
            with st.spinner("Memuat Dokumen..."):
                vectorstore = initialize_vector_store(force_rebuild=False)
                st.session_state.vectorstore = vectorstore
    
    # 2. Load Chain
    if st.session_state.rag_chain is None:
        try:
            rag_chain = create_rag_chain(
                vectorstore=st.session_state.vectorstore,
                groq_api_key=groq_key,
                tavily_api_key=tavily_key,
                model_name="llama-3.3-70b-versatile"
            )
            st.session_state.rag_chain = rag_chain
            return True
        except Exception as e:
            st.error(f"Init Error: {str(e)}")
            return False
            
    return True

def process_query(query: str):
    # Add User Msg
    st.session_state.messages.append({"role": "user", "content": query})
    
    try:
        # Get AI Response
        result = st.session_state.rag_chain.ask(query)
        
        # Add AI Msg
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "sources": result["sources"]
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Maaf, error: {str(e)}",
            "sources": []
        })

# ==================== MAIN UI ====================

def main():
    # 1. Inject CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # 2. Init
    init_session()
    
    # 3. SIDEBAR (RESPONSIVE NATIVE STREAMLIT)
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        # Status Card
        st.markdown("""
        <div class="sidebar-stat">
            <div style="font-size:0.8rem; color:#64748b; font-weight:600;">SYSTEM STATUS</div>
            <div style="font-size:1.1rem; color:#10b981; font-weight:700; margin-top:4px;">● Online</div>
            <div style="font-size:0.8rem; color:#64748b; margin-top:4px;">Model: Llama 3.3 (70B)</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Actions")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Reset", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with c2:
            if st.button("🔄 Reload", use_container_width=True):
                st.session_state.vectorstore = initialize_vector_store(force_rebuild=True)
                groq_key, tavily_key = load_environment()
                st.session_state.rag_chain = create_rag_chain(
                    vectorstore=st.session_state.vectorstore,
                    groq_api_key=groq_key,
                    tavily_api_key=tavily_key
                )
                st.toast("Dokumen dimuat ulang!", icon="✅")
        
        st.markdown("---")
        st.info("Prioritas: Dokumen Lokal (`data/`). Jika tidak ada, mencari via Web.")

    # 4. SETUP CHECK
    if not st.session_state.initialized:
        if setup_app():
            st.session_state.initialized = True
        else:
            st.stop()

    # 5. CHAT AREA
    chat_placeholder = st.container()
    
    with chat_placeholder:
        if not st.session_state.messages:
            st.markdown(render_welcome(), unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                # CRITICAL: unsafe_allow_html=True MUST be on
                st.markdown(
                    render_message(
                        msg["role"], 
                        msg["content"], 
                        msg.get("sources", [])
                    ), 
                    unsafe_allow_html=True
                )

    # 6. INPUT AREA (FIXED BOTTOM)
    st.markdown('<div class="input-sticky"><div class="input-wrapper">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input(
            "Pesan", 
            placeholder="Ketik pertanyaan Anda di sini...", 
            label_visibility="collapsed",
            key="chat_input_main"
        )
    with col2:
        send_pressed = st.button("Kirim", use_container_width=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Process
    if send_pressed and user_input:
        process_query(user_input)
        st.rerun()

if __name__ == "__main__":
    main()