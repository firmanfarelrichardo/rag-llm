# Security Guidelines untuk RAG-LLM Project

## 🔐 File yang WAJIB Diabaikan Git

### Critical Files (NEVER COMMIT)
```
.env                    # API keys utama
.env.local             # Environment lokal
chroma_db/             # Database vector lokal
*.key                  # Private keys
credentials.json       # Service account credentials
```

### Best Practices Checklist

- [x] `.gitignore` sudah dikonfigurasi
- [x] `.env` sudah diabaikan oleh git
- [x] Dependencies terinstall dengan benar
- [ ] Buat file `.env` dan isi dengan API keys Anda
- [ ] Test aplikasi dengan `streamlit run app.py`

## 🚨 Jika API Key Ter-Leak

### Immediate Actions

1. **Revoke API Keys Segera:**
   - Google AI: https://makersuite.google.com/app/apikey
   - Tavily: https://tavily.com/dashboard/api-keys

2. **Generate Keys Baru:**
   - Buat API key baru di dashboard masing-masing
   - Update file `.env` lokal

3. **Clean Git History:**
   ```bash
   # Hapus file dari tracking
   git rm --cached .env
   
   # Commit perubahan
   git commit -m "security: Remove leaked credentials"
   
   # Force push (jika diperlukan)
   git push origin main --force-with-lease
   ```

4. **Notify Team (jika kolaboratif):**
   - Beritahu tim bahwa keys sudah diganti
   - Minta semua update `.env` mereka

## 🛡️ GitHub Repository Settings

### Recommended Settings

1. **Branch Protection Rules:**
   - Settings → Branches → Add rule
   - Enable "Require pull request reviews"
   - Enable "Require status checks to pass"

2. **Secret Scanning:**
   - Settings → Code security and analysis
   - Enable "Secret scanning"
   - Enable "Push protection"

3. **Dependabot Alerts:**
   - Enable untuk monitoring vulnerabilities

## 📝 Commit Message Guidelines

### Good Examples
```bash
git commit -m "feat: Add hybrid RAG with Gemini"
git commit -m "docs: Update README with security guidelines"
git commit -m "security: Remove sensitive files from tracking"
git commit -m "fix: Update dependencies for compatibility"
```

### Bad Examples (AVOID)
```bash
git commit -m "Added API key AIza..." ❌
git commit -m "Update .env" ❌
git commit -m "Fixed stuff" ❌
```

## 🔍 Pre-Commit Checklist

Sebelum setiap commit, cek:

```bash
# 1. Cek status
git status

# 2. Cek diff
git diff

# 3. Pastikan tidak ada .env
git ls-files | grep -E '\.(env|key)$'

# 4. Test gitignore
git check-ignore .env chroma_db/
```

## 🌐 Deployment Security

### Production Environment

1. **Never use .env in production**
2. Use platform environment variables:
   - Streamlit Cloud: Secrets management
   - Heroku: Config Vars
   - Railway: Environment Variables

3. **Enable HTTPS only**

4. **Rate limiting untuk API calls**

## 📧 Contact

Jika menemukan security issue:
- **DO NOT** buat public issue
- Email langsung ke maintainer
- Gunakan GitHub Security Advisory

---

## ✅ Installation Success Summary

### Dependencies Installed
- ✅ Streamlit 1.52.1
- ✅ LangChain 1.2.0
- ✅ LangChain Community 0.4.1
- ✅ LangChain Google GenAI 4.1.1
- ✅ Google Generative AI 0.7.2
- ✅ ChromaDB 1.3.7
- ✅ PyPDF 6.4.2
- ✅ Tavily Python 0.7.16
- ✅ Python Dotenv 1.2.1

### Next Steps

1. **Create `.env` file:**
```bash
cp .env.example .env
```

2. **Add your API keys to `.env`:**
```env
GOOGLE_API_KEY=AIza...
TAVILY_API_KEY=tvly-...
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Verify git safety:**
```bash
git status  # .env should NOT appear
```

5. **Commit and push:**
```bash
git add .
git commit -m "fix: Update dependencies for Google Gemini compatibility"
git push origin main
```

---

**Last Updated:** December 17, 2025
