import uiautomator2 as u2

# Konek ke HP/Emulator
d = u2.connect()

print("🔍 HEIMDALL UI SCANNER 🔍")
print("Sedang memindai layar saat ini...\n")

# Ambil semua elemen yang clickable (bisa diklik)
elements = d(clickable=True)

found_fab = False

for el in elements:
    # Ambil info elemen
    info = el.info
    text = info.get('text', '')
    desc = info.get('contentDescription', '')
    res_id = info.get('resourceName', '')
    class_name = info.get('className', '')
    
    # Filter biar gak nyampah (tampilkan yang relevan saja)
    if text or desc or res_id:
        print(f"--------------------------------------------------")
        print(f"📌 Class: {class_name}")
        print(f"   ID   : {res_id}")
        print(f"   Text : {text}")
        print(f"   Desc : {desc}")
        
        # Coba tebak apakah ini FAB?
        if "ImageButton" in class_name or "fab" in str(res_id).lower():
            print("   >>> 💡 KEMUNGKINAN INI ADALAH FAB! <<<")
            found_fab = True

print("--------------------------------------------------")
if not found_fab:
    print("\n⚠️ Tidak ditemukan elemen ciri-ciri FAB standar.")
    print("Coba cari elemen dengan Class 'android.widget.ImageButton' di list atas.")