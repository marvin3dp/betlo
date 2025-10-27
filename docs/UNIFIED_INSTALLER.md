# 🚀 Unified Smart Installer

## Overview

The `install.sh` script has been enhanced with **smart environment detection** and now integrates all functionality previously split across multiple installation scripts.

---

## What Changed?

### Before (v3.x)
```
install.sh              # Basic Python/dependency installer
install_chrome_vps.sh   # Separate VPS Chrome installer
```

**Problems:**
- Users confused about which script to run
- VPS users had to run multiple scripts
- No automatic environment detection
- Manual configuration needed

### After (v4.0.0)
```
install.sh  # Unified smart installer (replaces both)
```

**Benefits:**
- ✅ **One script for everything**
- ✅ **Auto-detects** Desktop vs VPS
- ✅ **Auto-installs** Chrome + dependencies on VPS
- ✅ **Auto-installs** Xvfb for VPS
- ✅ **Smart error handling** with colored output
- ✅ **Environment-specific** instructions

---

## Smart Detection Features

### 1. Environment Detection

```bash
has_display() {
    # Check if DISPLAY is set
    if [ -n "$DISPLAY" ]; then return 0; fi
    
    # Check if xset can query X server
    if command -v xset &> /dev/null; then
        if xset q &> /dev/null 2>&1; then return 0; fi
    fi
    
    # Check if Xvfb is already running
    if pgrep -x "Xvfb" > /dev/null; then return 0; fi
    
    return 1
}
```

**Result:**
- Detects **Desktop** → Standard installation
- Detects **VPS** → Install Chrome + Xvfb + VPS dependencies

### 2. Chrome Installation (VPS Only)

When VPS is detected:
1. ✅ Downloads Google Chrome `.deb` package
2. ✅ Installs core dependencies (wget, ca-certificates, fonts, etc.)
3. ✅ Handles Ubuntu/Debian 24.04+ `t64` package variants
4. ✅ Installs Xvfb (X Virtual Framebuffer)
5. ✅ Provides VPS-specific instructions

### 3. Package Compatibility

**Handles version-specific packages:**

```bash
# Try standard packages first
sudo apt install -y \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2

# Fallback to t64 variants for Ubuntu 24.04+
|| sudo apt install -y \
    libatk-bridge2.0-0t64 \
    libgtk-3-0t64 \
    libasound2t64
```

### 4. Environment-Specific Output

**Desktop Output:**
```
🖥️  DESKTOP INSTALLATION COMPLETE
═══════════════════════════════════════════════════════

🚀 Quick Start (Recommended):
   ./venv.sh  # Smart auto-detect & run

📖 Manual Options:
   1. Activate virtual environment
   2. Run the bot
   3. Deactivate when done
```

**VPS Output:**
```
🖥️  VPS/SERVER INSTALLATION COMPLETE
═══════════════════════════════════════════════════════

⚠️  No display detected - VPS mode configured

🚀 Quick Start (Recommended):
   ./venv.sh  # Smart auto-detect & run

📖 Manual Options:
   Option 1: Xvfb Mode (Recommended for Zefoy)
   Option 2: Pure Headless Mode

💡 Tips for VPS:
   • Xvfb provides better compatibility with Zefoy
   • Ensure /dev/shm has at least 500MB
   • Run ./check_vps.sh to verify environment
```

---

## Migration Guide

### For New Users

**Just run:**
```bash
./install.sh
```

That's it! The script auto-detects everything.

### For Existing Users (v3.x)

**No changes needed!** But you can benefit from:

1. **Delete old script references:**
   ```bash
   rm -f install_chrome_vps.sh  # Now integrated in install.sh
   ```

2. **Re-run unified installer** (optional):
   ```bash
   ./install.sh
   ```

3. **Use smart runner** (recommended):
   ```bash
   ./venv.sh  # Auto-detects & runs optimally
   ```

---

## Technical Details

### What Gets Installed

#### All Platforms:
- Python 3.8+ virtual environment
- `python3-venv` and `python3-full`
- All Python dependencies from `requirements.txt`
- Tesseract OCR (if available, optional)

