"""
UI Module - FIXED HTML RENDERING & CLEAN UI
"""

import html

def get_custom_css() -> str:
    return """
    <style>
    /* IMPORT FONT INTER */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-main: #f8fafc;
        --bg-chat: #ffffff;
        --text-primary: #0f172a;
        --text-secondary: #64748b;
        --accent: #2563eb;
        --accent-hover: #1d4ed8;
        --border: #e2e8f0;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* HIDE DEFAULT ELEMENTS */
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu { display: none; }
    .stDeployButton { display: none; }
    footer { display: none; }
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid var(--border);
    }
    
    .sidebar-stat {
        background: #f1f5f9;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid var(--border);
        margin-bottom: 16px;
    }
    
    /* CHAT CONTAINER STYLING */
    .stApp {
        background-color: var(--bg-main);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 10rem; /* Space for fixed input */
        max-width: 850px;
    }

    /* BUBBLE STYLING */
    .chat-row {
        display: flex;
        width: 100%;
        margin-bottom: 1.5rem;
    }
    
    .chat-row.user {
        justify-content: flex-end;
    }
    
    .chat-row.assistant {
        justify-content: flex-start;
    }
    
    .chat-bubble {
        padding: 1rem 1.25rem;
        border-radius: 12px;
        max-width: 85%;
        font-size: 0.95rem;
        line-height: 1.6;
        position: relative;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .chat-bubble.user {
        background-color: var(--accent);
        color: white;
        border-bottom-right-radius: 2px;
    }
    
    .chat-bubble.assistant {
        background-color: white;
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-bottom-left-radius: 2px;
    }
    
    /* AVATAR */
    .avatar {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.85rem;
        flex-shrink: 0;
    }
    
    .avatar.assistant {
        background: #eff6ff;
        color: var(--accent);
        margin-right: 12px;
        border: 1px solid #dbeafe;
    }
    
    /* SOURCES STYLING */
    .sources-container {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #f1f5f9;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    
    .source-label {
        font-size: 0.7rem;
        color: var(--text-secondary);
        font-weight: 600;
        text-transform: uppercase;
        width: 100%;
        margin-bottom: 4px;
    }
    
    .source-tag {
        font-size: 0.75rem;
        background: #f8fafc;
        color: var(--text-secondary);
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid var(--border);
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
        text-decoration: none;
    }
    
    .source-tag:hover {
        border-color: var(--accent);
        color: var(--accent);
        background: white;
    }

    /* INPUT AREA */
    .input-sticky {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 20px 0;
        border-top: 1px solid var(--border);
        z-index: 999;
        display: flex;
        justify-content: center;
    }
    
    .input-wrapper {
        width: 100%;
        max-width: 850px;
        padding: 0 1rem;
        display: flex;
        gap: 10px;
    }
    
    /* STREAMLIT ELEMENT OVERRIDES */
    .stTextInput > div > div {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background: white !important;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    .stButton > button {
        border-radius: 10px !important;
        height: 42px !important;
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: var(--accent-hover) !important;
    }
    
    /* Remove default margins in markdown */
    .chat-bubble p { margin: 0; }
    </style>
    """

def render_welcome() -> str:
    # No indentation inside HTML string to prevent markdown code block issues
    return """<div style="text-align:center; margin: 4rem 0;">
<div style="font-size: 3rem; margin-bottom: 1rem;">👋</div>
<h2 style="color: #0f172a; margin-bottom: 0.5rem;">RAG Assistant</h2>
<p style="color: #64748b;">Tanyakan sesuatu tentang dokumen Anda atau cari info dari web.</p>
</div>"""

def render_message(role: str, content: str, sources: list = None) -> str:
    """
    Renders message HTML.
    CRITICAL: String formatting must NOT have indentation to avoid Markdown Code Blocks.
    """
    
    # 1. Handle User Message
    if role == "user":
        # Escape user content to prevent HTML injection but allow styling
        safe_content = html.escape(content)
        return f"""
<div class="chat-row user">
<div class="chat-bubble user">
{safe_content}
</div>
</div>
"""

    # 2. Handle Assistant Message
    else:
        sources_html = ""
        if sources:
            tags = []
            for src in sources:
                clean_src = src.replace("🌐 ", "").replace("📄 ", "")
                icon = "🌐" if "http" in clean_src else "📄"
                display = clean_src[:30] + "..." if len(clean_src) > 30 else clean_src
                # Creating span tags
                tags.append(f"""<span class="source-tag" title="{clean_src}">{icon} {display}</span>""")
            
            # Join tags
            tags_str = "".join(tags)
            sources_html = f"""
<div class="sources-container">
<div class="source-label">Sources</div>
{tags_str}
</div>"""
        
        # Return final HTML string WITHOUT indentation
        return f"""
<div class="chat-row assistant">
<div class="avatar assistant">AI</div>
<div class="chat-bubble assistant">
{content}
{sources_html}
</div>
</div>
"""