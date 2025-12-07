# **🛡️ HEIMDALL**

**"The All-Seeing QA Automation Tool"**

Halo Guys\! 👋

Selamat datang di **Heimdall**, framework automation *in-house* yang didesain agar QA Manual bisa bikin automation tanpa pusing koding. Heimdall membaca skenario bahasa manusia (.heim), menjalankannya di Android, lalu menyajikan **Laporan Word (Saga)** dan **Flowchart Bisnis (Mermaid)** secara otomatis.

## **👁️ Apa itu Heimdall?**

Asal Nama:  
Diambil dari Heimdall, dewa penjaga jembatan Bifrost dalam mitologi Nordik yang memiliki penglihatan dan pendengaran super.  
**Filosofi Tools Ini:**

* **Visi Jangka Panjang:** Tidak ada bug yang lolos dari pengawasan Heimdall. Tools ini memantau status HTTP (API), performa, dan UI secara *pixel-perfect*.  
* **Security:** Heimdall adalah penjaga gerbang (*Quality Gate*) sebelum aplikasi dirilis ke user. Jika Heimdall bilang "Merah", berarti dilarang rilis\!

## **🛠️ Tech Stack (Dapur Pacu)**

Kita menggunakan teknologi yang ringan, cepat, dan modern:

* 🐍 **Python 3.10+**: Otak utama logika automation.  
* 🤖 **uiautomator2**: Driver android yang lebih cepat dan ringan dibanding Appium.  
* 🧜‍♀️ **Mermaid JS**: Engine visualisasi untuk menggambar *Business Flowchart* cantik.  
* 📝 **Python-Docx**: Generator laporan dokumen otomatis.

## **🚀 Cara Install (Persiapan Perang)**

Sebelum mulai *running*, pastikan laptop kalian sudah siap. Lakukan langkah ini sekali saja:

### **1\. Install Python (Wajib\!)**

Pastikan sudah install Python versi 3.10 ke atas.

### **2\. Install Library Project**

Buka terminal di folder project ini, lalu ketik:

```bash

pip install -r requirements.txt
```

### **3\. Siapkan HP Android**

* Colok HP ke laptop via USB.  
* Pastikan **USB Debugging** sudah *ON*.  
* Jalankan inisialisasi driver (cuma perlu sekali seumur hidup per HP):  
```bash
  python -m uiautomator2 init
```

  *(Izinkan semua instalasi aplikasi ATX/Automator di layar HP)*.

## **🧠 THE BRAIN: Fitur Cerdas Heimdall (Baru\!)**

Heimdall sekarang punya "Otak". Dia bisa mengingat data, mengambil keputusan, dan melakukan pengulangan. Berikut cara pakainya:

### **1\. Global Memory (SIMPAN & {...})**

Gunakan ini untuk menyimpan teks dari layar (misal: No Transaksi, Total Harga) dan memakainya lagi nanti.

* **Syntax:** SIMPAN teks dari "Selector" KE "{NamaVariabel}"  
* **Cara Pakai:** Panggil variabel dengan kurung kurawal {...}.

**Contoh Script:**

```

# 1. Ambil data dari layar  
SIMPAN teks dari "id/tv_order_number" KE "{NomorOrder}"

# 2. Pakai data tersebut di langkah berikutnya  
Ketuk tombol "Cari Pesanan"  
Ketik "{NomorOrder}" pada kolom "Search Bar"
```

### **2\. Conditional Logic (JIKA)**

Gunakan ini untuk menangani pop-up iklan, error sinkronisasi, atau kondisi yang tidak pasti.

* **Syntax:** Blok JIKA muncul teks "..." diakhiri dengan AKHIR JIKA.

**Contoh Script:**

```
# Cek apakah ada error sinyal?  
JIKA muncul teks "Gagal Terhubung"  
    Ketuk tombol "Coba Lagi"  
    Tunggu sampai muncul teks "Berhasil"  
AKHIR JIKA

# Lanjut kerja normal  
Ketuk tombol "Menu Utama"
```

### **3\. Looping (ULANGI)**

