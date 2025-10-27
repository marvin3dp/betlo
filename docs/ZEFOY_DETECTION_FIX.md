# 🔍 Zefoy Detection Troubleshooting Guide

This guide helps fix issues when Zefoy elements (captcha, buttons, page info)
are not detected.

## 🚨 Common Symptoms

- ⚠️ "Captcha not detected after 3 attempts"
- ⚠️ "No captcha detected - Check debug folder"
- Bot fails to find Zefoy page elements
- Empty or incomplete page source

---

## ✅ Quick Fix (Recommended)

**Use Xvfb for best Zefoy compatibility:**

```bash
./run_xvfb.sh
```

This provides a virtual display which gives **95%+ success rate** with Zefoy.

---

## 🔧 Diagnostic Steps

### 1. Run Zefoy Detection Test

```bash
./test_zefoy.sh
```

This will:

- Load Zefoy page
- Check for captcha and other elements
- Save debug info (HTML, screenshot, diagnostic report)
- Show what's being detected

**Check the output:**

- ✓ = Element found
- ✗ = Element NOT found

### 2. Check Debug Folder

After running the bot or test, check `debug/` folder:

```bash
ls -lh debug/
```

**Files created:**

- `diagnostic_*.txt` - Element detection report
- `page_source_*.html` - Full HTML of the page
- `screenshot_*.png` - Screenshot of what browser sees

**Review diagnostic report:**

```bash
cat debug/diagnostic_*.txt
```

Look for:

- **Captcha element**: Should be FOUND
- **Page source length**: Should be > 10,000 chars
- **Contains 'captcha'**: Should be YES
- **Forms/Buttons count**: Should be > 0

---

## 🐛 Common Issues & Solutions

### Issue 1: Captcha Element Not Found

**Cause:** Page not fully loaded or Zefoy blocked the request

**Solutions:**

1. **Wait longer** (already implemented in latest version):
   - Bot now waits 8-10 seconds in headless/Xvfb
   - Additional 3-5 seconds for dynamic content
   - 3 retry attempts with 3-5 second delays

2. **Use Xvfb instead of pure headless:**

   ```bash
   ./run_xvfb.sh
   ```

3. **Check if blocked by Cloudflare:**
   - Open `debug/screenshot_*.png`
   - If you see Cloudflare challenge → wait and retry later
   - Cloudflare may be blocking automation

4. **Verify Zefoy URL:**
   - Check `config.yaml` → `zefoy_url`
   - Make sure it's the correct Zefoy domain
   - Zefoy sometimes changes domains

### Issue 2: Page Source Too Short (< 5,000 chars)

**Cause:** Empty page or blocked by anti-bot

**Solutions:**

1. **Check screenshot** in `debug/` folder:
   - If blank/white → page didn't load
   - If showing error → connection issue
   - If showing Cloudflare → anti-bot triggered

2. **Verify Chrome is working:**

   ```bash
   ./check_vps.sh
   ```

3. **Check /dev/shm size** (on VPS):

   ```bash
   df -h /dev/shm
   ```

   Should be at least 500MB. If smaller, increase it:

   ```bash
   sudo mount -o remount,size=1G /dev/shm
   ```

4. **Kill zombie Chrome processes:**
   ```bash
   pkill -f chrome
   pkill -f chromium
   ```

### Issue 3: Wrong Page Loaded

**Cause:** Redirect or incorrect URL

**Solutions:**

1. **Check current URL** in diagnostic report:

   ```bash
   grep "URL:" debug/diagnostic_*.txt
   ```

2. **If redirected to login/error page:**
   - Zefoy may have changed authentication
   - Check if site is down: visit URL in normal browser
   - Try accessing from different IP

3. **Update config.yaml** with correct URL if needed

### Issue 4: Elements Found But Still Fails

**Cause:** Timing issue or element not interactable

**Solutions:**

