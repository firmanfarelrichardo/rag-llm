# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 🚫 Google Gemini API Quota Exceeded

**Error Message:**
```
Error: RESOURCE_EXHAUSTED: 429 
Quota exceeded for metric: generativelanguage.googleapis.com/embed_content_free_tier_requests
```

**What This Means:**
- Your Google API key has reached its daily or per-minute request limit
- Free tier limits: 1,500 embedding requests per day
- Each PDF page can consume 2-5 requests depending on content size

**Solutions:**

#### 1. ⏰ Wait and Retry
- **Daily quota resets**: Wait 24 hours and try again
- **Per-minute quota**: Wait a few minutes before retrying
- The app will automatically retry 3 times with delays

#### 2. 🔑 Get a New API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new project
3. Generate a new API key
4. Replace the old key in the sidebar

**Why this works:** Each project has separate quota limits

#### 3. 📉 Reduce Document Size
- **Upload fewer pages**: Start with 10-20 pages max
- **Split large PDFs**: Break into smaller files
- **Test with small files first**: Verify setup before uploading large documents

#### 4. 📊 Monitor Your Usage
- Check usage: [Google AI Studio Usage Dashboard](https://ai.google.dev/gemini-api/docs/quota)
- View current limits and consumption
- Plan uploads accordingly

#### 5. 💳 Upgrade to Paid Plan
- If you need higher limits consistently
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Enable billing for unlimited requests (pay-per-use)

---

### 🔑 Invalid API Key Error

**Error Message:**
```
INVALID_ARGUMENT: API key not valid
```

**Solutions:**

1. **Verify API Key:**
   - Copy key carefully (no extra spaces)
   - Check if key is for Gemini API (not other Google APIs)

2. **Enable Gemini API:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Ensure Gemini API is enabled for your project

3. **Regenerate Key:**
   - Delete old key
   - Create fresh key
   - Use the new one

---

### 📄 PDF Processing Tips

**Best Practices:**

1. **Start Small:**
   ```
   ✅ Good: 1 PDF, 10-20 pages
   ❌ Avoid: Multiple 100+ page PDFs at once
   ```

2. **File Quality:**
   - Use text-based PDFs (not scanned images)
   - Ensure PDFs are not corrupted
   - Remove unnecessary pages

3. **Processing Time:**
   - Small files (< 20 pages): 1-2 minutes
   - Medium files (20-50 pages): 3-5 minutes
   - Large files (50+ pages): 5-10 minutes

---

### 🌐 Web Search Not Working

**Error Message:**
```
Tavily API Key is required
```

**Solutions:**

1. Get Tavily API Key:
   - Visit [Tavily.com](https://tavily.com)
   - Sign up for free account
   - Copy API key
   - Paste in sidebar

2. Free Tier Limits:
   - 1,000 searches per month
   - Sufficient for testing

---

### 💬 Chat Not Responding

**Possible Causes:**

1. **No Documents Loaded:**
   - Upload and process PDFs first
   - Wait for "Knowledge Base Ready" message

2. **API Key Issues:**
   - Verify both Google and Tavily keys are entered
   - Check quota limits

3. **Network Issues:**
   - Check internet connection
   - Retry after a few seconds

---

### 🔄 Application Performance

**Slow Performance:**

1. **Too Many Documents:**
   - Limit to 3-5 PDFs at a time
   - Total chunks should be < 500

2. **Large Context:**
   - Reduce chunk size in `.env`:
     ```
     CHUNK_SIZE=800
     CHUNK_OVERLAP=80
     ```

3. **Browser Memory:**
   - Close unused tabs
   - Clear browser cache
   - Use Chrome/Edge for best performance

---

## 📊 Understanding Quota Consumption

### Embedding Requests Calculation

**Example:**
- 1 page of text ≈ 500-1000 words
- Chunk size = 1000 characters ≈ 150-200 words
- 1 page = 3-5 chunks
- **1 PDF with 20 pages ≈ 60-100 embedding requests**

### Daily Usage Planning

With 1,500 requests/day:
- Small PDFs (20 pages each): ~15-25 documents
- Medium PDFs (50 pages each): ~6-10 documents
- Large PDFs (100 pages each): ~3-5 documents

**Recommendation:** Process documents in batches throughout the day

---

## 🆘 Still Having Issues?

1. **Check Error Logs:**
   - Look at terminal/console output
   - Note exact error messages

2. **Verify Environment:**
   - Python version: 3.13.7
   - Virtual environment activated
   - All dependencies installed

3. **Clear Cache:**
   ```bash
   # Delete ChromaDB cache
   rm -rf chroma_db/
   
   # Restart application
   streamlit run app.py
   ```

4. **Test API Keys:**
   - Try keys in Google AI Studio first
   - Verify they work outside the app

---

## 📝 Contact & Support

- **Documentation:** [README.md](README.md)
- **Security:** [SECURITY.md](SECURITY.md)
- **GitHub Issues:** Create issue on repository

---

## 💡 Pro Tips

1. **Test First:** Always test with a small PDF before uploading many documents
2. **Monitor Quota:** Keep track of daily usage to avoid surprises
3. **Multiple Keys:** Use different API keys for different projects
4. **Off-Peak Hours:** Process large documents during off-peak hours
5. **Backup Keys:** Keep 2-3 API keys as backup

---

**Last Updated:** December 17, 2025
