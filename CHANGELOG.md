# Changelog - Model dan UI Update

## [3.0.0] - 2024-12-17 - SIMPLE & CLEAN REDESIGN 🎯

### 🎨 Complete Redesign - Simple, Clean, Minimalist
**Philosophy:** Simplicity first, no unnecessary elements

**Major Changes:**
1. **No Sidebar** - Removed sidebar completely, full width layout
2. **Clean Dark Theme** - GitHub/Discord inspired dark theme
3. **Simple Layout** - Header (sticky) + Chat + Input (fixed bottom)
4. **Minimalist Design** - Only essential elements, no clutter
5. **Professional** - Production-ready, clean, readable

**New Features:**
- **Sticky Header**: Title, subtitle, stats, controls always visible
- **Full Width Chat**: Max-width 1200px, centered, spacious
- **Fixed Input**: Always at bottom, WhatsApp-style UX
- **Clean Messages**: Simple cards with subtle borders
- **Source Tags**: Inline tags dengan hover effects
- **Welcome Screen**: Feature grid dengan 4 cards
- **Status Badge**: Online indicator dengan pulse animation
- **Control Buttons**: Reset & Reload di header

**Color System:**
```
Background: #0d1117, #161b22, #1f2937
Accent: #3b82f6 (Blue)
Text: #e6edf3, #8b949e
Border: #30363d
```

**Typography:**
- Font: Inter (Google Fonts)
- Weights: 300-700
- Sizes: 0.75rem - 2rem
- Line-height: 1.6-1.7

**Performance:**
- Minimal CSS (simple selectors)
- CSS-only animations
- No heavy effects
- Fast rendering
- Excellent mobile performance

**Files:**
- `ui.py` - Complete rewrite (simple theme)
- `app.py` - Complete rewrite (no sidebar layout)
- `DESIGN_SIMPLE.md` - New documentation
- Backups: `ui_backup_cyber.py`, `app_backup_cyber.py`

**Why This Version?**
- More professional
- Better readability
- Faster performance
- Cleaner code
- Better mobile UX
- Production-ready

---

## [2.0.0] - 2024-12-17 - MAJOR UI OVERHAUL 🎨

### 🚀 Complete UI Redesign - Ultra Modern Design
**Perombakan Total:** Desain UI dirombak 100% dengan tema modern glassmorphism

**Sidebar Permanen:**
- ❌ DIHAPUS: Tombol collapse sidebar (sidebar SELALU tampil)
- ✅ Fixed sidebar di sebelah kiri (320px width)
- ✅ Glassmorphism effect dengan backdrop blur
- ✅ Gradient background yang elegan
- ✅ Tidak ada lagi tombol hamburger yang menyulitkan