Gunakan ini untuk menginput banyak data sekaligus tanpa copy-paste script. Hemat waktu\!

* **Syntax:** Blok ULANGI "Var" DARI \["A", "B", "C"\] diakhiri SELESAI ULANGI.

**Contoh Script:**

```
# Input 3 jenis aktivitas berturut-turut  
ULANGI "Kategori" DARI ["Demoplot", "Gathering", "Kunjungan"]  
    Ketuk tombol "Tambah"  
    Ketuk tombol "{Kategori}"  
    Ketuk tombol "Simpan"  
SELESAI ULANGI
```

### **4\. Modular Script (JALANKAN)**

Gunakan ini untuk memanggil file .heim lain. Cocok untuk script Login yang dipakai berulang-ulang.

* **Syntax:** JALANKAN "path/to/file.heim"

**Contoh Script (master\_test.heim):**

```
# Panggil modul login biar gak ngetik ulang  
JALANKAN "scenarios/modules/login.heim"

# Lanjut tes fitur spesifik  
Ketuk tombol "Profile"
```

### **5. Tombol Sistem (TEKAN TOMBOL SISTEM)**

Gunakan ini untuk menekan tombol fisik Android (Back, Home, Enter).

* **Syntax:** TEKAN TOMBOL SISTEM "NamaTombol"  
* **Opsi:** "Back", "Home", "Enter", "Recent".

**Contoh Script:**
```
Ketuk tombol "Menu Dalam"  
# Kembali ke menu sebelumnya  
TEKAN TOMBOL SISTEM "Back"
```

## **📝 Cheat Sheet Syntax Dasar**

| Perintah | Contoh Script | Keterangan |
| :---- | :---- | :---- |
| **Buka** | Buka aplikasi "com.nama.package" | Membuka aplikasi berdasarkan Package Name. |
| **Ketik (Label)** | Ketik "user" pada kolom "Email" | Mencari kolom input di dekat label "Email". |
| **Ketik (Urutan)** | Ketik "123" pada kolom "urutan 1" | **Jurus Sakti\!** Mengisi kolom input pertama (index 0\) yang ditemukan. Gunakan ini jika label susah dideteksi. |
| **Ketuk** | Ketuk tombol "Masuk" | Klik tombol/teks bernama "Masuk". |
| **Ketuk (FAB)** | Ketuk tombol "FAB" | **BARU\!** Khusus klik tombol melayang (+) di pojok kanan bawah. Menggunakan koordinat pintar. |
| **Tunggu** | Tunggu sampai muncul teks "Home" | Menunggu (loading) sampai teks tertentu muncul. |
| **Pastikan** | Pastikan muncul teks "Success" | Validasi (Assertion). Jika teks tidak muncul, test dianggap **GAGAL**. |
| **Gulir** | Gulir ke "Bawah" | Scroll manual (Engine sudah punya *Smart Scroll*, tapi ini untuk memaksa). |


## **⚠️ Troubleshooting & Tips (Wajib Baca!)**
1. **Masalah Emulator: Keyboard Hilang?**
Heimdall menggunakan "Ghost Keyboard" (FastInputIME) untuk mencegah error looping fokus pada Emulator.

- **Efek Samping:** Saat script berjalan (atau setelah script stop mendadak/crash), Keyboard HP mungkin **TIDAK MUNCUL** saat kalian mau ngetik manual.

- **Solusi:** Tools ini sudah dilengkapi fitur Auto-Restore. Namun jika keyboard kalian hilang permanen:

   1. Jalankan script dummy sekali lagi sampai selesai (driver akan merestore keyboard di akhir sesi), ATAU

   2. Matikan FastInputIME manual lewat terminal:

```bash
adb shell settings put secure default_input_method com.android.inputmethod.latin/.LatinIME
```

2. Tips Tombol Tanpa ID (VirtualFAB)
- Jika ketemu tombol Tambah (+) yang melayang dan tidak punya ID:
Cukup tulis: Ketuk tombol "FAB".

- Driver otomatis menembak koordinat (X=85%, Y=80%) layar (di atas Bottom Bar).



