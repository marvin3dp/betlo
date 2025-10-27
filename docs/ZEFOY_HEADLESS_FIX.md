# Zefoy Headless Mode Fix

Zefoy menggunakan **advanced bot detection** yang sangat agresif. Pure headless
mode mungkin tidak bekerja dengan sempurna.

## 🔴 Problem: Zefoy Not Working in Headless

**Symptoms:**

- ❌ Captcha button not detected
- ❌ Service buttons not found
- ❌ Page elements missing
- ❌ Bot says "No captcha present" but you know it's there

**Root Cause:**

- Zefoy serves different HTML untuk headless browsers
- Advanced JavaScript bot detection
- Dynamic content not loading properly
- Timing issues with page rendering

---

## ✅ SOLUTION 1: Use Xvfb (RECOMMENDED for VPS)

Xvfb provides **virtual display** - bot runs in "visible" mode but tanpa actual
GUI window.

**Ini adalah solusi paling reliable untuk VPS!**

### Quick Setup:

```bash
# 1. Install Xvfb
sudo apt install xvfb

# 2. Set config headless to FALSE
nano config.yaml
# Set: headless: false  # Important! Xvfb provides display

# 3. Run with Xvfb script
./venv.sh  # Smart auto-detect (uses Xvfb on VPS)
```

### Manual Xvfb:

```bash
# Start Xvfb on display :99
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Run bot (with headless: false in config)
python run.py

# Cleanup
pkill Xvfb
```

### Why Xvfb Works:

- ✓ Bot runs in "visible" mode
- ✓ Full page rendering like real browser
- ✓ No headless detection
- ✓ All JavaScript executes normally
- ✓ Works on VPS without GUI

---

## ✅ SOLUTION 2: Debug Mode (Diagnosis)

If Xvfb doesn't work atau you want to understand the problem:

### Enable Debug Logging:

```yaml
# config.yaml
logging:
  level: DEBUG # Shows detailed info
```

### Check Debug Output:

```bash
# Run bot
python run.py

# Bot will save page source and screenshots to debug/ folder
ls -lh debug/

# View page source to see what bot sees:
cat debug/page_source_initial_load_*.html

# View screenshot:
eog debug/screenshot_initial_load_*.png  # Linux
open debug/screenshot_initial_load_*.png  # macOS
```

### What to Look For:

1. **Empty page or basic HTML?**
   - Zefoy detected headless, serving minimal content
   - Solution: Use Xvfb

2. **JavaScript errors?**
   - Check browser console in screenshot
   - May need to wait longer

3. **Elements present but not found?**
   - Selector may be wrong
   - Elements might be dynamically loaded

---

## ✅ SOLUTION 3: Increase Timeouts

Bot sekarang automatically waits longer di headless mode, tapi you can increase
more:

```yaml
# config.yaml
timeouts:
  page_load: 60 # Increase from 30
  element_wait: 20 # Increase from 10
  captcha_wait: 180 # Increase from 120
```

**Current Auto-Behavior:**

- Headless mode: Waits 5-7 seconds after page load
- Visible mode: Waits 2-3 seconds
- Plus document.readyState check
- Plus 2-3 second dynamic content wait

---

## ✅ SOLUTION 4: Check Stealth Status

Verify stealth scripts are working:

```bash
# Run bot and check logs
python run.py 2>&1 | grep -i stealth

# Should see:
# [DEBUG] Applying stealth scripts for headless mode...
# [DEBUG] ✓ Stealth scripts applied successfully
```

If NOT seen:

- Scripts failed to apply
- CDP commands not supported
- Chrome version too old

**Fix:**

```bash
# Update Chrome
sudo apt update
sudo apt upgrade google-chrome-stable

# Verify version
google-chrome --version
# Should be 120+ for best stealth support
```

---

## ✅ SOLUTION 5: Try Different Chrome Arguments

### Option A: Minimal Arguments (Less Aggressive)

Edit `betlo/bot.py`, comment out some arguments:

```python
# Remove these if causing issues:
# options.add_argument("--disable-gpu")
# options.add_argument("--disable-software-rasterizer")
```

### Option B: Add User Data Dir

```python
# In betlo/bot.py, add:
options.add_argument("--user-data-dir=/tmp/chrome_profile")
```

---

## 📊 Mode Comparison

| Mode               | Detection Risk | Page Rendering | VPS Compatible | Success Rate |
| ------------------ | -------------- | -------------- | -------------- | ------------ |
| Pure Headless      | High           | May be partial | ✓              | 40-60%       |
| Headless + Stealth | Medium         | Better         | ✓              | 70-80%       |
| Xvfb + Visible     | Low            | Full           | ✓              | 95%+         |
| Real Display       | None           | Full           | ❌             | 100%         |

**Recommendation:** Use **Xvfb + Visible mode** for VPS.

