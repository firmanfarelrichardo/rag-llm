# 🚀 Quick Start Guide

## ✅ Installation Complete!

All dependencies have been successfully installed. Your Hybrid RAG Chatbot is ready to use!

## 📋 Next Steps

### 1. Get Your FREE API Keys

#### **Groq API Key** (Ultra-fast Llama 3 inference)
1. Visit: https://console.groq.com/keys
2. Sign up (free account)
3. Click "Create API Key"
4. Copy the key (starts with `gsk_`)

#### **Tavily API Key** (AI-optimized web search)
1. Visit: https://tavily.com/
2. Sign up (1000 searches/month free)
3. Go to dashboard
4. Copy your API key (starts with `tvly_`)

### 2. Configure Your API Keys

Open the `.env.example` file and copy it to `.env`:

```bash
cp .env.example .env
```

Then edit `.env` and add your keys:

```env
GROQ_API_KEY=gsk_your_actual_groq_key_here
TAVILY_API_KEY=tvly_your_actual_tavily_key_here
```

### 3. Add Your PDF Documents

Place your PDF files in the `data/` folder:

```
rag-llm/
└── data/
    ├── document1.pdf
    ├── research_paper.pdf
    └── manual.pdf
```

**Note:** The system supports English and Indonesian PDFs but always responds in Indonesian.

### 4. Run the Application

```bash
streamlit run app.py
```

The app will:
- ✅ Load API keys
- ✅ Automatically scan and ingest PDFs
- ✅ Create/load ChromaDB vector store
- ✅ Launch at `http://localhost:8501`

## 🎯 How It Works

1. **Ask Questions**: Type in Indonesian or English
2. **Smart Retrieval**:
   - First searches local documents (ChromaDB)
   - Falls back to web search if needed (Tavily)
3. **AI Response**: Llama 3 (70B) generates answer in Indonesian
4. **Source Citations**: Shows which documents/websites were used

## 💡 Usage Tips

- **Clear Chat**: Use sidebar "Reset Obrolan" button
- **Reload Documents**: Click "Muat Ulang Dokumen" after adding new PDFs
- **No PDFs?**: App works with web-only mode

## 🔧 Troubleshooting

### "API key not found"
- Ensure `.env` file exists in project root
- Check keys are correctly formatted
- Restart Streamlit after adding keys

### "No PDF files found"
- Add PDFs to `data/` folder
- App will still work with web search only

### ChromaDB errors
- Delete `chroma_db/` folder
- Restart app to rebuild

## 📝 Example Questions

Try asking:
- "Apa isi dokumen ini?" (What's in this document?)
- "Jelaskan tentang [topic]" (Explain about [topic])
- "Siapa presiden Indonesia saat ini?" (Who is Indonesia's current president?)

## 🎨 Features

- ✅ Gemini-style dark mode UI
- ✅ Hybrid RAG (local + web)
- ✅ Cross-lingual (reads EN/ID, responds in ID)
- ✅ Source citations
- ✅ Fast inference via Groq

---

**Enjoy your AI-powered chatbot! 🤖**
