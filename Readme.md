# **🛡️ HEIMDALL**

**"The All-Seeing QA Automation Tool"**

Halo Guys\! 👋

Selamat datang di **Heimdall**, tools automation *lokal* hasil gabut semaleman. Tools ini dibuat untuk mengatasi kejenuhan *regression test* manual tanpa harus terjebak kerumitan setup Appium.

Simpelnya: Heimdall membaca skenario bahasa manusia (.heim), menjalankannya di HP Android, lalu menyajikan **Laporan Word (Saga)** dan **Peta Alur (Mindmap)** yang rapi untuk dokumentasi proyek.

## **👁️ Apa itu Heimdall?**

**Asal Nama:**  
Diambil dari Heimdall, dewa penjaga jembatan Bifrost dalam mitologi Nordik yang memiliki penglihatan dan pendengaran super.
  
**Filosofi Tools Ini:**

* **Visi Jangka Panjang:** Tidak ada bug yang lolos dari pengawasan Heimdall. Tools ini memantau status HTTP (API), performa, dan UI secara *pixel-perfect*.  
* **Security:** Heimdall adalah penjaga gerbang (*Quality Gate*) sebelum aplikasi dirilis ke user. Jika Heimdall bilang "Merah", berarti dilarang rilis\!

## **🛠️ Tech Stack (Dapur Pacu)**

Kita menggunakan teknologi yang ringan, cepat, dan modern:

* 🐍 **Python 3.10+**: Otak utama logika automation.  
* 🤖 **uiautomator2**: Driver android yang lebih cepat dan ringan dibanding Appium.  
* 📊 **Graphviz**: Engine visualisasi untuk menggambar *Mindmap Flowchart*.  
* 📝 **Python-Docx**: Generator laporan dokumen otomatis.

## **🚀 Cara Install (Persiapan Perang)**

Sebelum mulai *running*, pastikan laptop kalian sudah siap. Lakukan langkah ini sekali saja:

### **1\. Install Python & Graphviz (Wajib\!)**

* **Python:** Pastikan sudah install Python versi 3.10 ke atas.  
* **Graphviz (⚠️ PENTING):**  
  * Tools ini butuh software Graphviz terinstall di OS agar Mindmap bisa digambar.  
  * **Windows:** Download installer di [graphviz.org](https://graphviz.org/download/). Saat install, **CENTANG OPSI "Add Graphviz to PATH"**.  
  * **Mac:** Buka terminal, ketik brew install graphviz.

### **2\. Install Library Project**

Buka terminal di folder project ini, lalu ketik:

```bash
pip install \-r requirements.txt
```

### **3\. Siapkan HP Android**

* Colok HP ke laptop via USB.  
* Pastikan **USB Debugging** sudah *ON*.  
* Jalankan inisialisasi driver (cuma perlu sekali seumur hidup per HP):
```bash  
  python \-m uiautomator2 init
```

  *(Izinkan semua instalasi aplikasi ATX/Automator di layar HP)*.

## **📝 Cara Membuat Script (.heim)**

Gak perlu jago coding\! Cukup buat file baru di folder scenarios/ dengan akhiran .heim. Gunakan bahasa manusia yang santai.

### **Cheat Sheet Syntax**

| Perintah | Contoh Script | Keterangan |
| :---- | :---- | :---- |
| **Buka** | Buka aplikasi "com.nama.package" | Membuka aplikasi berdasarkan Package Name. |
| **Ketik (Label)** | Ketik "user" pada kolom "Email" | Mencari kolom input di dekat label "Email". |
| **Ketik (Urutan)** | Ketik "123" pada kolom "urutan 1" | **Jurus Sakti\!** Mengisi kolom input pertama (index 0\) yang ditemukan di layar. Gunakan ini jika label susah dideteksi. |
| **Ketuk** | Ketuk tombol "Masuk" | Klik tombol/teks bernama "Masuk". |
| **Tunggu** | Tunggu sampai muncul teks "Home" | Menunggu (loading) sampai teks tertentu muncul. |
| **Pastikan** | Pastikan muncul teks "Success" | Validasi (Assertion). Jika teks tidak muncul, test dianggap **GAGAL**. |
| **Gulir** | Gulir ke "Bawah" | Scroll manual (Engine sudah punya *Smart Scroll*, tapi ini untuk memaksa). |

## **🔥 Fitur Baru: Clustering (Pengelompokan)**

Agar Mindmap terlihat rapi dan terkotak-kotak sesuai modul fitur, gunakan tag \# FITUR: ....

**Contoh Script Rapi (login\_scenario.heim):**

```

# Skenario Login Lengkap

# FITUR: Validasi Awal  
Buka aplikasi "com.nama.package"  
Tunggu sampai muncul teks "Selamat Datang"

# FITUR: Input Data  
# Menggunakan jurus urutan agar anti-meleset  
Ketik "emailuser@email.com" pada kolom "urutan 1"  
Ketik "rahasia123" pada kolom "urutan 2"  
Ketuk tombol "Masuk"

# FITUR: Dashboard  
# Validasi akhir untuk memastikan login sukses  
Tunggu sampai muncul teks "Login berhasil"  
Pastikan muncul teks "Home"
```

## **▶️ Cara Eksekusi**

Buka terminal di folder project, lalu jalankan perintah:

```bash
python main.py scenarios/nama\_file.heim
```

Contoh:
```bash
python main.py scenarios/login_scenario.heim
```

## **📂 Hasil Output (Panen Data)**

Setelah test selesai, cek folder reports/nama\_test\_kalian/. Kalian akan mendapatkan:

1. **📄 Laporan Word (Heimdall\_Saga\_...docx)**:  
   * Langkah demi langkah naratif \+ Screenshot bukti.  
   * **API Log Summary:** Tabel ringkas request API (Endpoint & Status Code) ala *Chucker* (misal: POST /login ✅ 200 OK).  
2. **🗺️ Mindmap (Heimdall\_Flow\_...png)**:  
   * Visualisasi alur testing.  
   * Node dikelompokkan dalam kotak-kotak Fitur (Cluster).  
   * Warna **Hijau** \= Sukses, **Merah** \= Gagal.

## **🔮 Roadmap**

Berikut adalah rencana pengembangan Heimdall ke depan:

* \[ \] Integrasi support iOS (via WebDriverAgent).
* \[ \] Integrasi Web Platform.  
* \[ \] Integrasi ke pipeline CI/CD (Jenkins/GitLab Runner).  
* \[ \] Kirim report otomatis ke Slack/Telegram Group.  
* \[ \] Fitur "Record & Replay" (Bikin script tanpa ngetik).  
* \[ \] ... *(Masih banyak lagi)*

*Happy Testing\! Biarkan Heimdall yang menjaga kualitas aplikasi kita.* 🛡️