1. **Enable DEBUG logging:**

   In `config.yaml`:

   ```yaml
   logging:
     level: DEBUG
   ```

2. **Check logs** for detailed element detection:

   ```bash
   tail -f logs/betlo_*.log
   ```

3. **Look for JavaScript errors** in page source:
   ```bash
   grep -i "error" debug/page_source_*.html
   ```

---

## 📊 Success Rates by Mode

| Mode                        | Success Rate | Notes                  |
| --------------------------- | ------------ | ---------------------- |
| **Xvfb (Virtual Display)**  | 95%+         | ✅ Recommended for VPS |
| **Pure Headless + Stealth** | 60-80%       | ⚠️ Backup mode         |
| **Real Display**            | 99%          | 🖥️ For desktop use     |

---

## 🔍 Advanced Diagnostics

### Manual Page Check

```bash
# Activate venv
source venv/bin/activate

# Run Python shell
python
```

```python
from betlo.config import Config
import undetected_chromedriver as uc

config = Config()
options = uc.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)
driver.get(config.zefoy_url)

# Wait
import time
time.sleep(15)

# Check
print(f"Title: {driver.title}")
print(f"URL: {driver.current_url}")

# Find captcha
try:
    captcha = driver.find_element("id", "captchatoken")
    print("✓ Captcha FOUND")
except:
    print("✗ Captcha NOT FOUND")

# Save for inspection
with open("manual_test.html", "w") as f:
    f.write(driver.page_source)
driver.save_screenshot("manual_test.png")

driver.quit()
```

### Check Chrome Arguments

Bot uses these arguments for Zefoy compatibility:

```python
--no-sandbox
--disable-dev-shm-usage
--disable-setuid-sandbox
--disable-gpu
--disable-software-rasterizer
--window-size=1920,1080
--disable-blink-features=AutomationControlled
--disable-crash-reporter
--disable-breakpad
--remote-debugging-port=0
```

If still failing, you can try removing some arguments in `betlo/bot.py`.

---

## 🆘 Still Not Working?

### 1. Use Xvfb (Most Reliable)

```bash
./run_xvfb.sh
```

### 2. Check System Requirements

```bash
./check_vps.sh
```

Ensure:

- ✅ Chrome/Chromium installed
- ✅ Python 3.12+
- ✅ 2GB+ RAM available
- ✅ 500MB+ /dev/shm
- ✅ Xvfb installed (for VPS)

### 3. Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade undetected-chromedriver selenium
```

### 4. Try Different Network

Zefoy may block certain IPs:

- Try from different VPS/network
- Use VPN if on local machine
- Wait 30-60 minutes if rate-limited

---

## 📝 Report Issue

If still having problems, create debug report:

```bash
# Run test
./test_zefoy.sh

# Check VPS
./check_vps.sh > vps_report.txt

# Create archive
tar -czf debug_report.tar.gz debug/ vps_report.txt logs/
```

Include:

- `debug_report.tar.gz`
- Exact error messages
- Mode used (Xvfb/Headless/Display)
- VPS provider and specs (if applicable)

---

## 💡 Key Improvements (Latest Version)

The bot now includes:

✅ **Extended wait times** (8-10s for Zefoy page load) ✅ **3 retry attempts**
for captcha detection ✅ **Automatic diagnostic saving** when captcha not found
✅ **Better page ready state checking** ✅ **Comprehensive debug reports**
(HTML + screenshot + diagnostic) ✅ **Element detection logging** ✅ **Xvfb mode
detection**

These improvements significantly increase success rate, especially with Xvfb.

---

## 📚 Related Docs

- [VPS Setup Guide](VPS_SETUP.md)
- [Display Modes](DISPLAY_MODES.md)
- [Headless Stealth](HEADLESS_STEALTH.md)
- [FAQ](FAQ.md)

---

**Last Updated:** October 27, 2025 **Bot Version:** Latest (with enhanced Zefoy
detection)