## **▶️ Cara Eksekusi**

Buka terminal di folder project, lalu jalankan perintah:

```bash

python main.py scenarios/nama_file.heim
```

Contoh:

```bash

python main.py scenarios/pixel8_master_test.heim
```

## **📂 Hasil Output (Panen Data)**

Setelah test selesai, cek folder reports/nama\_test\_kalian/. Kalian akan mendapatkan:

1. **📄 Laporan Word (Heimdall\_Saga\_...docx)**:  
   * Format Slide Presentation (1 Step \= 1 Halaman).  
   * Narasi otomatis ala User ("User melakukan...").  
   * **API Log Summary:** Tabel ringkas request API (Endpoint & Status Code 200 OK).  
2. **🗺️ Flowchart Bisnis (flowchart.png)**:  
   * Diagram alur otomatis yang digambar oleh Mermaid JS.  
1.  **📄 Laporan Word (Heimdall\_Saga\_...docx)**:
    *   Format Slide Presentation (1 Step \= 1 Halaman).
    *   Narasi otomatis ala User ("User melakukan...").
    *   **API Log Summary:** Tabel ringkas request API (Endpoint & Status Code 200 OK).
2.  **🗺️ Flowchart Bisnis (flowchart.png)**:
    *   Diagram alur otomatis yang digambar oleh Mermaid JS.
    *   Memvisualisasikan **Logic (Diamond)** dan **Looping (Panah Balik)**.
    *   Dikelompokkan berdasarkan Cluster Fitur.

## **🗺️ HEIMDALL ASCENSION ROADMAP**

### ✅ PHASE 1: THE FOUNDATION (Pondasi Fisik)
**Status:** Completed 100%

*Fokus: Membangun driver yang stabil agar robot bisa berinteraksi dengan HP Android tanpa crash.*

- [x] **Smart Driver Engine (`core/driver.py`)**
    - **Robust Find:** Mencari elemen berdasarkan ID, Teks, atau Description secara bergantian.
    - **Auto Scroll:** Otomatis gulir ke bawah jika elemen tidak ditemukan di layar.
    - **Virtual FAB:** Klik koordinat khusus untuk tombol melayang (Floating Action Button).

- [x] **Stability Mechanism**
    - **Ghost Keyboard:** Menggunakan FastInputIME untuk mengetik cepat tanpa pop-up keyboard yang menutupi layar.
    - **Anti-Looping:** Mencegah robot terjebak mencari elemen selamanya (Timeout logic).

- [x] **Basic Reporting**
    - **Saga Writer:** Generate laporan .docx dengan format 1 Halaman = 1 Langkah + Screenshot.

- [x] **API Sniffer (`core/vision_log.py`)**
    - **Menangkap log HTTP request** di background (Status 200/500).

### ✅ PHASE 2: THE BRAIN (Kecerdasan Logika)
**Status:** Completed 100%

*Fokus: Membuat robot bisa "Mikir", mengingat data, dan mengambil keputusan.*

- [x] **Global Memory System (`core/state_manager.py`)**
    - **Syntax:** SIMPAN teks dari "ID" KE "{Variabel}".
    - **Fitur:** Menyimpan teks dari layar dan memanggilnya kembali di langkah berikutnya.

- [x] **Conditional Logic**
    - **Syntax:** JIKA muncul teks "X" ... AKHIR JIKA.
    - **Fitur:** Handling pop-up iklan, error message, atau alur bercabang.

- [x] **Looping Mechanism**
    - **Syntax:** ULANGI "Var" DARI ["A", "B"] ... SELESAI ULANGI.
    - **Fitur:** Input data massal atau cek menu berulang tanpa copy-paste script.

- [x] **Modular Architecture**
    - **Syntax:** JALANKAN "path/to/script.heim".
    - **Fitur:** Re-use script (misal: Login module dipanggil di banyak test).

- [x] **System Keys**
    - **Syntax:** TEKAN TOMBOL SISTEM "Back".
    - **Fitur:** Navigasi tombol fisik (Back, Home, Recent, Enter).

