# Chrome Connection Troubleshooting

## Error: "cannot connect to chrome at 127.0.0.1:XXXXX"

### Penyebab Umum

1. **Zombie Chrome processes** - Proses Chrome yang masih berjalan di background
2. **ChromeDriver version mismatch** - Versi ChromeDriver tidak cocok dengan
   Chrome
3. **Chrome tidak terinstall** - Google Chrome belum terinstall di sistem
4. **Port conflicts** - Port yang digunakan Chrome sudah dipakai
5. **Missing dependencies** - Library sistem yang diperlukan belum terinstall

---

## ✅ Solusi Otomatis (RECOMMENDED)

Jalankan script perbaikan otomatis:

```bash
cd [/path/to]/bots
bash fix_chrome.sh
```

Script ini akan:

- ✓ Kill zombie Chrome processes
- ✓ Check Chrome installation
- ✓ Update undetected-chromedriver
- ✓ Clean temporary files
- ✓ Check port conflicts
- ✓ Install missing dependencies
- ✓ Test Chrome startup

---

## 🛠️ Solusi Manual

### 1. Kill Zombie Chrome Processes

```bash
# Kill all Chrome processes
pkill -9 -f chrome
pkill -9 -f chromedriver

# Clean up temp files
rm -rf /tmp/.com.google.Chrome.*
rm -rf /tmp/.org.chromium.Chromium.*
rm -rf ~/.config/google-chrome/Singleton*
```

### 2. Install/Update Chrome

**Ubuntu/Debian:**

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable
```

**Check installation:**

```bash
google-chrome --version
# Output: Google Chrome 120.0.6099.109
```

### 3. Update undetected-chromedriver

```bash
# Upgrade to latest version
pip install --upgrade undetected-chromedriver

# Or reinstall
pip uninstall undetected-chromedriver
pip install undetected-chromedriver
```

### 4. Install Missing System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libglib2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0
```

### 5. Check Port Conflicts

```bash
# Check if port 9222 is in use
lsof -i :9222

# Kill process using the port
lsof -ti:9222 | xargs kill -9
```

### 6. Test Chrome Manually

```bash
# Test headless Chrome
google-chrome --headless --disable-gpu --no-sandbox --print-to-pdf=/dev/null about:blank

# If successful, Chrome will create a PDF and exit
```

---

## 🔧 Bot Improvements (Sudah Diterapkan)

Bot sekarang memiliki fitur baru untuk mengatasi masalah Chrome:

### 1. **Auto Zombie Process Cleanup**

Bot otomatis membersihkan proses Chrome yang menggantung sebelum start:

```python
def _kill_zombie_chrome_processes(self):
    # Kill Chrome and chromedriver processes
    subprocess.run(['pkill', '-f', 'chrome'])
    subprocess.run(['pkill', '-f', 'chromedriver'])
```

### 2. **Retry Mechanism**

Bot mencoba 3 kali dengan delay 2 detik antar percobaan:

```python
max_retries = 3
retry_delay = 2
```

### 3. **Better Error Messages**

Error messages sekarang memberikan solusi langsung:

```
Failed to initialize Chrome after all retries
Possible solutions:
1. Install/Update Chrome: sudo apt install google-chrome-stable
2. Kill zombie processes: pkill -f chrome
3. Update chromedriver: pip install --upgrade undetected-chromedriver
4. Check Chrome is in PATH: which google-chrome
```

### 4. **Stable Chrome Parameters**

```python
self.driver = uc.Chrome(
    options=options,
    version_main=None,
    use_subprocess=True,  # More stable
    driver_executable_path=None
)
```

### 5. **Additional Chrome Arguments**

```python
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

---

## 📝 Troubleshooting Steps

### Langkah 1: Coba run dengan headless mode

Edit `config.yaml`:

```yaml
browser:
  headless: true # Coba true dan false
```

### Langkah 2: Aktifkan DEBUG logging

Edit `config.yaml`:

```yaml
logging:
  level: DEBUG # Untuk log detail
```

### Langkah 3: Check logs

```bash
cat logs/betlo_*.log | grep -i "chrome\|driver\|error"
```

### Langkah 4: Manual test ChromeDriver

```bash
# Test if undetected_chromedriver works
python3 << EOF
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get('https://google.com')
print('Success!')
driver.quit()
EOF
```

### Langkah 5: Check Chrome processes

```bash
# See if Chrome is already running
ps aux | grep chrome

