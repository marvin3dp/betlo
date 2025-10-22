# Statistics & Progress Tracking

Complete guide to bot statistics and progress tracking features.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Statistics Display](#statistics-display)
- [Target Goals Progress](#target-goals-progress)
- [Progress Files](#progress-files)
- [Understanding Metrics](#understanding-metrics)
- [Tips & Best Practices](#tips--best-practices)

---

## Overview

The bot tracks two types of statistics:

1. **Session Statistics** - Current bot session metrics
2. **Target Goals Progress** - Long-term goal tracking

Both are accessible from the bot menus and provide insights into performance and
progress.

---

## Statistics Display

### Accessing Statistics

**From Main Menu (Bot NOT Running):**

```
Main Menu → 📊 View Statistics
```

Shows last session progress from saved data.

**From Bot Running Menu:**

```
Bot Menu → 📊 View Statistics
```

Shows live current session statistics.

---

### Live Session Statistics

When bot is running, you'll see:

```
╭─────────────────────── 📊 Bot Statistics ───────────────────────╮
│                                                                 │
│                     Uptime: 1h 23m 45s                          │
│                     Captchas Solved: 15                         │
│                     Tasks Completed: 12                         │
│                     Tasks Failed: 0                             │
│                                                                 │
│                     Services Used:                              │
│                       • Hearts: 8                               │
│                       • Views: 4                                │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
```

#### Metrics Explained

**Uptime:**

- Time since bot started
- Format: `1h 23m 45s` or `4m 16s` or `45s`
- Resets when bot restarts
- User-friendly format (no microseconds!)

**Captchas Solved:**

- Number of captchas successfully solved
- Includes both OCR and manual solves
- Counter for current session only

**Tasks Completed:**

- Number of successful service executions
- Only counts completed tasks
- Excludes failed or cancelled tasks

**Tasks Failed:**

- Number of failed executions
- Includes captcha failures
- Network errors, timeouts, etc.

**Services Used:**

- Breakdown by service type
- Shows execution count per service
- Only shows services that were used

---

### Last Session Statistics

When bot is not running:

```
╭────────────────────── 📊 Bot Statistics ─────────────────────╮
│                                                              │
│                  📊 Last Session Progress                    │
│                                                              │
│  • Hearts:                                                   │
│    Current: 2,500                                            │
│    Target: 10,000                                            │
│    Progress: 25.0%                                           │
│    Executions: 25                                            │
│                                                              │
│  • Views:                                                    │
│    Current: 15,000                                           │
│    Target: 50,000                                            │
│    Progress: 30.0%                                           │
│    Executions: 15                                            │
│                                                              │
│  Total Executions: 40                                        │
│  Last Updated: 2025-10-23                                    │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
```

Features:

- ✅ Loads from `target_progress.json`
- ✅ Shows only services with activity
- ✅ Displays current progress vs targets
- ✅ Total executions counter
- ✅ Last update timestamp
- ✅ Helpful tip to start bot

---

## Target Goals Progress

### Accessing Target Progress

```
Bot Running Menu → 🎯 View Target Goals Progress
```

### Progress Table

```
╭───────────────── 📊 Target Goals Progress ─────────────────╮
│                                                            │
│  Service          Current    Target    Progress    Execs  │
│  ────────────────────────────────────────────────────────  │
│  Hearts           2,500      10,000    25.0%       25     │
│  Views            15,000     50,000    30.0%       15     │
│  Shares           500        2,000     25.0%       10     │
│  Favorites        800        3,000     26.7%       8      │
│                                                            │
╰────────────────────────────────────────────────────────────╯
```

### Progress Bars

```
╭────────────────── 📊 Progress Bars ──────────────────╮
│                                                      │
│  Hearts        [██████░░░░░░░░░░] 25.0%             │
│  Views         [████████░░░░░░░░░] 30.0%            │
│  Shares        [██████░░░░░░░░░░] 25.0%             │
│  Favorites     [██████░░░░░░░░░░] 26.7%             │
│                                                      │
╰──────────────────────────────────────────────────────╯
```

**Color Coding:**

- 🔴 Red: 0-25% (just started)
- 🟠 Orange: 25-50% (progressing)
- 🟡 Yellow: 50-75% (halfway there)
- 🟢 Green: 75-100% (almost done)
- ✅ Bold Green: 100%+ (completed!)

---

## Progress Files

### target_progress.json

Location: `bots/target_progress.json`

Structure:

```json
{
  "last_updated": "2025-10-23T14:30:00.123456",
  "services": {
    "Hearts": {
      "target": 10000,
      "per_execution": 100,
      "current": 2500,
      "executions": 25
    },
    "Views": {
      "target": 50000,
      "per_execution": 1000,
      "current": 15000,
      "executions": 15
    }
  }
}
```

**Fields Explained:**

- `last_updated` - ISO timestamp of last update
- `target` - Target goal from config
- `per_execution` - Average per execution
- `current` - Current progress count
- `executions` - Number of executions completed

**When Updated:**

- After each successful execution
- When starting Goal Mode
- When target values change in config

**Persistence:**

- Saved automatically
- Survives bot restarts
- Tracks across sessions
- Can be manually edited (careful!)

---

## Understanding Metrics

### Calculation Examples

#### Current Progress

```
Service: Hearts
Executions: 25
Per Execution: 100
Current = 25 × 100 = 2,500 hearts
```

#### Progress Percentage

```
Current: 2,500
Target: 10,000
Percentage = (2,500 / 10,000) × 100 = 25.0%
```

#### Remaining

```
Target: 10,000
Current: 2,500
Remaining = 10,000 - 2,500 = 7,500
```

#### Estimated Executions

```
Remaining: 7,500
Per Execution: 100
Estimated = 7,500 / 100 = 75 more executions needed
```

---

### Success Rate

**Calculation:**

```
Success Rate = (Tasks Completed / Total Tasks) × 100%

Example:
Completed: 12
Failed: 3
Total: 15
Success Rate = (12 / 15) × 100 = 80%
```

**What's Good:**

- 90%+ - Excellent (OCR working well)
- 80-90% - Good (Normal performance)
- 70-80% - Fair (Check OCR settings)
- <70% - Poor (Troubleshoot needed)

---

### Average Per Execution

**How It's Determined:**

From config:

```yaml
service_targets:
  per_execution:
    hearts: 100 # ← Manual setting
    views: 1000
    followers: 50
```

**Adjusting Values:**

If you notice different actual results:

```yaml
# Example: Hearts usually give 120 instead of 100
per_execution:
  hearts: 120 # Update this
```

This affects:

- Estimated executions
- Progress calculations
- Goal Mode planning

---

## Tips & Best Practices

### 1. Monitor Regularly

```
✅ Check statistics after every 5-10 executions
✅ Compare actual vs estimated progress
✅ Watch for declining success rate
```

### 2. Set Realistic Targets

```yaml
# Good targets (achievable)
service_targets:
  hearts: 10000      # ~100 executions
  views: 50000       # ~50 executions
  shares: 2000       # ~40 executions

# Too aggressive (may take very long)
service_targets:
  hearts: 1000000    # ~10,000 executions (unrealistic)
```

### 3. Track Success Rate

```
If success rate drops below 80%:
1. Check OCR settings
2. Enable DEBUG mode
3. Review screenshots
4. Consider AGGRESSIVE mode
```

### 4. Use Goal Mode Effectively

```
✅ Do:
- Set realistic targets
- Run daily sessions
- Check progress regularly
- Adjust per_execution if needed

❌ Don't:
- Set impossible targets
- Run 24/7 without monitoring
- Ignore declining success rate
```

### 5. Backup Progress File

```bash
# Backup before major changes
cp target_progress.json target_progress.backup.json

# Restore if needed
cp target_progress.backup.json target_progress.json
```

---

## Interpreting Statistics

### Scenario 1: High Success, Slow Progress

```
Stats:
- Success Rate: 95%
- Tasks Completed: 20
- Current Progress: 500 (expected: 2000)

Diagnosis:
- OCR working well
- But actual per_execution is lower than config

Solution:
- Check actual results from TikTok
- Update per_execution in config
- Continue with realistic expectations
```

### Scenario 2: Low Success Rate

```
Stats:
- Success Rate: 60%
- Captchas Solved: 5/15
- Tasks Failed: 6

Diagnosis:
- OCR struggling with captchas

Solution:
1. Enable DEBUG mode
2. Check preprocessing quality
3. Try AGGRESSIVE mode
4. Enable manual_input as fallback
```

### Scenario 3: Zero Progress Despite Success

```
Stats:
- Tasks Completed: 10
- Current Progress: 0
- No errors shown

Diagnosis:
- Executions complete but Zefoy didn't deliver
- Service might be offline
- Network issues

Solution:
- Check service status on Zefoy
- Verify TikTok video still exists
- Check internet connection
- Wait and retry later
```

---

## Advanced Features

### Custom Progress Tracking

Edit `target_progress.json` manually:

```json
{
  "services": {
    "Hearts": {
      "target": 10000,
      "current": 5000, // ← Set starting point
      "executions": 50, // ← Adjust count
      "per_execution": 100
    }
  }
}
```

**Use cases:**

- Starting mid-campaign
- Manual service executions
- Corrections for errors

### Export Statistics

```bash
# View current stats
cat target_progress.json

# Export to CSV (manual)
# Service,Current,Target,Progress,Executions
echo "Hearts,2500,10000,25%,25" > stats.csv
echo "Views,15000,50000,30%,15" >> stats.csv
```

### Statistics in Logs

Check logs for detailed stats:

```bash
tail -f logs/zefoy_bot_*.log | grep -i "statistics\|progress"
```

---

## Troubleshooting Statistics

### Statistics Not Updating

**Check:**

1. File exists: `ls target_progress.json`
2. File permissions: `chmod 644 target_progress.json`
3. Valid JSON: `python -m json.tool target_progress.json`
4. Bot has write access

**Solution:**

```bash
# Fix permissions
chmod 644 target_progress.json

# Reset if corrupted
mv target_progress.json target_progress.old
# Restart bot to create new file
```

### Incorrect Progress

**Possible causes:**

1. Wrong `per_execution` values
2. Manual edits with errors
3. Service giving variable results

**Solution:**

```bash
# Reset specific service
python3 << EOF
import json
with open('target_progress.json', 'r') as f:
    data = json.load(f)
data['services']['Hearts']['current'] = 0
data['services']['Hearts']['executions'] = 0
with open('target_progress.json', 'w') as f:
    json.dump(data, f, indent=2)
EOF
```

### Missing Statistics File

**If deleted or lost:**

Bot will create new file on next run:

```json
{
  "last_updated": "2025-10-23...",
  "services": {
    "Hearts": {
      "target": 10000,
      "per_execution": 100,
      "current": 0,
      "executions": 0
    }
  }
}
```

---

## Summary

**Key Points:**

- ✅ Two types of statistics: Session (live) and Progress (persistent)
- ✅ Uptime now shows user-friendly format
- ✅ Statistics accessible from main menu anytime
- ✅ Progress tracked in `target_progress.json`
- ✅ Automatic updates after each execution
- ✅ Visual progress bars and percentages
- ✅ Detailed metrics for analysis

**Best Practices:**

- Monitor statistics regularly
- Set realistic targets
- Track success rate trends
- Adjust per_execution based on actual results
- Backup progress file before major changes

---

**Related Documentation:**

- [USAGE_GUIDE.md](USAGE_GUIDE.md) - How to use features
- [README.md](../README.md) - Main documentation
- [CHANGELOG.md](CHANGELOG.md) - Recent updates

---

**Happy Tracking! 📊**
