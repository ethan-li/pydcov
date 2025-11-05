# PyDCov Coverage Error Troubleshooting Guide

Quick reference for diagnosing and fixing common coverage generation errors.

---

## Error: "stamp mismatch with notes file"

### Symptoms
```
geninfo: WARNING: ('gcov') GCOV failed for /path/to/file.gcda!
geninfo: ERROR: expected TraceFile
stderr: file.gcda:stamp mismatch with notes file
```

### Diagnosis
```bash
# Check if .gcno files exist
find build -name "*.gcno" | wc -l
find build -name "*.gcda" | wc -l
# These counts should match!

# Check file timestamps
ls -la build/**/*.gcda
ls -la build/**/*.gcno
# .gcno files should be older (from compile time)
# .gcda files should be newer (from test execution)
```

### Quick Fix
```bash
# Option 1: Delete .gcda files and re-run tests
find build -name "*.gcda" -delete
pydcov add "your_test_command"

# Option 2: Clean rebuild
make clean
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make
pydcov init
pydcov add "your_test_command"
```

### Root Causes
1. ✗ Code recompiled after .gcda files generated
2. ✗ .gcno files from different build than .gcda files
3. ✗ Compiler version mismatch
4. ✗ Incremental build with partial recompilation

### Prevention
- Always use clean builds in CI/CD
- Delete .gcda files before each test run
- Don't mix coverage data from different builds

---

## Error: "All subdirectories failed to generate coverage data"

### Symptoms
```
[ERROR] All subdirectories failed to generate coverage data
[ERROR] Check the warnings above for details on individual subdirectory failures
```

### Diagnosis
```bash
# Check pydcov directory structure
ls -la pydcov_dir/
ls -la pydcov_dir/add_*/

# Verify .gcda and .gcno files were collected
find pydcov_dir -name "*.gcda"
find pydcov_dir -name "*.gcno"

# Check for detailed error messages in logs
pydcov merge --verbose
```

### Quick Fix
```bash
# Clean and restart coverage collection
rm -rf pydcov_dir
pydcov init
pydcov add "your_test_command"
pydcov report
```

