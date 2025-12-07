# 🛡️ HEIMDALL PROJECT CONTEXT

## 🎯 GOAL
Heimdall adalah framework Automation Testing in-house untuk Android yang dirancang agar:
1.  **Human-Readable:** Script `.heim` menggunakan Bahasa Indonesia yang mudah dipahami QA Manual.
2.  **Engineering Power:** Backend menggunakan Python yang robust dan scalable.
3.  **Visual Output:** Menghasilkan Laporan Word (.docx) dan Flowchart Bisnis (.png).
4.  **Platform:** Memiliki Web Dashboard (Streamlit) untuk kemudahan eksekusi.

## 🛠️ TECH STACK (Strict Rules)
* **Language:** Python 3.10+
* **Mobile Driver:** `uiautomator2` (Strictly NO Appium/Selenium for Mobile).
* **Visual Engine:** `Mermaid JS` (Render via API mermaid.ink).
* **GUI/Dashboard:** `Streamlit`, `Altair` (Charts), `Pandas`.
* **Packaging:** `PyInstaller` (Target Phase 4).

## 🧠 CORE ARCHITECTURE
1.  **Parser (`core/parser.py`):**
    * Menerjemahkan syntax: `JIKA` (Logic), `ULANGI` (Loop), `SIMPAN` (Memory), `JALANKAN` (Modular).
2.  **Driver (`core/driver.py`):**
    * **Resilience Mode:** Menggunakan *Soft Assertion* (Error dicatat, tapi script lanjut jalan).
    * **Smart Features:** Virtual FAB, Ghost Keyboard, Auto Scroll.
3.  **Visualizer (`reporters/map_builder.py`):**
    * Generates `flowchart.mmd` & `flowchart.png`.
    * **Rule:** Class styling wajib menggunakan `:::` (Triple Colon) untuk kompatibilitas Mermaid terbaru.
4.  **Web Dashboard (`app.py`):**
    * Menjalankan `main.py` via `subprocess` dengan flag `-u` (Unbuffered) untuk log realtime.
    * Menampilkan Pie Chart (Pass/Fail) & Tabel Detail Step secara live.

## 🗺️ HEIMDALL MASTER ROADMAP (LIVE STATUS)

### ✅ PHASE 1: THE FOUNDATION
* [x] **Smart Driver:** Auto-scroll, ID/Text/Desc search, Virtual FAB.
* [x] **Stability:** Ghost Keyboard, Anti-looping, Auto-dismiss keyboard.
* [x] **Logging:** API Sniffer (Status 200 OK).

### ✅ PHASE 2: THE BRAIN
* [x] **Global Memory:** `SIMPAN teks ... KE {Var}`.
* [x] **Conditional Logic:** `JIKA ... AKHIR JIKA`.
* [x] **Looping:** `ULANGI ... DARI [...]`.
* [x] **Modular:** `JALANKAN "file.heim"`.
* [x] **System Keys:** `TEKAN TOMBOL SISTEM`.

### ✅ PHASE 3: VISUAL INTELLIGENCE
* [x] **Mermaid Engine:** Migrasi Graphviz -> Mermaid JS.
* [x] **Smart Mapping:** Visualisasi Diamond (Logic) & Loop.
* [x] **Rendering:** Generate PNG otomatis & tempel ke Word.

### 🚧 PHASE 4: THE PLATFORM REVOLUTION (Current Focus)
* [x] **Dashboard GUI:** Interface web (Streamlit) & Device Manager.
* [x] **Live Console:** Log terminal realtime di browser.
* [x] **Analytics:** Pie Chart Pass/Fail & Detail Table.
* [x] **Resilience:** Soft Assertion implementation.
* [ ] **Portable Packaging:** Bungkus jadi `.exe` / `.app` (PyInstaller).

### 🔮 PHASE 5: ENTERPRISE SCALE (Target Launch Awal Tahun)
* [ ] **Automated Build:** GitHub Actions untuk auto-build installer.
* [ ] **Parallel Execution:** Menjalankan 1 script di banyak HP serentak.
* [ ] **Notification Bot:** Kirim report ke Slack/Telegram.

### 👻 PHASE 6: FUTURE EXPANSION
* [ ] **Native Desktop App:** Rewrite UI pakai Flet/Flutter.
* [ ] **Hybrid Driver:** Support Playwright untuk Web Testing.
* [ ] **Record & Replay:** Ghostwriter (Rekam klik mouse).

---

## 🤖 AI INSTRUCTIONS (ROADMAP PROTOCOL)

**UNTUK AI ASSISTANT:**
File ini adalah "Single Source of Truth" untuk status proyek Heimdall.
1.  **Update Otomatis:** Jika user menyatakan sebuah fitur telah selesai dikerjakan, KAMU WAJIB mengupdate status checkbox di bagian Roadmap di atas dari `[ ]` menjadi `[x]`.
2.  **Context Aware:** Selalu baca bagian "TECH STACK" sebelum memberikan saran kode baru. Jangan menyarankan library yang bertentangan (misal: jangan saranin Appium).
3.  **Refactoring:** Jika melakukan refactoring kode, pastikan sesuai dengan "CODING CONVENTIONS" (misal: Soft Assertion).
4.  **Reporting:** Jika user bertanya "Progress kita sampai mana?", rangkum status berdasarkan Roadmap di file ini.