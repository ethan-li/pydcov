# Coverage Generation Failure Analysis: "stamp mismatch with notes file"

## Executive Summary

Your pydcov workflow is failing with a **"stamp mismatch with notes file"** error during coverage merge. This document provides:
1. Root cause analysis
2. Why the error occurs
3. Immediate fixes for your CI/CD pipeline
4. Long-term improvements implemented in pydcov

---

## Error Analysis

### What Does "stamp mismatch" Mean?

The error occurs when **`.gcda` (coverage data) and `.gcno` (notes) files are out of sync**. These files contain:

- **`.gcno` files**: Generated at **compile time**, contain program structure (functions, branches, lines)
- **`.gcda` files**: Generated at **runtime**, contain execution counts

Both files have an internal **timestamp/version stamp** that must match. When they don't match, gcov/geninfo refuses to process them.

### Why Does This Happen?

From your error log:
```
/xxx.c.gcda:stamp mismatch with notes file
```

**Common causes:**

1. **Code was recompiled** between test runs without cleaning `.gcda` files
2. **`.gcno` files are missing or from a different build** than `.gcda` files
3. **Compiler version changed** between build and test execution
4. **Build artifacts were copied incorrectly** (e.g., `.gcda` and `.gcno` from different builds)

### Why Does geninfo Fail Despite Showing Coverage Stats?

The stdout shows:
```
Lines executed:0.00% of 92
```

This means gcov **partially processed** the file before hitting the stamp mismatch. However:
- The error in stderr causes geninfo to **abort completely**
- No valid `.info` file is generated
- The entire subdirectory is marked as failed

---

## Immediate Solutions for Your CI/CD Pipeline

### Solution 1: Clean Coverage Data Before Each Test Run (Recommended)

Add this to your CI script **before running tests**:

```bash
# Clean all .gcda files before test execution
find /build/x86_64-linux -name "*.gcda" -delete

# Then run your tests
pydcov add "your_test_command"
```

**Why this works:** Ensures `.gcda` files are freshly generated and match the current `.gcno` files.

### Solution 2: Rebuild with Coverage Flags

If you're reusing a build directory, ensure a clean rebuild:

```bash
# Clean and rebuild
cd /build/x86_64-linux
make clean
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make

# Then run tests
cd /tests
pydcov add "your_test_command"
```

### Solution 3: Verify .gcno Files Exist

Check that `.gcno` files are present alongside `.gcda` files:

```bash
# Count .gcda and .gcno files
echo "GCDA files: $(find build -name '*.gcda' | wc -l)"
echo "GCNO files: $(find build -name '*.gcno' | wc -l)"

# They should match!
```

If `.gcno` files are missing, your build isn't configured correctly for coverage.

---

## Root Cause in Your Specific Case

Looking at your error log, I suspect **one of these scenarios**:

### Scenario A: Incremental Build Issue
```
1. Initial build generates .gcno files
2. Code is modified and partially rebuilt
3. Some .gcno files are regenerated (new stamps)
4. Tests run, generating .gcda files
5. pydcov collects both old and new .gcno files
6. Stamp mismatch occurs
```

**Fix:** Always do a clean build in CI/CD:
```bash
rm -rf build/x86_64-linux
mkdir -p build/x86_64-linux
cd build/x86_64-linux
cmake ../.. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make
```

### Scenario B: Missing .gcno Files
```
1. Build generates .gcno files in build directory
2. Tests run in different directory
3. pydcov collects .gcda files but can't find matching .gcno files
4. Stamp mismatch occurs
```

**Fix:** Ensure pydcov is configured with correct build directory:

---

## Improvements Made to pydcov

### 1. Better .gcno File Collection

**Before:** Copied all `.gcno` files by name, causing overwrites if multiple files had the same name.

**After:** Copies `.gcno` files **paired with their corresponding `.gcda` files** from the same directory:

