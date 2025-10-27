# Headless Mode Stealth Features

Bot ini menggunakan advanced stealth techniques untuk membuat headless mode
tidak terdeteksi oleh website.

---

## 🎭 Stealth Features

### 1. JavaScript Injection

Bot automatically inject JavaScript untuk hide headless indicators:

```javascript
// Hide webdriver property
Object.defineProperty(navigator, "webdriver", {
  get: () => undefined,
});

// Mock plugins (headless = empty, normal browser = has plugins)
Object.defineProperty(navigator, "plugins", {
  get: () => [1, 2, 3, 4, 5],
});

// Mock Chrome runtime
window.chrome = { runtime: {} };
```

### 2. Chrome Arguments Optimization

**REMOVED (Red flags for detection):**

- ❌ `--disable-web-security` - Suspicious flag
- ❌ `--disable-extensions` - Unusual for regular browser
- ❌ `--remote-debugging-port=0` - Bot indicator

**KEPT (Stealth-friendly):**

- ✓ `--headless=new` - Modern headless mode
- ✓ `--disable-blink-features=AutomationControlled` - Hide automation
- ✓ `--start-maximized` - Realistic window behavior
- ✓ `--window-size=1920,1080` - Standard resolution

### 3. Navigator Properties Override

Bot mocks realistic browser properties:

| Property                        | Headless (Default) | Stealth (Modified) |
| ------------------------------- | ------------------ | ------------------ |
| `navigator.webdriver`           | `true`             | `undefined`        |
| `navigator.plugins`             | `[]`               | `[1,2,3,4,5]`      |
| `navigator.languages`           | `[]`               | `['en-US', 'en']`  |
| `navigator.vendor`              | `Google Inc.`      | `Google Inc.`      |
| `navigator.platform`            | `Linux x86_64`     | `Linux x86_64`     |
| `navigator.maxTouchPoints`      | `0`                | `1`                |
| `navigator.hardwareConcurrency` | varies             | `8`                |
| `navigator.deviceMemory`        | `undefined`        | `8`                |

### 4. CDP (Chrome DevTools Protocol)

Menggunakan `Page.addScriptToEvaluateOnNewDocument` untuk inject scripts sebelum
page load:

```python
self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": stealth_script
})
```

Ini memastikan scripts executed BEFORE any website JavaScript runs.

---

## 🔍 Detection Tests

### Test Headless Detection

Visit these sites untuk test apakah bot terdeteksi:

1. **Bot detection test:**

   ```
   https://bot.sannysoft.com/
   ```

   - Should show: "Normal browser behavior"
   - Should NOT show: "Headless Chrome detected"

2. **Headless test:**

   ```
   https://arh.antoinevastel.com/bots/areyouheadless
   ```

   - Should show: "You are NOT headless"

3. **WebDriver test:**
   ```javascript
   // Run in browser console
   console.log(navigator.webdriver); // Should be: undefined
   ```

---

## 🐛 Troubleshooting Headless Mode

### Issue 1: Captcha Not Detected

**Symptom:** Bot says "No captcha found" in headless mode

**Cause:** Page may render differently in headless

**Solution:**

```yaml
# config.yaml
browser:
  headless: true

captcha:
  auto_open_image: true # Enable this!
  save_image: true # Save captcha for inspection
```

### Issue 2: Service Buttons Not Found

**Symptom:** "Could not find service button" in headless

**Cause:** JavaScript may not fully load or selectors different

**Solution:**

```bash
# Take screenshot in headless mode
# Bot automatically saves screenshots on errors

# Check screenshots folder:
ls -lh screenshots/

# View screenshot to see what bot sees:
# screenshots/error_*.png
```

### Issue 3: Elements Not Clickable

**Symptom:** "Element not clickable" in headless but works in visible mode

**Cause:** Elements may be overlapped or not rendered properly

**Solutions:**

1. **Increase wait times:**

```yaml
# config.yaml
timeouts:
  element_wait: 15 # Increase from 10 to 15
  page_load: 45 # Increase for slow VPS
```

2. **Disable images (faster rendering):**

```yaml
browser:
  disable_images: true
```

3. **Try with Xvfb (virtual display):**

```bash
# Install Xvfb
sudo apt install xvfb

# Run with Xvfb
xvfb-run python run.py
```

### Issue 4: Page Content Not Loading

**Symptom:** Blank page or missing content in headless

