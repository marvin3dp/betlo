# Usage Guide

Comprehensive guide for using TikTok Bot effectively.

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Main Menu](#main-menu)
- [Starting the Bot](#starting-the-bot)
- [Executing Services](#executing-services)
- [Execution Modes](#execution-modes)
- [Statistics & Progress](#statistics--progress)
- [Settings Configuration](#settings-configuration)
- [Best Practices](#best-practices)
- [Tips & Tricks](#tips--tricks)

---

## Quick Start

### Basic Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 2. Run the bot
python run.py

# 3. From main menu, select "🚀 Start Bot"

# 4. Wait for captcha to be solved (automatic or manual)

# 5. Select "▶️ Execute Service"

# 6. Choose service (Hearts, Views, etc.)

# 7. Enter TikTok video URL

# 8. Select execution mode

# 9. Confirm and wait for completion
```

---

## Main Menu

When you run `python run.py`, you'll see the main menu:

```
╭────────────── 📌 Main Menu Options ──────────────╮
│                                                  │
│  🚀 Start Bot - Launch the automation bot        │
│  ⚙️  Configure Settings - Adjust bot config      │
│  📊 View Statistics - Check bot performance      │
│  📋 View Available Services - See service status │
│  ❓ Help - Get help and documentation            │
│  🚪 Exit - Close the application                 │
│                                                  │
╰──────────────────────────────────────────────────╯
```

### Main Menu Options

| Option                         | Description              | When to Use                             |
| ------------------------------ | ------------------------ | --------------------------------------- |
| 🚀 **Start Bot**               | Launches browser and bot | To begin automation                     |
| ⚙️ **Configure Settings**      | Change bot configuration | Before first run, or to adjust settings |
| 📊 **View Statistics**         | View bot statistics      | To check progress and performance       |
| 📋 **View Available Services** | Check service status     | To see which services are available     |
| ❓ **Help**                    | View help information    | When you need guidance                  |
| 🚪 **Exit**                    | Close application        | When finished                           |

---

## Starting the Bot

### Step 1: Select "🚀 Start Bot"

The bot will:

1. Initialize Chrome browser (visible or headless based on config)
2. Load Zefoy website
3. Detect and solve captcha automatically (if OCR enabled)
4. Show success message when ready

### Step 2: Captcha Solving

**Automatic (OCR Enabled):**

```
╭──────────── 🔍 OCR Captcha Solver ───────────╮
│                                               │
│  ⚡ FAST Mode: 30 attempts in 10-20s          │
│  🎯 Attempting to solve captcha...            │
│                                               │
│  [████████████████░░░░] 60% Complete          │
│                                               │
╰───────────────────────────────────────────────╯
```

**Manual (OCR Failed or Disabled):**

```
╭────────── ⌨️  Manual Captcha Input ───────────╮
│                                                │
│  Please enter captcha text (a-z, A-Z only):   │
│  > _                                           │
│                                                │
│  Image saved: screenshots/captcha_*.png        │
│                                                │
╰────────────────────────────────────────────────╯
```

**Tips:**

- Image auto-opens in headless mode (if `auto_open_image: true`)
- Only letters (a-z, A-Z), no numbers or special characters
- Case doesn't matter (converts to match image)
- Press Enter to submit

---

## Executing Services

### Bot Running Menu

After bot starts successfully:

```
What would you like to do?
  ▶️  Execute Service
  📊 View Statistics
  🎯 View Target Goals Progress
  🔄 Refresh Page
  ◀️  Back to Main Menu
```

### Execution Flow

#### 1. Select Service

```
Select a service:
  Hearts [✅ Available]
  Views [✅ Available]
  Shares [✅ Available]
  Favorites [✅ Available]
  Comments Hearts [✅ Available]
  Followers [❌ OFFLINE]
  Live Stream [❌ OFFLINE]
  ◀️  Cancel
```

**Service Status Indicators:**

- ✅ **Available** - Service is ready to use
- 🎯 **Marked** - Set as active service (visual only)
- ⚠️ **Disabled** - Service disabled in config
- ❌ **OFFLINE** - Service offline on Zefoy

#### 2. Enter Video URL

```
Enter TikTok video URL:
> https://www.tiktok.com/@username/video/1234567890
```

**Valid URL formats:**

- `https://www.tiktok.com/@user/video/1234567890`
- `https://vm.tiktok.com/XXXXXXXXX/`
- `https://vt.tiktok.com/XXXXXXXXX/`

#### 3. Choose Execution Mode

```
Select execution mode:
  Manual Executions (set number of times to execute)
  Target Amount (set target views/hearts/etc count)
  Goal Mode (use target from config)
```

See [Execution Modes](#execution-modes) for details.

#### 4. Configure Options

**For Manual Executions:**

```
How many times to execute? (default: 1):
> 5
```

**For Target Amount:**

```
Enter target hearts amount (e.g., 10000):
> 10000

Target Amount: 10,000 hearts
Estimated Executions: ~100
(Based on ~100 per execution)
```

**For Goal Mode:**

```
╭──────────── 🎯 Hearts Goal ────────────╮
│                                        │
│  Target Goal: 10,000                   │
│  Current Progress: 2,500               │
│  Remaining: 7,500                      │
│  Per Execution: ~100                   │
│                                        │
╰────────────────────────────────────────╯
```

#### 5. Auto-Retry Option

```
Auto-retry when cooldown is detected?
> Yes
```

Recommended: **Yes** - Bot will wait and retry automatically.

#### 6. Confirm Execution

```
╭─────────── 🔍 Confirm Execution ───────────╮
│                                             │
│  Service: Hearts                            │
│  Video URL: https://tiktok.com/...          │
│  Mode: Target Amount                        │
│  Target: 10,000 hearts                      │
│  Auto-Retry: Yes                            │
│                                             │
╰─────────────────────────────────────────────╯

Execute this service?
> Yes
```

#### 7. Execution Progress

```
╭────────── ⏳ Processing ──────────╮
│                                   │
│  Executing service: Hearts        │
│  Please wait...                   │
│                                   │
╰───────────────────────────────────╯

[Progress updates appear here]

╭─────── ⏰ Cooldown Timer ───────╮
│                                 │
│  Next execution in: 3m 45s      │
│  [████████████░░░░░] 75%        │
│                                 │
╰─────────────────────────────────╯
```

---

## Execution Modes

### 1. Manual Executions

**Best for:** Quick boosts, testing, specific number of runs

**How it works:**

- You set number of executions (e.g., 5)
- Bot runs exactly that many times
- Stops after completing all executions

**Example:**

```
Executions: 5
Expected result: ~500 hearts (5 × ~100 per execution)
```

**Use cases:**

- Testing a service
- Quick boost before posting
- Limited time availability

---

### 2. Target Amount

**Best for:** Specific goals, one-time campaigns

**How it works:**

- You set target amount (e.g., 10,000 hearts)
- Bot calculates estimated executions needed
- Runs until target is reached or exceeded
- Tracks progress automatically

**Example:**

```
Target: 10,000 hearts
Current: 2,500
Remaining: 7,500
Estimated: ~75 more executions
```

**Use cases:**

- Reaching specific milestone
- Campaign goals
- One-time boost to specific number

---

### 3. Goal Mode

**Best for:** Long-term goals, continuous growth

**How it works:**

- Uses targets from `config.yaml`
- Tracks progress across sessions
- Continues from where you left off
- Saves progress automatically

**Configuration:**

```yaml
service_targets:
  hearts: 10000
  views: 50000
  followers: 1000

  per_execution:
    hearts: 100
    views: 1000
    followers: 50
```

**Features:**

- ✅ Progress saved between runs
- ✅ Automatic calculation
- ✅ Cross-session tracking
- ✅ Visual progress bars

**Use cases:**

- Long-term growth strategy
- Multiple sessions
- Consistent daily goals

---

## Statistics & Progress

### View Statistics (Main Menu)

**When bot is NOT running:**

```
╭───────── 📊 Bot Statistics ─────────╮
│                                     │
│  📊 Last Session Progress           │
│                                     │
│  • Hearts:                          │
│    Current: 2,500                   │
│    Target: 10,000                   │
│    Progress: 25.0%                  │
│    Executions: 25                   │
│                                     │
│  Total Executions: 25               │
│  Last Updated: 2025-10-23           │
│                                     │
╰─────────────────────────────────────╯
```

**When bot IS running:**

```
╭───────── 📊 Bot Statistics ─────────╮
│                                     │
│  Uptime: 1h 23m 45s                 │
│  Captchas Solved: 15                │
│  Tasks Completed: 12                │
│  Tasks Failed: 0                    │
│                                     │
│  Services Used:                     │
│    • Hearts: 8                      │
│    • Views: 4                       │
│                                     │
╰─────────────────────────────────────╯
```

### View Target Goals Progress

Detailed progress for all services:

```
╭──────────── 📊 Target Goals Progress ────────────╮
│                                                  │
│  Service     Current    Target   Progress   Execs│
│  Hearts      2,500      10,000   25.0%      25   │
│  Views       15,000     50,000   30.0%      15   │
│  Shares      500        2,000    25.0%      10   │
│                                                  │
╰──────────────────────────────────────────────────╯
```

---

## Settings Configuration

### Browser Settings

```
🌐 Browser Settings

Headless Mode: Run without browser UI
  Current: No
  Recommended: No (for first-time users)

Use AdBlock: Block ads for faster loading
  Current: Yes
  Recommended: Yes

Window Size: Browser resolution
  Current: 1920,1080
  Recommended: Keep default
```

### Captcha & OCR Settings

```
🔐 Captcha & OCR Settings

Current Mode: ⚡ FAST Mode

Options:
  🤖 Auto-solve Settings (OCR) - Enable/disable OCR
  ⌨️  Manual Captcha Input - Fallback settings
  ⚡ FAST Mode - Quick & optimized (10-20s)
  🐌 AGGRESSIVE Mode - Thorough & slower (3-5min)
```

**Recommended for beginners:**

- Auto-solve: **Enabled**
- Manual Input: **Enabled** (fallback)
- Mode: **FAST**

### Logging Settings

```
📝 Logging Settings

Log Level:
  • MAIN - Clean & simple (Recommended)
  • INFO - Standard with details
  • DEBUG - Verbose for troubleshooting

Current: MAIN
```

### Service Target Goals

```
🎯 Service Target Goals

Hearts target goal: 10000
Views target goal: 50000
Followers target goal: 1000
Shares target goal: 2000
```

---

## Best Practices

### 1. Start Small

```
✅ Do:
- Test with 1-2 executions first
- Verify service works
- Check cooldown times

❌ Don't:
- Run 100 executions on first try
- Use multiple services simultaneously
- Spam executions without cooldown
```

### 2. Use Auto-Retry

```yaml
retry:
  auto_retry_on_cooldown: true # ← Enable this
  max_attempts: 3
```

Benefits:

- Bot waits for cooldown automatically
- No need to manually retry
- Better success rate

### 3. Enable FAST Mode First

```yaml
captcha:
  auto_solve: true
  fast_mode: true # ← Start with this
  manual_input: true # ← Keep as fallback
```

Only switch to AGGRESSIVE if FAST mode fails repeatedly.

### 4. Monitor Progress

- Check statistics regularly
- Watch for errors in logs
- Verify targets are updating

### 5. Respect Cooldowns

```
Service cooldowns are normal:
- First execution: No cooldown
- After success: 2-5 minutes
- After cooldown: Variable

Let the bot wait - don't force it!
```

---

## Tips & Tricks

### Headless Mode for Background Operation

```yaml
browser:
  headless: true

captcha:
  auto_open_image: true # Important!
  save_image: true
```

Benefits:

- No browser window
- Lower resource usage
- Can use computer while bot runs
- Captcha still opens automatically

### Target Amount vs Goal Mode

**Use Target Amount when:**

- One-time goal
- Specific campaign
- Different target than config

**Use Goal Mode when:**

- Long-term goals
- Multiple sessions
- Consistent targets

### Debug Mode for Troubleshooting

```yaml
captcha:
  debug_mode: true

logging:
  level: DEBUG
```

This saves all preprocessing images to `screenshots/` for analysis.

### Chrome Cleanup

If bot becomes slow or crashes:

```bash
chmod +x fix_chrome.sh
./fix_chrome.sh
```

This kills zombie Chrome processes and cleans temp files.

### Save Screenshots

```yaml
captcha:
  save_image: true # Always save
  auto_open_image: true # Auto-open (headless)
```

Useful for:

- Manual solving
- Debugging OCR
- Headless mode
- Verifying captchas

---

## Common Workflows

### Workflow 1: Quick Daily Boost

```
1. Start Bot → Execute Service
2. Choose Hearts
3. Manual Executions: 5
4. Auto-retry: Yes
5. Let it run → ~500 hearts in 15-20 minutes
```

### Workflow 2: Target Campaign

```
1. Start Bot → Execute Service
2. Choose Views
3. Target Amount: 50,000
4. Auto-retry: Yes
5. Let it run → ~50 executions over 4-5 hours
```

### Workflow 3: Long-term Goals

```
1. Configure targets in config.yaml
2. Start Bot → Execute Service
3. Choose service
4. Goal Mode
5. Run daily until target reached
```

### Workflow 4: Headless Background

```
1. Set headless: true in config
2. Set auto_open_image: true
3. Start Bot
4. Solve captcha when image opens
5. Execute service
6. Continue using computer normally
```

---

## Troubleshooting During Use

### Captcha Keeps Failing

```
Solution 1: Try AGGRESSIVE mode
Solution 2: Use manual input
Solution 3: Check screenshots/ for quality
Solution 4: Verify Tesseract installed
```

### Service Shows Cooldown Immediately

```
This is normal! Services have cooldowns.

What to do:
- Enable auto_retry: true
- Let bot wait (3-5 minutes typical)
- Don't force execution
```

### Bot Stuck on "Processing"

```
Possible causes:
1. Network issue → Check internet
2. Page didn't load → Refresh page
3. Zefoy down → Try later

Solutions:
- Wait 30 seconds
- Select "🔄 Refresh Page"
- Restart bot if needed
```

### Statistics Not Updating

```
Check:
1. Service execution completed successfully
2. target_progress.json exists
3. No errors in logs

Solution:
- View Statistics again
- Check logs/ folder
- Verify service completed
```

---

## Getting More Help

- 📖 [README.md](../README.md) - Complete documentation
- 🤖 [OCR_TROUBLESHOOTING.md](OCR_TROUBLESHOOTING.md) - OCR issues
- 🌐 [HEADLESS_MODE_GUIDE.md](HEADLESS_MODE_GUIDE.md) - Headless mode
- 📝 [CHANGELOG.md](CHANGELOG.md) - What's new
- 🔧 [CHROME_TROUBLESHOOTING.md](CHROME_TROUBLESHOOTING.md) - Chrome issues

---

**Happy Automating! 🚀**