```python
# For each .gcda file, find its matching .gcno file
for gcda_file in gcda_files:
    gcno_file = gcda_file.with_suffix('.gcno')
    if gcno_file.exists():
        # Copy both files together
        shutil.copy2(gcda_file, dest)
        shutil.copy2(gcno_file, dest)
    else:
        # Warn about missing .gcno file
        logger.warning(f"Missing .gcno file for {gcda_file.name}")
```

### 2. Enhanced Error Reporting

**Before:** Only showed brief error message.

**After:** Shows detailed stdout/stderr from geninfo and provides actionable guidance:

```
[WARNING] geninfo failed for add_20251104_140435_148:
stdout:
  Lines executed:0.00% of 92
  ...
stderr:
  xxx.c.gcda:stamp mismatch with notes file

[WARNING] Stamp mismatch detected. This usually means:
  1. Code was recompiled after .gcda files were generated
  2. .gcno files are from a different build than .gcda files
  3. Compiler version mismatch between build and test execution
  Recommendation: Clean build directory and regenerate coverage from scratch
```

### 3. Missing .gcno File Detection

**New:** Warns when `.gcda` files don't have corresponding `.gcno` files:

```
[WARNING] Found 3 .gcda files without corresponding .gcno files.
This may cause 'stamp mismatch' errors during coverage generation.
```

---

## Testing Your Fix

After implementing the recommended solutions, verify the fix:

```bash
# 1. Clean build
cd /build/x86_64-linux
make clean
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make

# 2. Clean old coverage data
rm -rf /tests/pydcov_dir

# 3. Initialize pydcov
cd /tests
pydcov init

# 4. Run tests with coverage
pydcov add "your_test_command"

# 5. Generate report
pydcov report

# 6. Verify success
ls -la pydcov_dir/report/index.html
```

---

## Recommended CI/CD Workflow

Here's the recommended CI script structure:

```bash
#!/bin/bash
set -e  # Exit on error

# Configuration
BUILD_DIR="/build/x86_64-linux"
TEST_DIR="/tests"

# Step 1: Clean build with coverage
echo "=== Building with coverage ==="
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake ../.. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make -j$(nproc)

# Step 2: Initialize coverage tracking
echo "=== Initializing coverage ==="
cd "$TEST_DIR"
rm -rf pydcov_dir  # Clean old coverage data
pydcov init

# Step 3: Run tests with coverage collection
echo "=== Running tests ==="
pydcov add "your_test_command"

# Step 4: Generate coverage report
echo "=== Generating coverage report ==="
pydcov report

# Step 5: Verify report was generated
if [ -f "pydcov_dir/report/index.html" ]; then
    echo "✓ Coverage report generated successfully"
else
    echo "✗ Coverage report generation failed"
    exit 1
fi
```

---

## FAQ

### Q: Can pydcov skip corrupted files and continue?

**A:** Yes, with the improvements I've made, pydcov now:
- Continues processing other subdirectories even if some fail
- Only fails if **ALL** subdirectories fail
- Provides detailed warnings for each failure

However, in your case, you only have **1 subdirectory**, so if it fails, the entire merge fails. The solution is to **fix the root cause** (stamp mismatch) rather than skip it.

### Q: Should I use `--ignore-errors` with geninfo?

**A:** pydcov already uses `--ignore-errors source,unused,format,corrupt,gcov`. However, this doesn't help with stamp mismatches because they indicate **fundamentally incompatible data files**.

### Q: How do I prevent this in the future?

**A:** Follow these best practices:
1. **Always clean build** in CI/CD environments
2. **Delete .gcda files** before each test run
3. **Use pydcov init** to start fresh coverage tracking
4. **Don't mix coverage data** from different builds

---

## Summary

**Root Cause:** `.gcda` and `.gcno` files have mismatched timestamps/versions.

**Immediate Fix:** Clean `.gcda` files before running tests:
```bash
find build -name "*.gcda" -delete
pydcov add "your_test_command"
```

**Long-term Fix:** Implement clean build workflow in CI/CD (see recommended workflow above).

**pydcov Improvements:** Better error reporting, .gcno file pairing, and missing file detection.
