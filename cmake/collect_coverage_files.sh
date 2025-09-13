#!/bin/bash
# Script to collect coverage files for incremental coverage

BUILD_DIR="$1"
INCREMENTAL_DIR="$2"

if [ -z "$BUILD_DIR" ] || [ -z "$INCREMENTAL_DIR" ]; then
    echo "Usage: $0 <build_dir> <incremental_dir>"
    exit 1
fi

echo "Collecting coverage files from $BUILD_DIR to $INCREMENTAL_DIR"

# Create incremental directory if it doesn't exist
mkdir -p "$INCREMENTAL_DIR"

# Count files before collection
profraw_count=0
gcda_count=0

# Collect .profraw files (Clang)
if find "$BUILD_DIR" -name "*.profraw" -not -path "*/incremental/*" -type f | head -1 | grep -q .; then
    find "$BUILD_DIR" -name "*.profraw" -not -path "*/incremental/*" -type f -exec cp {} "$INCREMENTAL_DIR/" \;
    profraw_count=$(find "$INCREMENTAL_DIR" -name "*.profraw" | wc -l)
    echo "Copied $profraw_count .profraw files"
else
    echo "No .profraw files found"
fi

# Collect .gcda files (GCC)
if find "$BUILD_DIR" -name "*.gcda" -not -path "*/incremental/*" -type f | head -1 | grep -q .; then
    find "$BUILD_DIR" -name "*.gcda" -not -path "*/incremental/*" -type f -exec cp {} "$INCREMENTAL_DIR/" \;
    gcda_count=$(find "$INCREMENTAL_DIR" -name "*.gcda" | wc -l)
    echo "Copied $gcda_count .gcda files"
else
    echo "No .gcda files found"
fi

# Collect .gcno files (GCC)
if find "$BUILD_DIR" -name "*.gcno" -not -path "*/incremental/*" -type f | head -1 | grep -q .; then
    find "$BUILD_DIR" -name "*.gcno" -not -path "*/incremental/*" -type f -exec cp {} "$INCREMENTAL_DIR/" \;
    gcno_count=$(find "$INCREMENTAL_DIR" -name "*.gcno" | wc -l)
    echo "Copied $gcno_count .gcno files"
else
    echo "No .gcno files found"
fi

total_files=$((profraw_count + gcda_count))
echo "Total coverage files collected: $total_files"

exit 0