### Root Causes
1. ✗ Stamp mismatch (see above)
2. ✗ Missing .gcno files
3. ✗ Corrupted coverage files
4. ✗ No coverage data collected (tests didn't run)

---

## Error: "No .gcda files found"

### Symptoms
```
[WARNING] No .gcda files found in pydcov directory
[ERROR] Coverage data merge failed
```

### Diagnosis
```bash
# Check if tests actually ran
echo $?  # Should be 0 if tests passed

# Check if coverage instrumentation is enabled
grep -r "PYDCOV_COVERAGE_ENABLED" build/CMakeCache.txt

# Check if .gcda files exist in build directory
find build -name "*.gcda"
```

### Quick Fix
```bash
# Ensure coverage is enabled in CMake
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make clean && make

# Run tests to generate .gcda files
pydcov add "your_test_command"
```

### Root Causes
1. ✗ Coverage not enabled in build (`-DPYDCOV_COVERAGE_ENABLED=ON` missing)
2. ✗ Tests didn't execute (failed before running)
3. ✗ Wrong build directory specified
4. ✗ Tests ran but didn't execute any instrumented code

---

## Error: "Missing .gcno file for X.gcda"

### Symptoms
```
[WARNING] Found N .gcda files without corresponding .gcno files.
This may cause 'stamp mismatch' errors during coverage generation.
```

### Diagnosis
```bash
# Find .gcda files without matching .gcno files
for gcda in $(find build -name "*.gcda"); do
    gcno="${gcda%.gcda}.gcno"
    if [ ! -f "$gcno" ]; then
        echo "Missing: $gcno"
    fi
done
```

### Quick Fix
```bash
# Rebuild to regenerate .gcno files
make clean
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make

# Then re-run tests
rm -rf pydcov_dir
pydcov init
pydcov add "your_test_command"
```

### Root Causes
1. ✗ Partial build (some files not compiled with coverage)
2. ✗ .gcno files deleted or not copied correctly
3. ✗ Build configuration changed mid-build
4. ✗ Different build directories for compile and test

---

## Error: "geninfo failed" (generic)

### Symptoms
```
[WARNING] geninfo failed for add_YYYYMMDD_HHMMSS_XXX: <error details>
```

### Diagnosis
```bash
# Run geninfo manually to see full error
cd pydcov_dir/add_YYYYMMDD_HHMMSS_XXX
geninfo . --output-filename test.info --rc branch_coverage=1 --rc function_coverage=1

# Check geninfo version
geninfo --version

# Check lcov version
lcov --version
```

### Quick Fix
```bash
# Update lcov/geninfo if outdated
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install --upgrade lcov

# macOS:
brew upgrade lcov

# Then retry
pydcov merge
```

### Root Causes
1. ✗ Outdated lcov/geninfo version
2. ✗ Corrupted coverage files
3. ✗ Incompatible gcov version
4. ✗ Source files moved or deleted

---

## Error: "Merged coverage data not found"

### Symptoms
```
[INFO] Merged coverage data not found, merging automatically...
```

### Diagnosis
```bash
# Check if merged.info exists
ls -la pydcov_dir/merged.info

# Check if add subdirectories exist
ls -la pydcov_dir/add_*/
```

### Quick Fix
```bash
# This is usually not an error - pydcov will merge automatically
# If merge fails, check the subsequent error messages

# Manual merge:
pydcov merge
```

### Root Causes
1. ℹ️ Normal behavior - merged.info not yet generated
2. ✗ Previous merge failed (check logs)
3. ✗ No add subdirectories (no coverage collected)

---

## Error: "lcov not found" or "gcov not found"

### Symptoms
```
[ERROR] lcov not found
[ERROR] gcov not found
```

### Diagnosis
```bash
# Check if tools are installed
which lcov
which gcov
which geninfo
which genhtml

# Check PATH
echo $PATH
```

### Quick Fix
```bash
# Install lcov (includes geninfo, genhtml)
# Ubuntu/Debian:
sudo apt-get install lcov

# macOS:
brew install lcov

# RHEL/CentOS:
sudo yum install lcov

# Verify installation
lcov --version
gcov --version
```

---

## Debugging Checklist

When coverage generation fails, check these in order:

### 1. Build Configuration
- [ ] Coverage enabled: `grep PYDCOV_COVERAGE_ENABLED build/CMakeCache.txt`
- [ ] Debug build: `grep CMAKE_BUILD_TYPE build/CMakeCache.txt`
- [ ] Clean build: `make clean && make`

### 2. Coverage Files
- [ ] .gcno files exist: `find build -name "*.gcno" | wc -l`
- [ ] .gcda files exist: `find build -name "*.gcda" | wc -l`
- [ ] Counts match: `.gcno count == .gcda count`
- [ ] Files collected: `ls pydcov_dir/add_*/`

### 3. Tools
- [ ] lcov installed: `which lcov`
- [ ] gcov installed: `which gcov`
- [ ] geninfo installed: `which geninfo`
- [ ] Versions compatible: `lcov --version`

### 4. Configuration
- [ ] .pydcov.json exists: `cat .pydcov.json`
- [ ] build_root correct: Check path in config
- [ ] pydcov_dir correct: Check path in config

### 5. Logs
- [ ] Check DEBUG logs: `pydcov merge --verbose`
- [ ] Check geninfo output: Look for detailed errors
- [ ] Check test execution: Verify tests actually ran

---

## Common Patterns

### Pattern 1: CI/CD Stamp Mismatch
**Scenario:** Works locally, fails in CI/CD

**Cause:** CI/CD reuses build artifacts from previous runs

**Fix:**
```bash
# Add to CI/CD script
rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
make
```

### Pattern 2: Incremental Build Issues
**Scenario:** First run works, subsequent runs fail

**Cause:** .gcda files persist across builds

**Fix:**
```bash
# Before each test run
find build -name "*.gcda" -delete
pydcov add "your_test_command"
```

### Pattern 3: Multiple Build Configurations
**Scenario:** Coverage works for Debug, fails for Release

**Cause:** Coverage only works with Debug builds

**Fix:**
```bash
# Always use Debug for coverage
cmake .. -DCMAKE_BUILD_TYPE=Debug -DPYDCOV_COVERAGE_ENABLED=ON
```

---

## Getting Help

If you're still stuck after trying these solutions:

1. **Enable verbose logging:**
   ```bash
   pydcov merge --verbose
   pydcov report --verbose
   ```

2. **Collect diagnostic information:**
   ```bash
   # System info
   uname -a
   gcc --version
   lcov --version
   
   # Build info
   cat build/CMakeCache.txt | grep -E "(CMAKE_BUILD_TYPE|PYDCOV|COVERAGE)"
   
   # Coverage files
   find build -name "*.gcda" -o -name "*.gcno" | head -20
   find pydcov_dir -type f | head -20
   
   # Config
   cat .pydcov.json
   ```

3. **Check the detailed analysis:**
   See `COVERAGE_STAMP_MISMATCH_ANALYSIS.md` for in-depth explanation

4. **File an issue:**
   Include the diagnostic information above when reporting issues

