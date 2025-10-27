# Display Modes & Strategies

Bot ini mendukung 3 mode operasi untuk VPS/server. Pilih berdasarkan kebutuhan
Anda.

---

## 📊 Mode Comparison

| Mode                        | Success Rate | Compatibility | RAM Usage | Setup Complexity |
| --------------------------- | ------------ | ------------- | --------- | ---------------- |
| **Xvfb + Visible**          | **95%+** ⭐  | **Excellent** | ~500MB    | Easy             |
| **Pure Headless + Stealth** | 60-80%       | Good          | ~300MB    | Automatic        |
| **Real Display**            | 100%         | Perfect       | ~500MB    | Not for VPS      |

---

## 🎯 MODE 1: Xvfb + Visible (RECOMMENDED)

### ⭐ Best Choice for VPS

**What is it:**

- Xvfb provides virtual X11 display
- Bot runs in "visible" mode
- No actual GUI window (headless server)
- Full browser rendering

**Why it works:**

- ✅ Zefoy sees normal browser behavior
- ✅ All JavaScript executes properly
- ✅ No headless detection
- ✅ All elements load correctly
- ✅ 95%+ success rate

**Setup:**

```bash
# 1. Auto-install via script
./run_xvfb.sh  # Handles everything automatically

# 2. Manual setup (if needed)
sudo apt install xvfb
nano config.yaml  # Set: headless: false
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
python run.py
```

**Config:**

```yaml
# config.yaml
browser:
  headless: false # Important! Let Xvfb provide display
  window_size: "1920,1080"
```

**When to use:**

- ✅ Running on VPS/server
- ✅ Want maximum Zefoy compatibility
- ✅ Have 2GB+ RAM available
- ✅ Can install Xvfb (sudo access)

**Logs you'll see:**

```
🖥️  Xvfb virtual display detected - Running in visible mode
✓ Best compatibility mode for Zefoy (95%+ success rate)
```

---

## 🎭 MODE 2: Pure Headless + Stealth (BACKUP)

### Fallback Option

**What is it:**

- Chrome runs in headless mode
- Stealth JavaScript hides automation
- Navigator properties mocked
- No Xvfb needed

**Why it sometimes fails:**

- ⚠️ Zefoy has aggressive detection
- ⚠️ May serve different HTML
- ⚠️ Some elements might not load
- ⚠️ 60-80% success rate

**Setup:**

```bash
# Automatic - no installation needed
nano config.yaml  # Set: headless: true
python run.py
```

**Config:**

```yaml
# config.yaml
browser:
  headless: true # Stealth auto-enabled
  window_size: "1920,1080"
```

**Stealth Features (Auto-Applied):**

- ✅ Hide navigator.webdriver
- ✅ Mock plugins/mimeTypes
- ✅ Mock chrome.runtime
- ✅ Realistic hardware properties
- ✅ Override permissions API

**When to use:**

- ✅ Cannot install Xvfb
- ✅ Very low RAM (<1GB)
- ✅ Quick testing
- ✅ Backup when Xvfb fails

**Logs you'll see:**

```
🎭 Headless mode enabled with stealth scripts
💡 For best Zefoy compatibility, use Xvfb: ./run_xvfb.sh
🎭 Applying stealth scripts (backup mode, 60-80% success)
✓ Stealth scripts applied
```

---

## 🖥️ MODE 3: Real Display (LOCAL ONLY)

### Local Development

**What is it:**

- Real GUI window
- See browser visually
- No detection issues
- 100% success rate

**When to use:**

- ✅ Local development/testing
- ✅ Debugging issues
- ✅ Initial setup
- ❌ **NOT for VPS** (no display available)

**Setup:**

```yaml
# config.yaml
browser:
  headless: false
```

```bash
# Just run normally (on machine with display)
python run.py
```

---

## 🔄 Auto-Detection Logic

Bot automatically detects environment:

```python
# Detection Flow:
1. Check config: headless setting
2. Check $DISPLAY environment variable
3. Check for Xvfb process

# Results:
- DISPLAY=:99 found → "Using Xvfb" (best)
- No DISPLAY, headless=false → Error (need Xvfb)
- No DISPLAY, headless=true → Stealth mode (backup)
- Real DISPLAY → Visible mode (local)
```

**Detection Messages:**

```bash
# Xvfb detected:
🖥️  Xvfb virtual display detected - Running in visible mode
✓ Best compatibility mode for Zefoy (95%+ success rate)

# No display, auto-headless:
⚠ No display detected (VPS/Server environment)
⚠ Auto-enabling headless mode with stealth
💡 For better Zefoy compatibility, use Xvfb: ./run_xvfb.sh

# Manual headless:
🎭 Headless mode enabled with stealth scripts
💡 For best Zefoy compatibility, use Xvfb: ./run_xvfb.sh
```