### ✅ PHASE 3: VISUAL INTELLIGENCE (Visualisasi Bisnis)
**Status:** Completed 100%

*Fokus: Mengubah log teknis menjadi Diagram Alur Bisnis yang cantik.*

- [x] **Mermaid JS Migration (`reporters/map_builder.py`)**
    - Mengganti Graphviz dengan Mermaid untuk hasil yang lebih modern.

- [x] **Smart Flowchart Mapping**
    - **Diamond Shape (🔸):** Otomatis menggambar percabangan saat ada logika JIKA.
    - **Loop Arrow (🔄):** Otomatis menggambar panah balik saat ada ULANGI.
    - **Cluster Coloring:** Memberi warna background berbeda untuk setiap fitur/modul.

- [x] **Rendering Engine**
    - **Hit API mermaid.ink** untuk convert kode teks jadi file .png.
    - **Auto-embed (tempel)** gambar Flowchart ke halaman pertama laporan Word.

### ✅ PHASE 4: THE PLATFORM REVOLUTION (Transformasi GUI & Portable)
**Status:** Completed 100% (READY FOR DEPLOY)

*Fokus: Web Dashboard, Resilience, dan Distribusi Aplikasi.*

- [x] **Heimdall Web Center**
    - **Dashboard GUI (Streamlit):** Device Manager, Scenario Selector (Folder Picker).

- [x] **Live Execution System**
    - **Real-time log console** di browser (Fix buffering Linux/Windows).

- [x] **Dynamic Resilience System**
    - **Soft Assertion (PASTIKAN):** Robot mencatat error tapi lanjut kerja (Non-blocking).
    - **Hard Assertion (WAJIB):** Robot berhenti total jika kondisi krusial tidak terpenuhi (Blocking).

- [x] **Anti-Crash Driver Core**
    - **Safe Tap/Swipe:** Otomatis switch ke Shell Command jika permission UIAutomator ditolak (Fix Xiaomi/Emulator).
    - **Self-Healing:** Auto-reset service jika driver macet.

- [x] **Analytics Dashboard**
    - **Pie Chart Pass/Fail** & Detail Table yang akurat.

- [x] **Cross-Platform Packaging**
    - **Build .exe (Windows) dan Binary (Linux)** menggunakan PyInstaller.
    - **Hybrid Logic:** Satu source code bisa jalan sebagai Script (Dev) maupun Worker (Portable).

### 🔮 PHASE 5: ENTERPRISE SCALE (Target Launch Awal Tahun)
**Status:** Planning / Backlog

*Fokus: Skalabilitas dan Distribusi Tim Besar.*

- [ ] **Automated Build System (GitHub Actions)**
    - Setup CI/CD pipeline.
    - Setiap push code -> Otomatis build installer untuk Windows, Mac, dan Linux.

- [ ] **Parallel Execution (Kage Bunshin)**
    - Menjalankan 1 script di 3 HP berbeda secara bersamaan (Stress Test).

- [ ] **Notification Hub**
    - Bot Telegram/Slack yang mengirim pesan: "Tes Selesai. Pass: 90%, Fail: 10%. Download report di sini."

### 👻 PHASE 6: FUTURE EXPANSION (Experimental)
**Status:** R&D (Research & Development)

*Fokus: Evolusi Teknologi Jangka Panjang.*

- [ ] **Native Desktop App Rewrite**
    - Jika Streamlit dirasa kurang native, rewrite UI menggunakan Flet (Flutter for Python) atau PyQt.

- [ ] **Hybrid Driver (Web Testing)**
    - Integrasi Playwright agar Heimdall bisa tes website desktop, bukan cuma Android.

- [ ] **Ghostwriter (Record & Replay)**
    - Fitur merekam layar dan klik mouse user, lalu otomatis generate script `.heim`.

- [ ] **Self-Healing AI**
    - Jika ID tombol berubah (karena update developer), robot mencoba mencari tombol alternatif berdasarkan kemiripan visual/teks.

*Happy Testing\! Biarkan Heimdall yang menjaga kualitas aplikasi kita.* 🛡️