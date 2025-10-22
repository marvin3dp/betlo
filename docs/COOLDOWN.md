# Cooldown Improvements - October 22, 2025

## Overview

Ditambahkan **fallback cooldown** untuk memastikan SEMUA servis dan mode
menggunakan cooldown time dengan benar, kecuali saat pertama kali mengirimkan
search atau pertama kali start.

## Masalah yang Ditemukan

### ⚠️ Masalah Utama

Sebelumnya, jika `next_cooldown` tidak terdeteksi dari response Zefoy (karena
parsing error atau format response berubah), bot akan:

- **Continuous mode**: Hanya delay 1-2 detik sebelum execution berikutnya
- **Non-continuous mode**: Tidak ada cooldown sama sekali sebelum execution
  berikutnya

Ini berbahaya karena bisa membuat bot running terlalu cepat dan berpotensi
di-ban.

## Perbaikan yang Diterapkan

### 1. **Continuous Mode - Fallback Cooldown Sebelum Execution**

**File**: `zefoy_bot/bot.py` (Line ~502-508)

**Sebelum:**

```python
if pending_cooldown > 0:
    # Wait for cooldown...
else:
    random_delay(1, 2)  # ❌ HANYA 1-2 DETIK!
```

**Sesudah:**

```python
if pending_cooldown > 0:
    # Wait for cooldown...
else:
    # ✅ FALLBACK: 60 detik default
    default_cooldown = 60
    self.logger.warning(f"No cooldown detected. Using default: {default_cooldown}s")
    countdown_timer(default_cooldown, f"Default cooldown for {service_name}")
```

### 2. **Continuous Mode - Fallback Cooldown Setelah Success (3 tempat)**

#### A. Setelah `_wait_and_click_ready_button()` Success

**Line ~567-574**

```python
if successful_executions + 1 < target:
    if result.get('next_cooldown'):
        pending_cooldown = result['next_cooldown']
    else:
        # ✅ FALLBACK: 120 detik (2 menit)
        pending_cooldown = 120
        self.logger.warning("No cooldown detected. Using default: 120s")
```

#### B. Setelah First Execution Success

**Line ~687-694**

```python
if is_continuous_mode and successful_executions < target:
    if result.get('next_cooldown'):
        pending_cooldown = result['next_cooldown']
    else:
        # ✅ FALLBACK: 120 detik (2 menit)
        pending_cooldown = 120
        self.logger.warning("No cooldown detected. Using default: 120s")
```

#### C. Setelah Ready Button Success (dari initial cooldown)

**Line ~842-849**

```python
if is_continuous_mode and successful_executions < target:
    if ready_result.get('next_cooldown'):
        pending_cooldown = ready_result['next_cooldown']
    else:
        # ✅ FALLBACK: 120 detik (2 menit)
        pending_cooldown = 120
        self.logger.warning("No cooldown detected. Using default: 120s")
```

### 3. **Non-Continuous Mode - Fallback Cooldown (2 tempat)**

#### A. Setelah First Execution Success

**Line ~697-714**

```python
if not is_continuous_mode and auto_retry and successful_executions < target:
    if result.get('next_cooldown'):
        wait_seconds = result['next_cooldown']
    else:
        # ✅ FALLBACK: 120 detik (2 menit)
        wait_seconds = 120
        self.logger.warning("No cooldown detected. Using default: 120s")

    # Wait immediately...
    countdown_timer(wait_seconds, f"Cooldown for next {service_name}")
```

#### B. Setelah Ready Button Success

**Line ~857-868**

```python
if not is_continuous_mode and auto_retry and successful_executions < target:
    if ready_result.get('next_cooldown'):
        wait_seconds = ready_result['next_cooldown']
    else:
        # ✅ FALLBACK: 120 detik (2 menit)
        wait_seconds = 120
        self.logger.warning("No cooldown detected. Using default: 120s")

    # Wait immediately...
    countdown_timer(wait_seconds, f"Cooldown for next {service_name}")
```

## Flow Lengkap Cooldown Handling

### ✅ First Execution (successful_executions = 0)