---

## 📋 Decision Tree

```
Are you on VPS/Server?
├─ YES → Can you install Xvfb (sudo)?
│   ├─ YES → Use Xvfb + Visible ⭐ (./run_xvfb.sh)
│   └─ NO  → Use Pure Headless + Stealth (headless: true)
│
└─ NO (Local Machine)
    └─ Use Real Display (headless: false)
```

---

## 🎯 Recommended Settings

### VPS/Server (with sudo):

```yaml
# config.yaml
browser:
  headless: false # Xvfb provides display
  window_size: "1920,1080"
  single_process: false
```

```bash
./run_xvfb.sh
```

### VPS/Server (no sudo):

```yaml
# config.yaml
browser:
  headless: true # Auto-stealth
  window_size: "1920,1080"
  single_process: false
```

```bash
python run.py
```

### Local Development:

```yaml
# config.yaml
browser:
  headless: false # See browser window
  window_size: "1920,1080"
```

```bash
python run.py
```

---

## 🐛 Troubleshooting by Mode

### Xvfb Issues:

```bash
# Xvfb not starting
sudo apt install xvfb

# Display not set
export DISPLAY=:99

# Check Xvfb running
ps aux | grep Xvfb

# Kill and restart
pkill Xvfb
./run_xvfb.sh
```

**⚠️ xkbcomp Warnings (SAFE TO IGNORE)**

If you see warnings like:

```
Could not resolve keysym XF86CameraAccessEnable
Could not resolve keysym XF86NextElement
...
Errors from xkbcomp are not fatal to the X server
```

- ✅ **These are harmless** - Xvfb works perfectly
- ✅ **Already suppressed** - Script hides these by default
- ✅ **No action needed** - Bot will run normally
- 💡 The message confirms: "not fatal to the X server"

### Headless + Stealth Issues:

```bash
# Enable debug to see if stealth applied
nano config.yaml  # Set: logging.level: DEBUG

# Check logs
grep "stealth" logs/betlo_*.log

# Should see:
# ✓ Stealth scripts applied

# If stealth fails → Use Xvfb!
./run_xvfb.sh
```

### Elements Not Detected:

```bash
# In headless mode → Switch to Xvfb
./run_xvfb.sh

# In Xvfb mode → Check DISPLAY
echo $DISPLAY  # Should be :99

# Enable debug mode
nano config.yaml  # Set: logging.level: DEBUG

# Check debug files
ls -lh debug/
cat debug/page_source_*.html
```

---

## 💡 Best Practices

### 1. Start with Xvfb

Always try Xvfb first on VPS:

```bash
./run_xvfb.sh
```

### 2. Test Locally First

Before deploying to VPS:

```yaml
# Local: headless: false
# Test everything works

# Then VPS: Use Xvfb
```

### 3. Enable Debug for Issues

```yaml
logging:
  level: DEBUG # See detailed info
```

### 4. Monitor Logs

```bash
# Real-time monitoring
tail -f logs/betlo_*.log

# Check for mode detection
grep "display\|stealth\|Xvfb" logs/betlo_*.log
```

### 5. Use Screen for 24/7

```bash
screen -S bot
./run_xvfb.sh
# Detach: Ctrl+A then D
```

---

## 📚 Related Documentation

- [VPS_SETUP.md](./VPS_SETUP.md) - Complete VPS guide
- [ZEFOY_HEADLESS_FIX.md](./ZEFOY_HEADLESS_FIX.md) - Zefoy-specific fixes
- [HEADLESS_STEALTH.md](./HEADLESS_STEALTH.md) - Stealth details
- [HEADLESS_MODE_GUIDE.md](./HEADLESS_MODE_GUIDE.md) - General headless

---

## 🆘 Quick Reference

```bash
# Xvfb (recommended)
./run_xvfb.sh

# Pure headless (backup)
python run.py  # with headless: true

# Check current mode
grep "display\|Xvfb" logs/betlo_*.log

# Switch to Xvfb
pkill -f chrome
./run_xvfb.sh

# Debug mode
nano config.yaml  # logging.level: DEBUG
ls -lh debug/
```

---

## Summary

**TLDR:**

1. **VPS → Use Xvfb** (`./run_xvfb.sh`) - 95%+ success ⭐
2. **No sudo → Pure Headless** (`headless: true`) - 60-80% success
3. **Local → Real Display** (`headless: false`) - 100% success

**Bottom Line:** Xvfb is the best solution for VPS. Stealth is kept as backup.