**Cause:** Some sites detect headless and serve different content

**Diagnosis:**

```python
# Add this to take screenshot manually
# In betlo/bot.py, after page load:
self.driver.save_screenshot("screenshots/debug_page.png")
```

**Solutions:**

1. **Check stealth scripts are applied:**
   - Look for log: `✓ Stealth scripts applied successfully`
   - If not shown, stealth scripts failed

2. **Verify user agent:**

```yaml
# config.yaml
browser:
  user_agent: |
    Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

3. **Try visible mode on VPS with Xvfb:**

```bash
# Set headless: false in config.yaml
# Run with Xvfb
xvfb-run python run.py
```

---

## 📊 Headless vs Visible Comparison

| Feature         | Visible Mode      | Headless Mode (Stealth) |
| --------------- | ----------------- | ----------------------- |
| Display         | ✓ Shows window    | ✗ No window             |
| Speed           | Normal            | Faster (no GUI)         |
| RAM Usage       | ~500MB            | ~300MB                  |
| Detection Risk  | Low               | Low (with stealth)      |
| VPS Compatible  | ❌ Needs display  | ✓ Works on VPS          |
| Screenshots     | Manual            | Auto on errors          |
| Debugging       | Easy (see window) | Use screenshots         |
| Captcha Solving | Visual            | Auto-open image         |

---

## 🎯 Best Practices for Headless Mode

### 1. Always Test in Visible Mode First

```bash
# First, test in visible mode on local machine
# config.yaml: headless: false
python run.py

# If works, then enable headless for VPS
# config.yaml: headless: true
```

### 2. Enable Debug Logging

```yaml
# config.yaml
logging:
  level: DEBUG # Shows stealth script status
```

### 3. Use Auto-Open Captcha

```yaml
# config.yaml
captcha:
  auto_open_image: true # Essential for headless
  upload_to_cloud: true # For VPS access
```

### 4. Monitor Screenshots

```bash
# Bot saves screenshots on errors
# Check them regularly
ls -lt screenshots/ | head -10

# View latest error screenshot
eog screenshots/error_*.png  # Linux
open screenshots/error_*.png  # macOS
```

### 5. Increase Timeouts for VPS

```yaml
# config.yaml - VPS often slower
timeouts:
  page_load: 45
  element_wait: 15
  captcha_wait: 120
```

---

## 🔬 Advanced: Manual Stealth Testing

### Test Navigator Properties

```python
# Add to betlo/bot.py after driver setup
test_script = """
console.log('webdriver:', navigator.webdriver);
console.log('plugins:', navigator.plugins.length);
console.log('languages:', navigator.languages);
console.log('platform:', navigator.platform);
console.log('vendor:', navigator.vendor);
console.log('maxTouchPoints:', navigator.maxTouchPoints);
console.log('hardwareConcurrency:', navigator.hardwareConcurrency);
console.log('deviceMemory:', navigator.deviceMemory);
"""

self.driver.execute_script(test_script)
```

### Check for Headless Indicators

```javascript
// Run in browser console (after bot loads page)

// Should be undefined (not true)
console.log("webdriver:", navigator.webdriver);

// Should have plugins
console.log("plugins:", navigator.plugins.length);

// Should NOT be empty
console.log("languages:", navigator.languages);

// Should exist
console.log("chrome:", window.chrome);
```

---

## 🆘 Getting Help

If headless mode still not working:

1. **Check logs for stealth status:**

```bash
grep "stealth" logs/betlo_*.log
```

2. **Verify Chrome version:**

```bash
google-chrome --version
# Should be recent version (120+)
```

3. **Test basic headless:**

```bash
google-chrome --headless --no-sandbox --dump-dom https://google.com
# Should output HTML
```

4. **Check screenshots:**

```bash
# If no screenshots, bot may crash before taking them
ls -lh screenshots/
```

5. **Try with Xvfb:**

```bash
# Sometimes Xvfb works better than pure headless
xvfb-run python run.py
```

---

## 📚 Additional Resources

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Headless Chrome Detection](https://intoli.com/blog/not-possible-to-block-chrome-headless/)
- [Bot Detection Techniques](https://bot.sannysoft.com/)

---

**Need more help?** Check [VPS_SETUP.md](./VPS_SETUP.md) and
[HEADLESS_MODE_GUIDE.md](./HEADLESS_MODE_GUIDE.md)