```
1. ❌ TIDAK ada cooldown check sebelum execute (BENAR - ini first time!)
2. Submit URL dan execute service
3. ✅ Extract next_cooldown dari response
4. ✅ Jika tidak terdeteksi → gunakan default 120s
5. ✅ Continuous mode: set pending_cooldown untuk next execution
   ✅ Non-continuous mode: wait immediately
```

### ✅ Subsequent Executions (successful_executions > 0)

#### Continuous Mode:

```
1. ✅ Check pending_cooldown dari previous execution
   - Jika ada: Wait cooldown
   - Jika TIDAK ada: Wait default 60s (FALLBACK BARU!)
2. Execute service dengan search->send flow
3. ✅ Extract next_cooldown dari response
4. ✅ Jika tidak terdeteksi → set default 120s
5. ✅ Set pending_cooldown untuk next execution
6. Loop ke step 1
```

#### Non-Continuous Mode:

```
1. Execute service
2. ✅ Extract next_cooldown dari response
3. ✅ Jika tidak terdeteksi → gunakan default 120s
4. ✅ Wait immediately sebelum next execution
5. Loop ke step 1
```

## Default Cooldown Values

| Skenario                                  | Default Cooldown    | Keterangan                          |
| ----------------------------------------- | ------------------- | ----------------------------------- |
| **Continuous mode - sebelum execution**   | 60 detik            | Jika pending_cooldown = 0           |
| **Setelah success - continuous mode**     | 120 detik (2 menit) | Jika next_cooldown tidak terdeteksi |
| **Setelah success - non-continuous mode** | 120 detik (2 menit) | Jika next_cooldown tidak terdeteksi |

## Exceptions (TIDAK Perlu Cooldown)

### ✅ BENAR - Tidak Perlu Cooldown:

1. **First execution** (`successful_executions = 0`) - Pertama kali start
   service
2. **First search submission** - Pertama kali submit URL ke service
3. **Eksekusi terakhir** - Tidak ada execution berikutnya

### ❌ SALAH - HARUS Ada Cooldown:

1. **Semua execution ke-2 dan seterusnya** - WAJIB wait cooldown
2. **Setelah success** - WAJIB ada cooldown sebelum next execution
3. **Continuous mode loop** - WAJIB wait pending_cooldown atau default

## Benefits

1. **✅ Keamanan**: Bot tidak akan running terlalu cepat meskipun cooldown
   parsing gagal
2. **✅ Reliability**: Selalu ada fallback cooldown untuk mencegah spam
3. **✅ Logging**: Warning jelas saat menggunakan default cooldown
4. **✅ Fleksibel**: Tetap prioritaskan cooldown dari Zefoy jika terdeteksi
5. **✅ Konsisten**: Semua mode (Goals, Target Amount, Manual >1x, Manual 1x)
   menggunakan cooldown

## Testing Recommendations

### Test Case 1: Normal Flow (Cooldown Terdeteksi)

- Run dengan Goals Mode atau Manual >1x
- Pastikan cooldown dari Zefoy terdeteksi dan digunakan
- Tidak ada warning "No cooldown detected"

### Test Case 2: Fallback Flow (Cooldown Tidak Terdeteksi)

- Jika ada perubahan format response Zefoy
- Pastikan default cooldown (60s atau 120s) digunakan
- Harus ada warning log: "No cooldown detected. Using default: XXs"

### Test Case 3: First Execution

- First execution TIDAK boleh ada cooldown sebelum execute
- Harus langsung submit dan execute

### Test Case 4: Non-Continuous Mode

- Manual 1x execution
- Setelah success, harus wait cooldown (dari response atau default 120s)

## Summary

**Total Perbaikan**: 6 tempat ditambahkan fallback cooldown

- 1x Continuous mode - sebelum execution
- 3x Continuous mode - setelah success
- 2x Non-continuous mode - setelah success

**Semua servis dan mode sekarang DIJAMIN menggunakan cooldown**, dengan fallback
yang aman jika parsing cooldown gagal.

**Exception tetap dijaga**: First execution dan first search TIDAK perlu
cooldown (sesuai requirement).
