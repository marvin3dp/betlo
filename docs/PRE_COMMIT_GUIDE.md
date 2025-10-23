# Pre-commit Guide - Optimized for Speed ⚡

This project uses an optimized pre-commit configuration that prioritizes speed
for frequent commits.

---

## 🚀 Quick Start

### Normal Commits (FAST - ~2 seconds)

```bash
git add .
git commit -m "your message"
```

**What runs automatically:**

- ✅ Trailing whitespace removal
- ✅ End-of-file fixes
- ✅ YAML/JSON validation
- ✅ Large file detection
- ✅ Merge conflict detection
- ✅ Line ending normalization
- ✅ Black (Python formatter) - only on `betlo/*.py`
- ✅ isort (import sorter) - only on `betlo/*.py`

**Total time:** ~2-5 seconds ⚡

---

## 🐌 Manual Checks (SLOW - ~2-5 minutes)

Run these manually before pushing or for final cleanup:

```bash
# Run ALL checks including slow ones
source venv/bin/activate
pre-commit run --hook-stage manual --all-files
```

**What runs manually:**

- 📝 Flake8 (Python linter)
- 📄 YAML formatter (requires Node.js)
- 📋 Markdown linter (requires Node.js)
- 🐚 Shell script formatter (requires Go)

**Why manual?** These checks require installing heavy environments (Node.js, Go)
which take 2-5 minutes on first run.

---

## 📖 Common Commands

### Regular commit (fast)

```bash
git add .
git commit -m "fix: update feature"
```

### Run all checks manually

```bash
source venv/bin/activate
pre-commit run --hook-stage manual --all-files
```

### Run specific hook

```bash
source venv/bin/activate
pre-commit run black --all-files          # Format Python files
pre-commit run markdownlint --all-files   # Check Markdown
pre-commit run shfmt --all-files          # Format shell scripts
```

### Skip pre-commit (emergency only)

```bash
git commit -m "emergency fix" --no-verify
```

### Update hooks to latest versions

```bash
source venv/bin/activate
pre-commit autoupdate
```

---

## 🎯 Optimization Details

### Fast Hooks (Run on Every Commit)

**Why fast?**

- Python-based (already in venv)
- Minimal dependencies
- Run only on changed files
- Limited to `betlo/*.py` for formatters

### Slow Hooks (Manual Only)

**Why slow?**

- **markdownlint**: Requires Node.js environment (~2-3 min install)
- **YAML formatter**: Requires Node.js environment (~2-3 min install)
- **shfmt**: Requires Go environment (~1-2 min install)
- **flake8**: Thorough but slow linting

These environments are installed once and cached, but first-time setup is slow.

---

## 🔧 Configuration File

Location: `.pre-commit-config.yaml`

### Structure:

```yaml
repos:
  # FAST HOOKS (auto-run on commit)
  - pre-commit-hooks (Python-based)
  - black (Python formatter)
  - isort (import sorter)

  # SLOW HOOKS (manual only - stages: [manual])
  - flake8 (linter)
  - pretty-format-yaml
  - markdownlint
  - shfmt
```

---

## 🛠️ Troubleshooting

### Problem: Pre-commit is slow

**Solution:** Check if you're running slow hooks by accident

```bash
# Should be FAST
git commit -m "test"

# Should be SLOW (only run when needed)
pre-commit run --hook-stage manual --all-files
```

### Problem: Hooks not running

**Solution:** Reinstall hooks

```bash
source venv/bin/activate
pre-commit uninstall
pre-commit install
```

### Problem: "command not found: pre-commit"

**Solution:** Activate virtual environment

```bash
source venv/bin/activate
# OR
source activate.sh
```

### Problem: Hook failed, need to commit anyway

**Solution:** Use `--no-verify` (emergency only)

```bash
git commit -m "emergency fix" --no-verify
```

---

## 📊 Performance Comparison

| Configuration         | Commit Time | First Run | Use Case            |
| --------------------- | ----------- | --------- | ------------------- |
| **Old (all hooks)**   | 2-5 minutes | 5-10 min  | Too slow            |
| **New (fast only)**   | 2-5 seconds | 10-30 sec | ✅ Daily commits    |
| **New (with manual)** | 2-5 minutes | 5-10 min  | Before push/release |

---

## 💡 Best Practices

### For Daily Development:

```bash
# Fast commits (auto-run fast hooks)
git add .
git commit -m "feat: add new feature"
git push
```

### Before Pushing to Main/Release:

```bash
# Run all checks including slow ones
source venv/bin/activate
pre-commit run --hook-stage manual --all-files

# Then commit and push
git add .
git commit -m "release: v2.3.0"
git push
```

### For CI/CD Pipeline:

```bash
# Run ALL checks (fast + manual)
pre-commit run --all-files
pre-commit run --hook-stage manual --all-files
```

---

## 🎓 Learn More

- [Pre-commit Official Docs](https://pre-commit.com/)
- [Hook Stages](https://pre-commit.com/#confining-hooks-to-run-at-certain-stages)
- [Available Hooks](https://pre-commit.com/hooks.html)

---

## 📝 Summary

**TL;DR:**

- ✅ **Fast commits** (~2-5 sec): Essential checks only
- 🐌 **Manual checks** (~2-5 min): Run before push with `--hook-stage manual`
- 🎯 **Best of both worlds**: Speed for daily work, thoroughness when needed

**Before (all hooks on commit):**

```
git commit → Wait 2-5 minutes → Frustrated 😤
```

**After (optimized):**

```
git commit → Wait 2-5 seconds → Happy 😊
Run manual checks before push → Thorough ✅
```
