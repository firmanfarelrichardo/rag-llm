"""
UI Module - SIMPLE & CLEAN DARK THEME
No sidebar, minimalist, professional layout
Built from scratch with simplicity in mind
"""

def get_custom_css() -> str:
    """
    Simple and clean dark theme CSS
    No sidebar, minimalist design, professional look
    
    Returns:
        CSS string for clean UI
    """
    return """
    <style>
    /* ========================================
       IMPORT CLEAN FONT - Inter
       ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ========================================
       GLOBAL RESET
       ======================================== */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* ========================================
       COLOR PALETTE - Simple Dark Theme
       ======================================== */
    :root {
        --bg-main: #0d1117;
        --bg-secondary: #161b22;
        --bg-tertiary: #1f2937;
        --accent: #3b82f6;
        --accent-hover: #2563eb;
        --text-primary: #e6edf3;
        --text-secondary: #8b949e;
        --border: #30363d;
        --success: #3fb950;
        --error: #f85149;
    }
    
    /* ========================================
       MAIN BACKGROUND
       ======================================== */
    .stApp {
        background: var(--bg-main);
        color: var(--text-primary);
    }
    
    /* ========================================
       MAIN CONTAINER - Full Width
       ======================================== */
    .main {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* ========================================
       HEADER - Simple & Clean
       ======================================== */
    .app-header {
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border);
        padding: 1.5rem 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(10px);
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    .header-stats {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .stat-item {
        text-align: right;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-value {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--accent);
    }
    
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        font-size: 0.875rem;
        color: var(--accent);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* ========================================
       CHAT CONTAINER
       ======================================== */
    .chat-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        min-height: calc(100vh - 200px);
    }
    
    /* ========================================
       CHAT MESSAGES - Clean Style
       ======================================== */
    .message {
        margin-bottom: 2rem;
        animation: fadeInUp 0.3s ease;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* User Message */
    .user-message {
        display: flex;
        justify-content: flex-end;
    }
    
    .user-content {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        max-width: 80%;
    }
    
    .message-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        color: var(--text-secondary);
    }
    
    .message-text {
        font-size: 0.95rem;
        line-height: 1.6;
        color: var(--text-primary);
    }
    
    /* Assistant Message */
    .assistant-message {
        display: flex;
        gap: 1rem;
    }
    
    .assistant-avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, var(--accent) 0%, #6366f1 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .assistant-content {
        flex: 1;
        max-width: 80%;
    }
    
    .assistant-bubble {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1.5rem;
    }
    
    /* ========================================
       SOURCE TAGS
       ======================================== */
    .sources {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
    }
    
    .sources-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .source-tag {
        display: inline-block;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 6px;
        padding: 0.375rem 0.75rem;
        margin: 0.25rem 0.25rem 0.25rem 0;
        font-size: 0.8125rem;
        color: var(--accent);
        transition: all 0.2s ease;
    }
    
    .source-tag:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: var(--accent);
    }
    
    /* ========================================
       WELCOME SCREEN
       ======================================== */
    .welcome {
        text-align: center;
        padding: 4rem 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    .welcome-description {
        font-size: 1.125rem;
        line-height: 1.7;
        color: var(--text-secondary);
        margin-bottom: 3rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .feature-card:hover {
        border-color: var(--accent);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }
    
    .feature-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* ========================================
       INPUT AREA - Fixed Bottom
       ======================================== */
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-secondary);
        border-top: 1px solid var(--border);
        padding: 1.5rem 2rem;
        backdrop-filter: blur(10px);
        z-index: 99;
    }
    
    .input-wrapper {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .stTextInput {
        flex: 1;
    }
    
    .stTextInput > div > div > input {
        background: var(--bg-main) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 0.875rem 1.25rem !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-secondary) !important;
    }
    
    /* ========================================
       BUTTONS
       ======================================== */
    .stButton > button {
        background: var(--accent) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--accent-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary buttons (in header) */
    .button-group {
        display: flex;
        gap: 0.5rem;
    }
    
    .button-group .stButton > button {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        color: var(--text-secondary) !important;
    }
    
    .button-group .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* ========================================
       ALERTS
       ======================================== */
    .stAlert {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }
    
    .stSuccess {
        border-left: 4px solid var(--success) !important;
    }
    
    .stError {
        border-left: 4px solid var(--error) !important;
    }
    
    .stWarning {
        border-left: 4px solid #f59e0b !important;
    }
    
    .stInfo {
        border-left: 4px solid var(--accent) !important;
    }
    
    /* ========================================
       LOADING SPINNER
       ======================================== */
    .stSpinner > div {
        border-top-color: var(--accent) !important;
    }
    
    /* ========================================
       SCROLLBAR
       ======================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-main);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* ========================================
       CODE BLOCKS
       ======================================== */
    code {
        background: var(--bg-main) !important;
        color: var(--accent) !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-size: 0.875rem !important;
    }
    
    pre {
        background: var(--bg-main) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* ========================================
       RESPONSIVE DESIGN
       ======================================== */
    @media (max-width: 768px) {
        .app-header {
            padding: 1rem;
        }
        
        .header-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .header-stats {
            gap: 1rem;
            width: 100%;
            justify-content: space-between;
        }
        
        .chat-container {
            padding: 1rem;
        }
        
        .user-content,
        .assistant-content {
            max-width: 95%;
        }
        
        .input-area {
            padding: 1rem;
        }
        
        .input-wrapper {
            flex-direction: column;
        }
        
        .stTextInput {
            width: 100%;
        }
        
        .stButton {
            width: 100%;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* ========================================
       UTILITY CLASSES
       ======================================== */
    .text-center { text-align: center; }
    .text-primary { color: var(--text-primary); }
    .text-secondary { color: var(--text-secondary); }
    .text-accent { color: var(--accent); }
    </style>
    """