---

## 🧪 Testing Strategy

### 1. Test Locally First (Visible Mode)

```yaml
# config.yaml
browser:
  headless: false
```

```bash
python run.py
```

**If works locally:**

- ✓ Bot code is OK
- ✓ Selectors are correct
- Problem is headless-specific

### 2. Test Headless Locally

```yaml
# config.yaml
browser:
  headless: true
```

```bash
python run.py
```

**If fails:**

- Zefoy detects headless
- Need Xvfb or better stealth

### 3. Test on VPS with Xvfb

```yaml
# config.yaml
browser:
  headless: false # Let Xvfb provide display
```

```bash
./venv.sh  # Smart auto-detect (uses Xvfb on VPS)
```

**Should work!**

---

## 🔍 Diagnostic Commands

### Check What Bot Sees:

```bash
# Enable DEBUG mode first
nano config.yaml
# Set: logging.level: DEBUG

# Run bot
python run.py

# Check debug files
ls -lh debug/

# View page HTML
cat debug/page_source_*.html | grep captcha
cat debug/page_source_*.html | grep "service"

# Check for JavaScript
cat debug/page_source_*.html | grep "<script"
```

### Check Chrome Process:

```bash
# While bot is running:
ps aux | grep chrome

# Should show chrome with correct arguments
# Check for: --headless, --no-sandbox, etc
```

### Check Display:

```bash
# Check DISPLAY variable
echo $DISPLAY

# If using Xvfb, should show: :99 or similar
# If empty, no display available

# Check Xvfb process
ps aux | grep Xvfb
```

---

## 🆘 Still Not Working?

### Last Resort Options:

#### 1. Use Screen Forwarding (Advanced)

```bash
# Install x11vnc
sudo apt install x11vnc

# Start Xvfb with VNC
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
x11vnc -display :99 -forever -shared &

# Connect with VNC client to see what's happening
# VNC to: your_vps_ip:5900
```

#### 2. Use Selenium Grid (Advanced)

Run Selenium Grid locally, connect from VPS.

#### 3. Disable Headless Completely

```yaml
# config.yaml
browser:
  headless: false
```

Then run with Xvfb:

```bash
./venv.sh  # Smart auto-detect (uses Xvfb on VPS)
```

---

## 📝 Checklist for VPS

Before reporting "headless not working":

- [ ] Tried with Xvfb? (`./venv.sh  # Smart auto-detect (uses Xvfb on VPS)`)
- [ ] Set headless: false when using Xvfb?
- [ ] Checked debug/ folder contents?
- [ ] Enabled DEBUG logging?
- [ ] Chrome version 120+?
- [ ] Checked logs for stealth status?
- [ ] Works in visible mode locally?
- [ ] Waited long enough? (5-10 seconds)
- [ ] Tried with clean Chrome profile?

---

## 💡 Best Practice

**For VPS/Server environments:**

1. ✅ **PRIMARY:** Use Xvfb with visible mode

   ```bash
   ./venv.sh  # Smart auto-detect (uses Xvfb on VPS)
   ```

2. ✅ **BACKUP:** Pure headless with stealth (60-80% success)

   ```yaml
   headless: true # Auto-stealth enabled
   ```

3. ✅ **DEBUG:** Enable DEBUG logging for diagnosis
   ```yaml
   logging.level: DEBUG
   ```

**For Local Development:**

1. ✅ Use visible mode for testing
2. ✅ Test headless before deploying to VPS
3. ✅ Enable debug mode to capture issues

---

## 📚 Additional Resources

- [VPS_SETUP.md](./VPS_SETUP.md) - Complete VPS setup
- [HEADLESS_STEALTH.md](./HEADLESS_STEALTH.md) - Stealth techniques
- [HEADLESS_MODE_GUIDE.md](./HEADLESS_MODE_GUIDE.md) - General headless guide
- [CHROME_TROUBLESHOOTING.md](./CHROME_TROUBLESHOOTING.md) - Chrome issues

---

## 🎯 Quick Commands

```bash
# Install Xvfb
sudo apt install xvfb

# Run with Xvfb (RECOMMENDED)
./venv.sh  # Smart auto-detect (uses Xvfb on VPS)

# Enable debug mode
nano config.yaml
# Set: logging.level: DEBUG

# Check debug output
ls -lh debug/
cat debug/page_source_*.html

# View screenshot
eog debug/screenshot_*.png

# Check stealth status
python run.py 2>&1 | grep stealth

# Kill everything and restart
pkill -9 -f chrome
pkill -9 -f Xvfb
./venv.sh  # Smart auto-detect (uses Xvfb on VPS)
```

---

**Bottom Line:** For VPS, **use Xvfb** with visible mode. It's the most reliable
solution for Zefoy's aggressive detection.