# Check ChromeDriver
ps aux | grep chromedriver
```

---

## 🚨 Common Error Messages & Solutions

### Error 1: "Chrome failed to start"

**Cause:** Chrome binary not found or corrupt **Solution:**

```bash
which google-chrome  # Check if Chrome is in PATH
sudo apt-get install --reinstall google-chrome-stable
```

### Error 2: "session not created: Chrome version must be between X and Y"

**Cause:** ChromeDriver version mismatch **Solution:**

```bash
pip install --upgrade undetected-chromedriver
# Or specify version
pip install undetected-chromedriver==3.5.5
```

### Error 3: "DevToolsActivePort file doesn't exist"

**Cause:** Chrome crash at startup or permission issues **Solution:**

```bash
# Clean Chrome cache
rm -rf ~/.config/google-chrome/
rm -rf /tmp/.com.google.Chrome.*

# Run bot with --no-sandbox
# (already included in bot code)
```

### Error 4: "chrome not reachable"

**Cause:** Chrome started but crashed or zombie process **Solution:**

```bash
# Kill all Chrome
pkill -9 -f chrome

# Run fix script
bash fix_chrome.sh
```

### Error 5: "Message: unknown error: Chrome failed to start: exited abnormally"

**Cause:** Missing system libraries **Solution:**

```bash
# Install all Chrome dependencies
sudo apt-get install -y libnss3 libgconf-2-4 libfontconfig1
```

---

## 🔍 Advanced Debugging

### Enable Chrome logging

```bash
# Set Chrome log path
export CHROME_LOG_FILE=/tmp/chrome_debug.log

# Run bot
python run.py

# Check Chrome logs
cat /tmp/chrome_debug.log
```

### Check Chrome with verbose output

```bash
google-chrome --headless --disable-gpu --enable-logging --v=1 about:blank 2>&1 | tee chrome_test.log
```

### Test with minimal options

Create test script `test_chrome.py`:

```python
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)
    print("✓ Chrome started successfully")
    driver.get('https://google.com')
    print(f"✓ Page title: {driver.title}")
    driver.quit()
    print("✓ Chrome closed successfully")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run test:

```bash
python3 test_chrome.py
```

---

## 📚 Additional Resources

### Check Chrome version compatibility

```bash
# Chrome version
google-chrome --version

# Python undetected_chromedriver version
python3 -c "import undetected_chromedriver as uc; print(uc.__version__)"

# Selenium version
python3 -c "import selenium; print(selenium.__version__)"
```

### Update all dependencies

```bash
pip install --upgrade \
    selenium \
    undetected-chromedriver \
    opencv-python \
    pytesseract
```

---

## ✅ Quick Fix Checklist

- [ ] Run `bash fix_chrome.sh`
- [ ] Kill zombie processes: `pkill -f chrome`
- [ ] Update ChromeDriver: `pip install --upgrade undetected-chromedriver`
- [ ] Check Chrome installed: `google-chrome --version`
- [ ] Clean temp files: `rm -rf /tmp/.com.google.Chrome.*`
- [ ] Install dependencies: `sudo apt-get install libnss3 libgconf-2-4`
- [ ] Test Chrome manually: `google-chrome --headless about:blank`
- [ ] Check logs: `cat logs/betlo_*.log`
- [ ] Try headless mode: Set `browser.headless: true` in config.yaml
- [ ] Enable DEBUG: Set `logging.level: DEBUG` in config.yaml

---

## 🆘 If All Else Fails

1. **Complete reinstall:**

```bash
# Remove Chrome
sudo apt-get purge google-chrome-stable
rm -rf ~/.config/google-chrome/

# Remove Python packages
pip uninstall selenium undetected-chromedriver -y

# Reinstall
sudo apt-get install google-chrome-stable
pip install selenium undetected-chromedriver

# Run fix script
bash fix_chrome.sh
```

2. **Try alternative browser:** Edit bot code to use Chromium instead of Chrome
   (advanced)

3. **Check system resources:**

```bash
# Check memory
free -h

# Check disk space
df -h

# Check CPU
top
```

4. **Reboot system:**

```bash
sudo reboot
```

---

**Last Updated:** October 2025 **Bot Version:** 2.0.0