def render_message(role: str, content: str, sources: list = None) -> str:
    """
    Render chat message - simple and clean
    
    Args:
        role: 'user' or 'assistant'
        content: Message content
        sources: List of sources
        
    Returns:
        HTML string
    """
    if role == "user":
        return f"""
        <div class="message user-message">
            <div class="user-content">
                <div class="message-label">You</div>
                <div class="message-text">{content}</div>
            </div>
        </div>
        """
    else:
        sources_html = ""
        if sources:
            tags = []
            for source in sources:
                clean = source.replace("🌐 ", "").replace("📄 ", "")
                icon = "🌐" if "http" in clean else "📄"
                display = clean[:40] + "..." if len(clean) > 40 else clean
                tags.append(f'<span class="source-tag">{icon} {display}</span>')
            
            sources_html = f"""
            <div class="sources">
                <span class="sources-label">Sources</span>
                <div>{"".join(tags)}</div>
            </div>
            """
        
        return f"""
        <div class="message assistant-message">
            <div class="assistant-avatar">AI</div>
            <div class="assistant-content">
                <div class="assistant-bubble">
                    <div class="message-label">Assistant</div>
                    <div class="message-text">{content}</div>
                </div>
                {sources_html}
            </div>
        </div>
        """


def render_welcome_message() -> str:
    """
    Render welcome screen - clean and simple
    
    Returns:
        HTML string
    """
    return """
    <div class="welcome">
        <div class="welcome-icon">💬</div>
        <h1 class="welcome-title">Hybrid RAG Chatbot</h1>
        <p class="welcome-description">
            Sistem AI yang menggabungkan dokumen lokal dengan pencarian web real-time.
            Dapatkan jawaban akurat dan komprehensif untuk setiap pertanyaan Anda.
        </p>
        
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">Llama 3.3 (70B)</div>
                <div class="feature-desc">Model AI terkini untuk respons akurat</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📚</div>
                <div class="feature-title">ChromaDB</div>
                <div class="feature-desc">Vector store lokal super cepat</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">🌐</div>
                <div class="feature-title">Tavily Search</div>
                <div class="feature-desc">Pencarian web untuk info terkini</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Hybrid RAG</div>
                <div class="feature-desc">Kombinasi dokumen lokal & web</div>
            </div>
        </div>
    </div>
    """


def render_status_indicator(status: str, message: str) -> str:
    """
    Render status indicator
    
    Args:
        status: 'loading', 'success', 'error', 'info'
        message: Status message
        
    Returns:
        HTML string
    """
    icons = {
        'loading': '⏳',
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️'
    }
    
    return f"""
    <div class="status-badge">
        <span>{icons.get(status, 'ℹ️')}</span>
        <span>{message}</span>
    </div>
    """