#### VPS/Server Only (Auto-Detected):
- Google Chrome (stable)
- Chrome dependencies:
  - `wget`, `ca-certificates`
  - `fonts-liberation`, `libnss3`
  - `libxss1`, `libgbm1`
  - `libappindicator3-1`, `libu2f-udev`
  - `libvulkan1`, `xdg-utils`
  - `libatk-bridge2.0-0` (or `t64` variant)
  - `libgtk-3-0` (or `t64` variant)
  - `libasound2` (or `t64` variant)
- **Xvfb** (X Virtual Framebuffer)

### Error Handling

**Smart fallbacks:**
- Package not found → Try `t64` variant
- Chrome download fails → Suggest Chromium alternative
- Xvfb install fails → Continue with headless warning
- VPS detection fails → Default to desktop mode (safe)

### Colored Output

**Color scheme:**
- 🟦 `CYAN` - Information/headers
- 🟩 `GREEN` - Success messages
- 🟨 `YELLOW` - Warnings
- 🟥 `RED` - Errors

Makes it easy to spot issues at a glance!

---

## Documentation Updates

All references to `install_chrome_vps.sh` have been removed/updated:

### Updated Files:
- ✅ `README.md` - VPS installation section
- ✅ `docs/VPS_SETUP.md` - All installation steps
- ✅ `docs/CHANGELOG.md` - v4.0.0 entry
- ✅ `RELEASE_v4.0.0.md` - New scripts section
- ✅ `check_vps.sh` - Error messages
- ✅ `betlo/bot.py` - Error troubleshooting
- ✅ `docs/FINAL_FIXES_v2.md` - Cloud provider instructions

### Deprecated:
- ❌ `install_chrome_vps.sh` - **Deleted** (functionality now in `install.sh`)

---

## Benefits Summary

| Feature | Before | After |
|---------|--------|-------|
| **Scripts Needed** | 2+ scripts | 1 script |
| **VPS Detection** | Manual | Automatic |
| **Chrome Install** | Manual/Separate | Automatic on VPS |
| **Xvfb Install** | Manual | Automatic on VPS |
| **Error Messages** | Generic | Environment-specific |
| **User Experience** | Confusing | Simple & clear |
| **Colored Output** | No | Yes |
| **Smart Fallbacks** | No | Yes |

---

## Troubleshooting

### Script Reports Wrong Environment

**Test detection manually:**
```bash
# Check if display is detected
echo $DISPLAY
xset q
pgrep -x "Xvfb"
```

**Force VPS mode:**
```bash
unset DISPLAY
./install.sh
```

### Chrome Not Installing on VPS

**Check network:**
```bash
wget -q --spider https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
echo $?  # Should be 0
```

**Manual install:**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

### Package Conflicts (t64 variants)

**Check Ubuntu/Debian version:**
```bash
lsb_release -a
```

**For Ubuntu 24.04+:**
Script automatically tries `t64` variants.

**For older versions:**
Script uses standard package names.

---

## Future Enhancements

Planned improvements:

- [ ] Support for more Linux distros (Fedora, Arch)
- [ ] Automatic Chrome version management
- [ ] Pre-flight checks before installation
- [ ] Rollback functionality
- [ ] Installation progress bar
- [ ] Docker container detection

---

## Credits

**Developed for v4.0.0 Major Release**

**Integration:** Merged `install_chrome_vps.sh` functionality into `install.sh`  
**Detection:** Smart environment detection based on `venv.sh` logic  
**UX:** Colored output and environment-specific instructions  
**Compatibility:** Ubuntu/Debian `t64` package support  

---

## See Also

- [VPS_SETUP.md](VPS_SETUP.md) - Complete VPS setup guide
- [DISPLAY_MODES.md](DISPLAY_MODES.md) - Display mode comparison
- [CHANGELOG.md](CHANGELOG.md) - Full v4.0.0 changelog
- [RELEASE_v4.0.0.md](../RELEASE_v4.0.0.md) - Release notes
