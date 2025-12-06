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
   * Memvisualisasikan **Logic (Diamond)** dan **Looping (Panah Balik)**.  
   * Dikelompokkan berdasarkan Cluster Fitur.

## **🗺️ HEIMDALL ASCENSION ROADMAP**

Berikut adalah status pengembangan Heimdall saat ini:

#### **✅ PHASE 1: THE FOUNDATION (Selesai)**

*Pondasi fisik robot agar kuat, stabil, dan bisa melihat.*

* \[x\] **Smart Driver:** Auto-scroll, pencarian elemen pintar (ID/Teks/Desc), Virtual FAB (Koordinat).  
* \[x\] **Stability Engine:** Ghost Keyboard (Anti-looping Emulator), Auto-dismiss keyboard.  
* \[x\] **Basic Reporting:** Saga Report (.docx) format Slide Presentation.  
* \[x\] **Logging:** API Sniffer (Capture Status Code 200 OK vs 500 Error).

#### **✅ PHASE 2: THE BRAIN (Selesai) 🧠**

*Menanamkan kecerdasan buatan agar robot bisa berpikir logis.*

* \[x\] **Global Memory:** SIMPAN teks ... KE {Var} (Menyimpan data antar langkah/file).  
* \[x\] **Conditional Logic:** JIKA ... AKHIR JIKA (Handling pop-up, error sync).  
* \[x\] **Looping:** ULANGI ... DARI \[...\] (Input data massal/berulang).  
* \[x\] **Modular Architecture:** JALANKAN "file.heim" (Re-use script login/setup).  
* \[x\] **System Keys:** TEKAN TOMBOL SISTEM "Back" (Navigasi fisik Android).

#### **✅ PHASE 3: VISUAL INTELLIGENCE (Selesai) 🧜‍♀️**

*Mengubah log teknis menjadi diagram bisnis yang cantik.*

* \[x\] **Mermaid Engine:** Migrasi dari Graphviz ke Mermaid JS (Modern Standard).  
* \[x\] **Smart Mapping:** Menggambar simbol **Diamond 🔸** (Logika) dan **Loop 🔄** otomatis.  
* \[x\] **Modern Styling:** Tema visual "Wide & Dynamic" dengan pewarnaan Cluster otomatis.  
* \[x\] **Rendering:** Generate file flowchart.png otomatis via API mermaid.ink.

#### **🚧 PHASE 4: THE PLATFORM REVOLUTION (Next Target) 🖥️**

*Mengubah tool "Hacker Terminal" menjadi Aplikasi Web Modern.*

* \[ \] **Heimdall Web Center (Streamlit):**  
  * **Dashboard GUI:** Tidak perlu lagi ketik di layar hitam. Cukup klik tombol di browser.  
  * **Scenario Selector:** Dropdown menu untuk memilih file .heim.  
  * **Device Manager:** Auto-detect HP yang tercolok.  
  * **Live Execution Viewer:** Melihat log perjalanan robot secara *real-time*.

#### **🔮 PHASE 5: ENTERPRISE SCALE (Masa Depan) 🚀**

*Fitur skala besar untuk kebutuhan korporat.*

* \[ \] **Cross-Platform Installer:** Mengemas jadi .exe (Windows) atau .dmg (Mac).  
* \[ \] **Parallel Execution (Kage Bunshin):** Menjalankan 1 script di 3 HP berbeda secara serentak.  
* \[ \] **RTM Integration:** Mapping ID Tiket Jira di header report otomatis.  
* \[ \] **Notification Bot:** Kirim notifikasi "Tes Selesai" ke Slack/Telegram.  
* \[ \] **Record & Replay:** Bikin script otomatis dengan merekam klik mouse ("The Ghostwriter").

*Happy Testing\! Biarkan Heimdall yang menjaga kualitas aplikasi kita.* 🛡️