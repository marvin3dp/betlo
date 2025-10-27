# ☁️ Cloud Captcha Upload Feature

## Overview

Fitur ini memungkinkan bot untuk mengupload gambar captcha ke **uploader.sh**
dan menampilkan URL-nya di terminal. Sangat berguna saat menjalankan bot di VPS
tanpa GUI!

## Mengapa Fitur Ini Berguna?

Ketika menjalankan bot di VPS (headless mode), Anda tidak bisa melihat gambar
captcha secara langsung. Dengan fitur ini:

✅ Captcha otomatis diupload ke cloud ✅ URL ditampilkan di terminal dengan UI
yang sama ✅ Buka URL di browser lokal Anda untuk melihat captcha ✅ Input
captcha dari terminal VPS ✅ Tidak perlu download file atau setup SSH tunneling

## Cara Mengaktifkan

### 1. Konfigurasi (config.yaml)

Buka `config.yaml` dan set `upload_to_cloud` ke `true`:

```yaml
captcha:
  auto_open_image: true
  auto_solve: false
  manual_input: true
  save_image: true
  upload_to_cloud: true # ← Aktifkan fitur upload
  cloud_uploader_url: https://uploader.sh # ← URL uploader (default)
```

### 2. Install Dependencies

Library `requests` sudah ada di `requirements.txt`. Pastikan Anda sudah install:

```bash
pip install -r requirements.txt
```

Atau install manual:

```bash
pip install requests
```

### 3. Jalankan Bot

Jalankan bot seperti biasa:

```bash
python run.py
```

## Cara Kerja

1. **Bot Mendeteksi Captcha** → Saat bot menemukan captcha yang perlu input
   manual
2. **Upload Otomatis** → Gambar captcha diupload ke uploader.sh
3. **URL Ditampilkan** → Terminal menampilkan URL dengan UI yang cantik:

```
┌─────────────────────────────────────────────────┐
│          🔐 Manual Captcha Required 🔐          │
│                                                 │
│    ☁️  Captcha uploaded to cloud!              │
│    📎 URL: https://uploader.sh/abc123.png      │
│                                                 │
│    💡 Open this URL in your browser            │
│    📝 Enter the text you see                   │
│    (lowercase letters only)                    │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│               ☁️  Cloud Link                    │
│                                                 │
│    🌐 Captcha URL:                              │
│    https://uploader.sh/captcha_20241027.png    │
└─────────────────────────────────────────────────┘

? Enter captcha text: _
```

4. **Buka URL** → Copy URL dan buka di browser Anda
5. **Lihat Captcha** → Lihat gambar captcha di browser
6. **Input Captcha** → Ketik teks captcha di terminal VPS
7. **Done!** → Bot melanjutkan proses

## Konfigurasi Lanjutan

### Ganti Cloud Uploader

Jika ingin menggunakan service upload lain yang kompatibel dengan uploader.sh
API:

```yaml
captcha:
  upload_to_cloud: true
  cloud_uploader_url: https://your-custom-uploader.com
```

### Disable Upload (Local Mode)

Jika tidak perlu upload (misalnya running di desktop dengan GUI):

```yaml
captcha:
  upload_to_cloud: false # ← Disable upload
  auto_open_image: true # ← Buka image dengan app default
```

## API uploader.sh

Fitur ini menggunakan API sederhana dari uploader.sh:

```bash
# Upload menggunakan curl
curl https://uploader.sh/filename.png --data-binary @captcha.png

# Response: URL yang bisa diakses
https://uploader.sh/xyzabc.png
```

Bot menggunakan library `requests` untuk melakukan hal yang sama:

```python
response = requests.post(
    f"https://uploader.sh/{filename}",
    data=image_data,
    headers={'Content-Type': 'application/octet-stream'}
)
uploaded_url = response.text.strip()
```

## Troubleshooting

### Upload Gagal

**Error: "requests library not available"**

- Install: `pip install requests`

**Error: "Upload failed with status code: XXX"**

- Cek koneksi internet
- Cek apakah uploader.sh dapat diakses: `curl https://uploader.sh`
- Coba lagi

**Error: "Failed to upload image to cloud"**

- Cek ukuran file (uploader.sh biasanya batasi size)
- Cek format file (harus PNG/JPG)

### URL Tidak Muncul

Jika URL tidak muncul di terminal:

- Cek `upload_to_cloud: true` di config.yaml
- Cek logs untuk error message
- Cek screenshots folder untuk memastikan captcha tersimpan

### Image Tidak Bisa Dibuka

Jika URL upload berhasil tapi image tidak bisa dibuka:

- URL mungkin sudah expired (uploader.sh punya limit waktu)
- Coba refresh/retry
- Cek apakah ada typo di URL

## Mode VPS vs Local

### VPS (Headless) - Recommended Settings:

```yaml
captcha:
  auto_open_image: false # Tidak perlu open app (no GUI)
  upload_to_cloud: true # Upload ke cloud ✅
  manual_input: true
```

### Local Desktop - Recommended Settings:

```yaml
captcha:
  auto_open_image: true # Buka dengan image viewer ✅
  upload_to_cloud: false # Tidak perlu upload
  manual_input: true
```

### Hybrid (Best of Both):

```yaml
captcha:
  auto_open_image: true # Buka local jika bisa
  upload_to_cloud: true # + Upload untuk backup/remote access
  manual_input: true
```

## Security & Privacy

⚠️ **Catatan Penting:**

- Gambar captcha diupload ke service publik (uploader.sh)
- URL bisa diakses siapa saja yang punya link
- File biasanya auto-delete setelah beberapa waktu
- Tidak ada data sensitif di captcha (hanya text random)
- Image hanya berisi text captcha, tidak ada info pribadi

Jika concerned tentang privacy:

- Gunakan local mode (`upload_to_cloud: false`)
- Atau setup your own upload server

## Tips & Best Practices

1. **VPS Workflow:**
   - Enable `upload_to_cloud: true`
   - Keep terminal SSH connection open
   - Open URL di browser laptop/phone Anda
   - Input captcha dari terminal

2. **Testing:**
   - Test di local dulu sebelum deploy ke VPS
   - Pastikan `requests` library terinstall
   - Test koneksi ke uploader.sh

3. **Monitoring:**
   - Check logs jika upload gagal
   - URL valid sekitar 24 jam (depends on uploader.sh)
   - Screenshot tetap tersimpan di folder `screenshots/`

## Examples

### Example 1: VPS Bot dengan Cloud Upload

```bash
# Di VPS
cd ~/bots
source venv/bin/activate
python run.py

# Bot running...
# Captcha detected!
# ☁️  URL: https://uploader.sh/captcha_123.png

# Di browser lokal (laptop/phone)
# Open: https://uploader.sh/captcha_123.png
# Lihat captcha: "abcdef"

# Kembali ke terminal VPS
? Enter captcha text: abcdef
# ✅ Captcha solved!
```

### Example 2: Local Desktop dengan Auto-Open

```bash
# Di local desktop
cd ~/bots
source venv/bin/activate
python run.py

# Bot running...
# Captcha detected!
# 📸 Image opened automatically
# (Image viewer terbuka otomatis)

# Input di terminal
? Enter captcha text: abcdef
# ✅ Captcha solved!
```

## Support

Jika ada masalah atau pertanyaan:

1. Check logs di `logs/` folder
2. Check screenshots di `screenshots/` folder
3. Enable debug mode: `logging.level: DEBUG` di config.yaml
4. Check dokumentasi lain di `docs/` folder

---

**Happy Botting!** 🚀🤖
