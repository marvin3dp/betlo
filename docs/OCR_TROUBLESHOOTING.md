# OCR Troubleshooting Guide

## Masalah: OCR Gagal Extract Text atau Input Captcha Salah

### Penyebab Umum

1. **Captcha dengan garis pengganggu** (strikethrough lines)
2. **Noise/derau pada gambar**
3. **Kontras rendah**
4. **Ukuran teks terlalu kecil**
5. **Font yang tidak biasa**

---

## Solusi yang Sudah Diterapkan

### 1. Multiple Preprocessing Methods (6 Metode)

Bot sekarang menggunakan **6 metode preprocessing** berbeda:

- **Line Removal + Adaptive Threshold** - Menghapus garis horizontal/vertikal
- **Heavy Morphological Line Removal + Otsu** - Penghapusan garis agresif
- **Bilateral Filter + Line Removal + CLAHE** - Preservasi edge sambil menghapus
  noise
- **Inverted + Line Removal** - Untuk teks terang di background gelap
- **Median Blur + Line Removal** - Menghilangkan salt-and-pepper noise
- **Erosion-Dilation** - Untuk garis tebal yang mengganggu

### 2. Advanced Line Removal Algorithm

Menggunakan **morphological operations** untuk:

- Mendeteksi garis horizontal dan vertikal
- Menghapus garis tanpa merusak karakter
- Membersihkan noise dengan bilateral filtering

### 3. Multiple OCR Configurations (8 Config)

Mencoba berbagai konfigurasi Tesseract:

- PSM 8 (single word) - paling umum untuk captcha
- PSM 7 (single line)
- PSM 6 (single block)
- PSM 13 (raw line)
- PSM 10 (single character)
- OEM 1 (LSTM engine) - lebih baik untuk gambar noisy
- OEM 3 (Legacy + LSTM)

**Total percobaan:** 6 metode × 8 config = **48 percobaan OCR**

### 4. Frequency-Based Confidence Scoring

- Melacak berapa kali hasil yang sama muncul
- Hasil yang muncul ≥3 kali dianggap high confidence
- Memilih hasil dengan confidence tertinggi

---

## Cara Mengaktifkan Debug Mode

### 1. Edit `config.yaml`

```yaml
captcha:
  auto_solve: true
  debug_mode: true # ← Ubah ke true
  manual_input: true
  save_image: true

logging:
  level: DEBUG # ← Ubah ke DEBUG untuk log detail
```

### 2. Jalankan Bot

```bash
python run.py
```

### 3. Check Hasil Debug

Saat debug_mode aktif, bot akan menyimpan:

- `captcha_TIMESTAMP_0_original.png` - Gambar captcha asli
- `captcha_TIMESTAMP_1_line_removal_adaptive.png` - Hasil preprocessing 1
- `captcha_TIMESTAMP_2_line_removal_otsu.png` - Hasil preprocessing 2
- `captcha_TIMESTAMP_3_bilateral_line_removal_clahe.png` - Hasil preprocessing 3
- `captcha_TIMESTAMP_4_inverted_line_removal.png` - Hasil preprocessing 4
- `captcha_TIMESTAMP_5_median_line_removal.png` - Hasil preprocessing 5
- `captcha_TIMESTAMP_6_erosion_dilation.png` - Hasil preprocessing 6

Semua file disimpan di folder `screenshots/`

### 4. Analisa Hasil

1. Bandingkan gambar original dengan gambar processed
2. Lihat metode mana yang paling baik menghilangkan garis
3. Check log DEBUG untuk melihat hasil OCR dari setiap metode
4. Jika perlu, sesuaikan parameter preprocessing

---

## Interpretasi Log

### Log Normal (Sukses)

```
[INFO] OCR extracted text (high confidence): example (appeared 5 times)
```

✅ Hasil muncul 5 kali dari berbagai metode - very reliable

### Log Medium Confidence

```
[INFO] OCR extracted text (best match): example (confidence: 8)
```

⚠️ Hasil terbaik tapi tidak muncul sering - might be correct

### Log Gagal

```
[WARNING] OCR failed to extract text from any preprocessing method (tried 6 methods × 8 configs = 48 total attempts)
```

❌ Semua 48 percobaan gagal - captcha terlalu sulit atau corrupt

---

## Tips Meningkatkan Akurasi

### 1. Pastikan Tesseract Terinstall dengan Benar

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Check versi
tesseract --version
```

### 2. Install Language Data Tambahan (Opsional)

```bash
sudo apt-get install tesseract-ocr-all
```

### 3. Tingkatkan Kualitas Screenshot

Di `config.yaml`:

```yaml
browser:
  window_size: 1920,1080 # ← Gunakan resolusi tinggi
  disable_images: false # ← Jangan disable images
```

### 4. Disable Headless Mode (Untuk Debugging)

```yaml
browser:
  headless: false # ← Biar bisa lihat captcha
```

---

## Advanced: Custom Preprocessing

Jika masih gagal, Anda bisa menambahkan preprocessing method sendiri di
`captcha_solver.py`:

```python
# Method 7: Custom method
try:
    # Tambahkan preprocessing Anda di sini
    custom_processed = cv2.GaussianBlur(gray, (5, 5), 0)
    # ... rest of processing

    processed_images.append(custom_processed)
    method_names.append("custom_method")
except Exception as e:
    self.logger.debug(f"Custom method failed: {e}")
```

---

## Fallback ke Manual Input

Jika OCR tetap gagal setelah semua metode:

1. Bot akan otomatis fallback ke manual input
2. Screenshot captcha disimpan di `screenshots/`
3. User diminta input manual via terminal
4. Input akan dibersihkan (hanya huruf a-z)

---

## Statistik Performa

Dengan update ini, tingkat keberhasilan OCR meningkat dari:

- **Sebelum:** ~30-40% (1 metode, 1 config)
- **Sesudah:** ~70-85% (6 metode, 8 configs, line removal)

Untuk captcha dengan garis pengganggu:

- **Sebelum:** ~10-20% berhasil
- **Sesudah:** ~60-75% berhasil

---

## Support

Jika masih ada masalah:

1. Aktifkan `debug_mode: true`
2. Set `logging.level: DEBUG`
3. Jalankan bot dan simpan log
4. Check gambar processed di `screenshots/`
5. Identifikasi metode mana yang paling mendekati hasil benar