**New Design System:**
1. **Color Scheme:**
   - Background: Gradient purple (#0f0c29 → #302b63 → #24243e)
   - Primary: Purple gradient (#667eea → #764ba2)
   - Accent: Pink gradient (#f093fb)
   - Text: Pure white (#ffffff) dengan opacity variations

2. **Typography:**
   - Font: Poppins (modern, clean, professional)
   - Sizes: Responsive dan hierarchy yang jelas
   - Weights: 300-800 untuk emphasis yang tepat

3. **Components:**
   - Glassmorphism cards dengan backdrop-filter blur
   - Smooth animations (slideInLeft, slideInRight, pulse, fadeIn)
   - Modern shadows dan borders
   - Gradient buttons dengan hover effects
   - Enhanced chat bubbles dengan better spacing

4. **Chat Interface:**
   - User messages: Glassmorphic cards, right-aligned
   - Bot messages: Clean cards with gradient AI icon
   - Improved typography dan line-height
   - Better source citations styling
   - Smooth slide-in animations

5. **Welcome Screen:**
   - Feature grid dengan hover effects
   - Modern card design dengan icons
   - Better information hierarchy
   - Engaging visual elements

6. **Responsive Design:**
   - Desktop: Full sidebar (320px)
   - Tablet: Medium sidebar (280px)
   - Mobile: Overlay sidebar dengan smooth transitions
   - Content adapts perfectly to all screen sizes

**Files Changed:**
- `ui.py` - Complete rewrite (555 lines → modern design system)
- `app.py` - Updated header, sidebar config, page setup
- `.streamlit/config.toml` - New theme colors, sidebar settings
- Backup created: `ui_old_backup.py`

**Removed:**
- All sidebar collapse button CSS
- Old color scheme (dark grey theme)
- All Inter font references
- Old animation styles
- Pulse animation for sidebar button (tidak perlu lagi)

**Added:**
- Poppins font family
- Glassmorphism design system
- New animation library (slideIn, fadeIn, etc.)
- Modern gradient system
- Enhanced responsive breakpoints
- Feature showcase components
- Better status indicators

## [1.4.1] - 2024-12-17

### Fixed - Sidebar Button Visibility
**Masalah:** Tombol untuk membuka/tutup sidebar tidak terlihat

**Solusi yang diterapkan:**
1. **Multiple CSS Selectors** - Menargetkan semua kemungkinan element sidebar button:
   - `[data-testid="baseButton-header"]`
   - `[data-testid="stSidebarCollapsedControl"]`
   - `button[aria-label*="Close sidebar"]`
   - `button[aria-label*="Open sidebar"]`

2. **Animated Pulse Effect** - Tombol berkedip untuk menarik perhatian:
   ```css
   animation: pulse 2s infinite;
   ```

3. **Enhanced Visibility**:
   - `display: flex !important`
   - `visibility: visible !important`
   - `opacity: 1 !important`
   - Gradient purple background yang mencolok
   - Shadow effect yang kuat

4. **Better Positioning**:
   - `position: fixed` di pojok kiri atas
   - `z-index: 999999` untuk always on top
   - `left: 0, top: 1rem`

5. **Hover Effects**:
   - Scale transformation (1.05x)
   - Enhanced shadow
   - Stop animation saat hover

**File yang diubah:**
- `ui.py` - Ditambah CSS untuk force show sidebar button
- `app.py` - initial_sidebar_state: "auto", ditambah visual hint dengan emoji dan bold text
- `.streamlit/config.toml` - Dihapus config yang tidak valid (hideSidebarNav)

## Perubahan yang Diterapkan

### 1. Update Model Groq (Update Terbaru)
**Masalah:** 
- Model `llama3-70b-8192` sudah tidak didukung (decommissioned)
- Model `llama-3.1-70b-versatile` juga sudah tidak didukung

**Solusi:** Diupdate ke `llama-3.3-70b-versatile` (model terbaru yang aktif)

**File yang diubah:**
- `app.py` - Line 128: model_name parameter
- `chain.py` - Line 24: default parameter
- `chain.py` - Line 248: default parameter di create_rag_chain

### 2. Perbaikan UI - Menghapus Emoticon

**Alasan:** Membuat UI lebih profesional dan konsisten

**Perubahan pada `app.py`:**
- Header: "# Hybrid RAG Chatbot" (tanpa robot emoji)
- Subtitle: Update ke "Llama 3.1 (70B)"
- Semua pesan error, warning, success: Dihapus emoticon
- Sidebar: Dihapus semua emoticon dari header dan tombol
- Spinner: Dihapus emoticon dari loading messages

**Perubahan pada `ui.py`:**
- Bot icon: Diubah dari "🤖" ke "AI"
- Sources: Diubah format dari emoji-based ke [Web]/[Doc] prefix
- Welcome message: Dihapus emoticon
- Status indicator: Diubah dari "⚡" ke "●"
- CSS: Ditambah styling untuk bot-icon text

**Perubahan pada `chain.py`:**
- Print statements: Diubah dari emoji ke [INFO]/[ERROR] prefix
- Sources: Dihapus emoji 📄 dan 🌐

**Perubahan pada `ingest.py`:**
- Semua print statements: Diubah ke format [OK]/[ERROR]/[WARNING]/[INFO]/[SUCCESS]
- Dihapus semua emoticon (✓, ✗, ⚠️, 🔍, 📄, ✂️, 🔮, ✅, 📁)

### 3. Perbaikan UI - Responsive Sidebar

**Penambahan CSS:**
```css
/* Sidebar responsive behavior */
[data-testid="stSidebar"] {
    min-width: 250px;
    max-width: 350px;
}

@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 200px;
        max-width: 280px;
    }
    .bot-icon {
        width: 32px;
        height: 32px;
        font-size: 0.8rem;
    }
}

@media (max-width: 480px) {
    .user-bubble, .bot-bubble {
        font-size: 0.85rem;
        padding: 0.75rem 1rem;
    }
}
```

**Fitur:**
- Sidebar otomatis menyesuaikan lebar pada mobile
- Chat bubbles responsive di berbagai ukuran layar
- Bot icon mengecil di mobile untuk menghemat space

## Testing

Setelah update, verifikasi:
1. ✅ Model baru bekerja (llama-3.1-70b-versatile)
2. ✅ UI bersih tanpa emoticon
3. ✅ Sidebar responsive di berbagai ukuran
4. ✅ Format sources lebih profesional ([Web]/[Doc])
5. ✅ Log messages konsisten dengan prefix

## Cara Menjalankan

```bash
streamlit run app.py
```

Browser akan membuka di `http://localhost:8501`

### 4. Perbaikan Sidebar Responsif (Update Terbaru)

**Masalah:** Sidebar tidak dapat diakses dengan mudah di mobile/tablet

**Solusi:**
- Tombol hamburger selalu terlihat di kiri atas
- Sidebar dapat dibuka/tutup dengan smooth animation
- Backdrop gelap saat sidebar terbuka di mobile
- CSS responsif untuk berbagai ukuran layar
- Initial state: expanded (sidebar terbuka default)

**Perubahan CSS:**
- Tombol collapsible dengan styling khusus (warna ungu)
- Sidebar fixed position di mobile dengan z-index tinggi
- Backdrop overlay saat sidebar terbuka
- Smooth transition untuk open/close

**File yang diubah:**
- `ui.py` - CSS untuk tombol dan responsivitas
- `app.py` - initial_sidebar_state = "expanded"
- `.streamlit/config.toml` - Konfigurasi sidebar

## Model yang Tersedia di Groq

Jika ingin mengganti model, pilihan yang tersedia (per Desember 2024):
- `llama-3.3-70b-versatile` (Terbaru dan terbaik, aktif) ⭐
- `llama-3.1-8b-instant` (Lebih cepat, kurang akurat)
- `mixtral-8x7b-32768` (Alternatif bagus)

Edit di `app.py` line 128 atau `chain.py` line 24.

**Catatan:** Model Groq sering diupdate. Cek https://console.groq.com/docs/models untuk list terbaru.
