# Frequently Asked Questions (FAQ)

Comprehensive FAQ for TikTok Bot users.

---

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Installation](#installation)
- [Configuration](#configuration)
- [OCR & Captcha](#ocr--captcha)
- [Services](#services)
- [Statistics & Progress](#statistics--progress)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Advanced](#advanced)

---

## General Questions

### What is this bot?

An automated TikTok service bot that works with Zefoy to provide:

- Hearts, Views, Shares, Followers, etc.
- Intelligent OCR captcha solver
- Beautiful terminal UI
- Progress tracking and statistics
- Headless mode support

### Is it safe to use?

**Technical Safety:** The bot uses undetected-chromedriver and mimics human
behavior.

**Account Safety:** No guarantees. Use at your own risk. Violating TikTok/Zefoy
ToS may result in account restrictions.

**Best Practices:**

- Don't abuse services
- Use reasonable limits
- Respect cooldowns
- Don't run 24/7

### Is it free?

Yes, the bot is free and open-source. Zefoy services are also free but have
cooldowns.

### Do I need a Zefoy account?

No. Zefoy doesn't require accounts. Just visit website and use services.

### Can I use it on mobile?

No. This is a desktop application requiring:

- Python 3.8+
- Chrome browser
- Tesseract OCR
- System resources (2GB+ RAM)

Works on: Linux, macOS, Windows (desktop)

---

## Installation

### Which Python version do I need?

**Minimum:** Python 3.8 **Recommended:** Python 3.11+ **Maximum:** Python 3.12
(tested)

**Check version:**

```bash
python --version
# or
python3 --version
```

### Why won't it install on Python 3.7?

Python 3.7 lacks features used by dependencies. Upgrade to 3.8+.

### Do I need to install Chrome?

Yes. The bot controls Chrome browser for automation.

**Alternatives:**

- Chromium (Linux)
- Chrome Beta/Dev (same API)

**Not supported:**

- Firefox
- Safari
- Edge (different API)

### Can I install without virtual environment?

**Not recommended** but possible:

```bash
# System-wide install (not recommended)
pip install -r requirements.txt

# May cause:
- Conflicts with other Python projects
- Permission errors
- Version conflicts
```

**Always use venv:**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Installation fails on Tesseract?

**Solution:**

```bash
# Linux
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH after install
```

**Verify:**

```bash
tesseract --version
```

---

## Configuration

### Where is the configuration file?

`config.yaml` in the project root:

```
bots/
├── config.yaml  ← Here
├── run.py
└── ...
```

### What's the difference between FAST and AGGRESSIVE mode?

| Feature       | FAST ⚡   | AGGRESSIVE 🐌 |
| ------------- | --------- | ------------- |
| Speed         | 10-20s    | 3-5 minutes   |
| Attempts      | ~30       | 300+          |
| Preprocessing | 5 methods | 12 methods    |
| OCR Configs   | 5 configs | 26 configs    |
| Success Rate  | 70-85%    | 75-90%        |
| Use When      | Daily use | FAST fails    |

**Recommendation:** Start with FAST, switch to AGGRESSIVE only if captcha
success rate is low.

### Should I enable headless mode?

**Headless Mode (headless: true):**

**Pros:**

- ✅ No browser window
- ✅ Lower resource usage
- ✅ Work while bot runs
- ✅ Cleaner desktop

**Cons:**

- ❌ Can't see what bot is doing
- ❌ Need auto_open_image for captcha
- ❌ Harder to debug

**Recommended:**

- First-time users: `headless: false`
- Experienced users: `headless: true` with `auto_open_image: true`

### What should I set service targets to?

**Conservative (Recommended for beginners):**

```yaml
service_targets:
  hearts: 5000 # ~50 executions
  views: 25000 # ~25 executions
  shares: 1000 # ~20 executions
```

**Moderate:**

```yaml
service_targets:
  hearts: 10000 # ~100 executions
  views: 50000 # ~50 executions
  shares: 2000 # ~40 executions
```

**Aggressive (Experienced users):**

```yaml
service_targets:
  hearts: 50000 # ~500 executions
  views: 100000 # ~100 executions
```

**Don't:**

- Set unrealistic goals (millions)
- Run continuously without monitoring
- Ignore cooldowns

---

## OCR & Captcha

### What's the captcha success rate?

**With FAST Mode:**

- Clean captcha: 85-95%
- With lines: 70-80%
- Heavy noise: 50-65%

**With AGGRESSIVE Mode:**

- Clean captcha: 90-98%
- With lines: 80-90%
- Heavy noise: 65-80%

**Factors affecting success:**

- Image quality
- Tesseract version
- Preprocessing settings
- Captcha difficulty

### OCR never works, what to do?

**Step-by-step troubleshooting:**

1. **Verify Tesseract:**

   ```bash
   tesseract --version
   ```

2. **Enable Debug Mode:**

   ```yaml
   captcha:
     debug_mode: true
   logging:
     level: DEBUG
   ```

3. **Check Screenshots:**
   - Look in `screenshots/`
   - Are preprocessing images clear?
   - Can YOU read the text?

4. **Try AGGRESSIVE Mode:**

   ```yaml
   captcha:
     fast_mode: false
     ocr_advanced:
       aggressive_preprocessing: true
       aggressive_ocr_configs: true
   ```

5. **Enable Manual Fallback:**

   ```yaml
   captcha:
     manual_input: true
   ```

6. **Read Guide:**
   - [OCR_TROUBLESHOOTING.md](OCR_TROUBLESHOOTING.md)
   - [AGGRESSIVE_OCR_MODE.md](AGGRESSIVE_OCR_MODE.md)

### Can I disable OCR and use manual only?

Yes:

```yaml
captcha:
  auto_solve: false # Disable OCR
  manual_input: true # Enable manual
  save_image: true # Save for viewing
  auto_open_image: true # Auto-open
```

**When to use:**

- OCR success rate very low (<30%)
- You prefer manual control
- Testing/debugging

### How do I solve captcha manually?

1. Captcha image will be saved to `screenshots/`
2. Image auto-opens (if `auto_open_image: true`)
3. Terminal shows: `Please enter captcha text:`
4. Type the letters you see (only a-z, A-Z)
5. Press Enter

**Tips:**

- Only letters, no numbers/special chars
- Case doesn't matter (bot converts)
- Look carefully at i/l, 0/O, etc.

### What if auto-open doesn't work in headless mode?

**Check configuration:**

```yaml
browser:
  headless: true

captcha:
  save_image: true # Must be true
  auto_open_image: true # Must be true
```

**Manual open:**

```bash
# While bot waits for input:
xdg-open screenshots/captcha_manual_*.png   # Linux
open screenshots/captcha_manual_*.png       # macOS
start screenshots\captcha_manual_*.png      # Windows
```

**See:** [HEADLESS_MODE_GUIDE.md](HEADLESS_MODE_GUIDE.md)

---

## Services

### Which services work?

**As of October 2025:**

✅ **Working:**

- Hearts
- Views
- Shares
- Favorites
- Comments Hearts

❌ **Offline (Zefoy disabled):**

- Followers
- Live Stream

**Note:** Service status changes based on Zefoy. Bot automatically detects
offline services.

### Can I use offline services?

You can try, but they likely won't work. Bot will warn you:

```
⚠️ Service Offline

Followers is currently OFFLINE on Zefoy.
This service may not work!

Continue anyway? No
```

### Why is service always on cooldown?

**This is normal!** Services have cooldowns:

**First execution:** No cooldown **After success:** 2-5 minutes typical **After
cooldown:** Variable (depends on Zefoy)

**What to do:**

- Enable `auto_retry_on_cooldown: true`
- Be patient
- Don't spam executions

**Cooldown times vary by:**

- Service type
- Time of day
- Zefoy server load

### Can I run multiple services simultaneously?

**Not recommended.**

**Why:**

- Browser can only view one page
- Might confuse bot logic
- Increased detection risk

**Instead:**

- Run one service at a time
- Complete or cancel before next
- Use execution modes efficiently

### How many executions per day is safe?

**Conservative:** 10-20 executions/day **Moderate:** 20-50 executions/day
**Aggressive:** 50+ executions/day (risky)

**Factors:**

- Account age
- Activity pattern
- Service type
- Previous violations

**Best practice:** Start small, increase gradually.

---

## Statistics & Progress

### Where are statistics stored?

**Session Statistics:** In memory (bot process)

- Lost when bot stops
- Shows live current session

**Progress:** `target_progress.json`

- Persists across sessions
- Tracks long-term goals
- Auto-saved after executions

### Statistics not showing in main menu?

**Possible causes:**

1. No previous session data
2. File not created yet
3. File permissions issue
4. Corrupted JSON

**Solutions:**

```bash
# Check file exists
ls target_progress.json

# Check permissions
chmod 644 target_progress.json

# Validate JSON
python -m json.tool target_progress.json

# If corrupted, delete and let bot recreate
mv target_progress.json target_progress.old
```

### Uptime format changed?

Yes! **Version 2.2.0** improved uptime display:

**Old:** `0:04:16.736806` (confusing) **New:** `4m 16s` (clean)

Auto-formats based on duration:

- `45s` (< 1 minute)
- `4m 16s` (< 1 hour)
- `1h 23m 45s` (≥ 1 hour)

### Can I reset progress?

Yes:

**Reset specific service:**

```bash
# Edit target_progress.json
# Set current: 0, executions: 0 for service
```

**Reset all:**

```bash
# Delete file
rm target_progress.json

# Bot creates new file on next run
```

**Or through code:**

```python
import json
data = json.load(open('target_progress.json'))
data['services']['Hearts']['current'] = 0
data['services']['Hearts']['executions'] = 0
json.dump(data, open('target_progress.json', 'w'), indent=2)
```

---

## Performance

### Bot is slow, how to speed up?

**Quick wins:**

```yaml
browser:
  headless: true # No UI overhead
  use_adblock: true # Faster page loads
  disable_images: true # Even faster

captcha:
  fast_mode: true # Quick OCR

timeouts:
  between_actions: 1 # Minimal delays
```

**System:**

- Close other Chrome instances
- Close unnecessary programs
- Ensure good internet connection

### High CPU/RAM usage?

**Normal usage:**

- CPU: 10-30% during OCR
- RAM: 200-500 MB
- Spikes during image processing

**If excessive:**

```bash
# Kill zombie Chrome
./fix_chrome.sh

# Restart bot
# Check for memory leaks in logs
```

### Captcha solving takes too long?

**If FAST mode (10-20s is normal):**

- This is expected
- Wait for completion
- Don't interrupt

**If AGGRESSIVE mode (3-5min is normal):**

- This is expected
- Switch to FAST if too slow

**If even FAST is slow (>1 minute):**

- Check CPU usage
- Verify Tesseract installation
- Check Debug logs for errors

---

## Troubleshooting

### Chrome keeps crashing?

**Solutions:**

1. **Clean zombies:**

   ```bash
   ./fix_chrome.sh
   ```

2. **Update ChromeDriver:**

   ```bash
   pip install --upgrade undetected-chromedriver
   ```

3. **Check Chrome version:**

   ```bash
   google-chrome --version
   ```

4. **Disable extensions:**

   ```yaml
   browser:
     use_adblock: false
   ```

5. **Increase timeouts:**
   ```yaml
   timeouts:
     page_load: 60
   ```

### Bot gets stuck?

**Common stuck points:**

**On "Loading page":**

- Network issue
- Zefoy down
- Firewall blocking

**On "Solving captcha":**

- OCR taking long (normal if AGGRESSIVE)
- OCR failed (will fallback to manual)

**On "Waiting for button":**

- Service on cooldown
- Bot waiting (normal)

**Solution:** Wait 30-60 seconds first. If still stuck, restart.

### Error: ChromeDriver version mismatch?

```bash
# Update undetected-chromedriver
pip install --upgrade undetected-chromedriver

# Or force reinstall
pip install --force-reinstall undetected-chromedriver

# Check Chrome version
google-chrome --version
```

### Logs showing errors?

**Check logs:**

```bash
tail -100 logs/betlo_*.log
```

**Common errors:**

**"Element not found":**

- Page didn't load
- Zefoy changed structure
- Network timeout

**"Captcha timeout":**

- OCR took too long
- Network issue
- Captcha image didn't load

**"Service unavailable":**

- Service offline on Zefoy
- Try different service

**Read:** [CHROME_TROUBLESHOOTING.md](CHROME_TROUBLESHOOTING.md)

---

## Advanced

### Can I modify OCR preprocessing?

Yes! Edit `betlo/captcha_solver.py`:

```python
def _preprocess_image(self, image):
    # Add your custom preprocessing here
    # Example: more aggressive line removal
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    # ... etc
```

**Caution:** Know what you're doing. Test thoroughly.

### Can I add new services?

Yes, if Zefoy adds new services:

1. **Add to config.yaml:**

   ```yaml
   zefoy:
     services:
       - name: "New Service"
         enabled: true
         button_class: "t-newservice-button"
   ```

2. **Add target:**

   ```yaml
   service_targets:
     new_service: 5000
     per_execution:
       new_service: 100
   ```

3. **Test thoroughly**

### Can I run bot as a service (systemd)?

**Not recommended** but possible:

```ini
# /etc/systemd/system/tiktok-bot.service
[Unit]
Description=TikTok Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/Documents/bots
Environment="PATH=/home/your-user/Documents/bots/venv/bin"
ExecStart=/home/your-user/Documents/bots/venv/bin/python run.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Issues:**

- Captcha solving requires interaction
- No terminal UI
- Monitoring difficult

**Better:** Use screen/tmux for long sessions.

### Can I use proxy?

Currently not built-in, but possible:

**Chrome proxy:**

```python
# In bot.py, add Chrome option:
options.add_argument('--proxy-server=http://proxy:port')
```

**System proxy:**

```bash
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
python run.py
```

### How to contribute?

See [README.md Contributing section](../README.md#-contributing)

**Quick steps:**

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## Still Have Questions?

### Documentation

- 📖 [README.md](../README.md) - Complete guide
- 📝 [USAGE_GUIDE.md](USAGE_GUIDE.md) - How to use
- 🔧 [INSTALLATION.md](INSTALLATION.md) - Install help
- 🤖 [OCR_TROUBLESHOOTING.md](OCR_TROUBLESHOOTING.md) - OCR issues
- 📊 [STATISTICS.md](STATISTICS.md) - Stats guide

### Support

- 💬 GitHub Discussions
- 🐛 GitHub Issues
- 📧 Email support (if available)

---

**Last Updated:** October 23, 2025 **Version:** 2.2.0

**[↑ Back to Top](#frequently-asked-questions-faq)**
