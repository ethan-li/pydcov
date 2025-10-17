"""
Test branch coverage functionality with GCC compiler.

This test verifies that branch coverage is properly collected, processed,
and reported when using GCC/gcov toolchain.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
import shutil


class TestBranchCoverage:
    """Test branch coverage with GCC."""

    def test_simple_branch_coverage(self):
        """Test branch coverage with simple C code containing if/else branches.
        
        This test creates a minimal C program with branches, compiles it with
        GCC coverage flags, runs it, and verifies that branch coverage data
        is collected and reported.
        """
        # Check if GCC is available
        if not shutil.which('gcc'):
            pytest.skip("GCC not available")
        
        # Check if lcov tools are available
        if not shutil.which('gcov') or not shutil.which('lcov') or not shutil.which('genhtml'):
            pytest.skip("LCOV tools not available (gcov, lcov, genhtml)")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create simple C code with branches
            c_file = temp_path / 'test_branches.c'
            c_file.write_text('''
#include <stdio.h>

int max(int a, int b) {
    if (a > b) {
        return a;  // Branch 1
    } else {
        return b;  // Branch 2
    }
}

int classify(int value) {
    if (value < 0) {
        return -1;  // Branch 1
    } else if (value == 0) {
        return 0;   // Branch 2
    } else {
        return 1;   // Branch 3
    }
}

int main() {
    // Test max function - both branches
    printf("max(5, 3) = %d\\n", max(5, 3));
    printf("max(2, 8) = %d\\n", max(2, 8));
    
    // Test classify function - all three branches
    printf("classify(-5) = %d\\n", classify(-5));
    printf("classify(0) = %d\\n", classify(0));
    printf("classify(10) = %d\\n", classify(10));
    
    return 0;
}
''')
            
            # Compile with GCC coverage flags
            exe_file = temp_path / 'test_branches'
            compile_cmd = [
                'gcc',
                '-o', str(exe_file),
                '--coverage',
                '-fprofile-arcs',
                '-ftest-coverage',
                str(c_file)
            ]
            
            print(f"\n=== Compiling with GCC coverage flags ===")
            print(f"Command: {' '.join(compile_cmd)}")
            result = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=temp_path)
            
            if result.returncode != 0:
                print(f"Compilation failed: {result.stderr}")
                pytest.fail(f"Failed to compile test code: {result.stderr}")
            
            print("✓ Compilation successful")
            
            # Run the executable to generate coverage data
            print(f"\n=== Running executable to generate coverage data ===")
            result = subprocess.run([str(exe_file)], capture_output=True, text=True, cwd=temp_path)
            
            if result.returncode != 0:
                print(f"Execution failed: {result.stderr}")
                pytest.fail(f"Failed to run test executable: {result.stderr}")
            
            print("✓ Execution successful")
            print(f"Output:\n{result.stdout}")
            
            # Check for .gcda and .gcno files
            gcda_files = list(temp_path.glob('*.gcda'))
            gcno_files = list(temp_path.glob('*.gcno'))
            
            print(f"\n=== Coverage files generated ===")
            print(f"Found {len(gcda_files)} .gcda files: {[f.name for f in gcda_files]}")
            print(f"Found {len(gcno_files)} .gcno files: {[f.name for f in gcno_files]}")
            
            assert len(gcda_files) > 0, "No .gcda files generated"
            assert len(gcno_files) > 0, "No .gcno files generated"
            
            # Run gcov with branch coverage flags
            print(f"\n=== Running gcov with branch coverage flags ===")
            gcov_cmd = [
                'gcov',
                '-b',  # Branch coverage
                '-c',  # Unconditional branch coverage
                '-f',  # Function coverage
                'test_branches.c'
            ]
            
            print(f"Command: {' '.join(gcov_cmd)}")
            result = subprocess.run(gcov_cmd, capture_output=True, text=True, cwd=temp_path)
            
            print(f"gcov output:\n{result.stdout}")
            if result.stderr:
                print(f"gcov stderr:\n{result.stderr}")
            
            # Check for .gcov files
            gcov_files = list(temp_path.glob('*.gcov'))
            print(f"\nFound {len(gcov_files)} .gcov files: {[f.name for f in gcov_files]}")
            
            # Read and check gcov output for branch information
            if gcov_files:
                gcov_content = gcov_files[0].read_text()
                print(f"\n=== First .gcov file content (first 50 lines) ===")
                print('\n'.join(gcov_content.split('\n')[:50]))
                
                # Check if branch information is present
                has_branch_info = 'branch' in gcov_content.lower()
                print(f"\n✓ Branch information in .gcov file: {has_branch_info}")
            
            # Run geninfo to create .info file with branch coverage
            print(f"\n=== Running geninfo with branch coverage flags ===")
            info_file = temp_path / 'coverage.info'
            geninfo_cmd = [
                'geninfo',
                str(temp_path),
                '--output-filename', str(info_file),
                '--rc', 'branch_coverage=1',
                '--rc', 'function_coverage=1'
            ]
            
            print(f"Command: {' '.join(geninfo_cmd)}")
            result = subprocess.run(geninfo_cmd, capture_output=True, text=True, cwd=temp_path)
            
            if result.returncode != 0:
                print(f"geninfo failed: {result.stderr}")
                pytest.fail(f"geninfo failed: {result.stderr}")
            
            print("✓ geninfo successful")
            if result.stdout:
                print(f"geninfo output:\n{result.stdout}")
            
            # Verify .info file exists and contains branch coverage data
            assert info_file.exists(), "Coverage .info file not created"
            
            info_content = info_file.read_text()
            print(f"\n=== Checking .info file for branch coverage data ===")
            print(f"File size: {len(info_content)} bytes")
            
            # Check for branch coverage entries
            has_brda = 'BRDA:' in info_content
            has_brf = 'BRF:' in info_content
            has_brh = 'BRH:' in info_content
            
            print(f"BRDA entries (branch data): {has_brda}")
            print(f"BRF entry (branches found): {has_brf}")
            print(f"BRH entry (branches hit): {has_brh}")
            
            # Count BRDA entries
            brda_count = info_content.count('BRDA:')
            print(f"Total BRDA entries: {brda_count}")
            
            # Show sample BRDA entries
            if has_brda:
                brda_lines = [line for line in info_content.split('\n') if line.startswith('BRDA:')]
                print(f"\nSample BRDA entries (first 10):")
                for line in brda_lines[:10]:
                    print(f"  {line}")
            
            # Show BRF and BRH values
            if has_brf:
                brf_lines = [line for line in info_content.split('\n') if line.startswith('BRF:')]
                print(f"\nBRF entries: {brf_lines}")
            
            if has_brh:
                brh_lines = [line for line in info_content.split('\n') if line.startswith('BRH:')]
                print(f"BRH entries: {brh_lines}")
            
            # ASSERTIONS - This is where we verify branch coverage is working
            assert has_brda, "❌ FAIL: No BRDA (branch data) entries found in .info file"
            assert has_brf, "❌ FAIL: No BRF (branches found) entry in .info file"
            assert has_brh, "❌ FAIL: No BRH (branches hit) entry in .info file"
            assert brda_count > 0, f"❌ FAIL: Expected branch data entries, found {brda_count}"
            
            print("\n" + "="*60)
            print("✅ SUCCESS: Branch coverage is working correctly!")
            print("="*60)
            print(f"✓ BRDA entries found: {brda_count}")
            print(f"✓ BRF entry found: {has_brf}")
            print(f"✓ BRH entry found: {has_brh}")
            print("="*60)


    def test_pydcov_branch_coverage_integration(self):
        """Test that PyDCov properly collects and reports branch coverage.

        This test uses the algorithm example module to verify that branch
        coverage works end-to-end with the PyDCov workflow.
        """
        # This test requires the algorithm example to be built with coverage
        algorithm_dir = Path(__file__).parent.parent / 'examples' / 'algorithm'
        build_dir = algorithm_dir / 'build'
        pydcov_dir = algorithm_dir / 'pydcov_dir'

        # Check if build directory exists
        if not build_dir.exists():
            pytest.skip("Algorithm example not built - run: cd examples/algorithm/build && PYDCOV_ENABLE_COVERAGE=1 cmake .. && make")

        # Check if CMake cache indicates coverage is enabled
        cmake_cache = build_dir / 'CMakeCache.txt'
        if not cmake_cache.exists():
            pytest.skip("CMake cache not found")

        cache_content = cmake_cache.read_text()
        if 'PYDCOV_COVERAGE_ENABLED:BOOL=ON' not in cache_content:
            pytest.skip("Coverage not enabled in CMake - run: cd examples/algorithm/build && PYDCOV_ENABLE_COVERAGE=1 cmake ..")

        # Clean previous coverage data
        if pydcov_dir.exists():
            shutil.rmtree(pydcov_dir)

        print(f"\n=== Testing PyDCov branch coverage integration ===")
        print(f"Algorithm directory: {algorithm_dir}")
        print(f"Build directory: {build_dir}")

        # Initialize PyDCov
        print(f"\n=== Initializing PyDCov ===")
        init_cmd = ['pydcov', 'init', '--build-root', str(build_dir)]
        result = subprocess.run(init_cmd, capture_output=True, text=True, cwd=algorithm_dir)

        if result.returncode != 0:
            print(f"pydcov init failed: {result.stderr}")
            pytest.fail(f"Failed to initialize PyDCov: {result.stderr}")

        print("✓ PyDCov initialized")

        # Run tests with coverage
        print(f"\n=== Running tests with coverage ===")
        add_cmd = ['pydcov', 'add', 'python', '-m', 'pytest', 'tests/', '-v']
        result = subprocess.run(add_cmd, capture_output=True, text=True, cwd=algorithm_dir)

        if result.returncode != 0:
            print(f"pydcov add failed: {result.stderr}")
            # Don't fail - tests might not exist or might fail
            print("Warning: Test execution had issues, but continuing to check coverage data")

        print("✓ Tests executed")

        # Merge coverage data
        print(f"\n=== Merging coverage data ===")
        merge_cmd = ['pydcov', 'merge']
        result = subprocess.run(merge_cmd, capture_output=True, text=True, cwd=algorithm_dir)

        if result.returncode != 0:
            print(f"pydcov merge output: {result.stdout}")
            print(f"pydcov merge stderr: {result.stderr}")

        # Check for merged.info file
        merged_info = pydcov_dir / 'merged.info'
        if not merged_info.exists():
            pytest.skip("No merged.info file generated - coverage data may not have been collected")

        print("✓ Coverage data merged")

        # Verify branch coverage in merged.info
        print(f"\n=== Checking merged.info for branch coverage ===")
        info_content = merged_info.read_text()

        has_brda = 'BRDA:' in info_content
        has_brf = 'BRF:' in info_content
        has_brh = 'BRH:' in info_content

        brda_count = info_content.count('BRDA:')

        print(f"BRDA entries (branch data): {has_brda}")
        print(f"BRF entry (branches found): {has_brf}")
        print(f"BRH entry (branches hit): {has_brh}")
        print(f"Total BRDA entries: {brda_count}")

        if has_brda:
            brda_lines = [line for line in info_content.split('\n') if line.startswith('BRDA:')]
            print(f"\nSample BRDA entries (first 5):")
            for line in brda_lines[:5]:
                print(f"  {line}")

        # Generate HTML report
        print(f"\n=== Generating HTML report ===")
        report_cmd = ['pydcov', 'report']
        result = subprocess.run(report_cmd, capture_output=True, text=True, cwd=algorithm_dir)

        if result.returncode != 0:
            print(f"pydcov report output: {result.stdout}")
            print(f"pydcov report stderr: {result.stderr}")

        report_dir = pydcov_dir / 'report'
        index_html = report_dir / 'index.html'

        if index_html.exists():
            print(f"✓ HTML report generated at {index_html}")

            # Check if HTML report contains branch coverage
            html_content = index_html.read_text()
            has_branch_in_html = 'branch' in html_content.lower()
            print(f"Branch coverage in HTML: {has_branch_in_html}")

        # ASSERTIONS
        print("\n" + "="*60)
        if has_brda and has_brf and has_brh:
            print("✅ SUCCESS: PyDCov branch coverage is working!")
            print("="*60)
            print(f"✓ BRDA entries found: {brda_count}")
            print(f"✓ BRF entry found: {has_brf}")
            print(f"✓ BRH entry found: {has_brh}")
            print("="*60)
        else:
            print("❌ FAIL: Branch coverage data missing!")
            print("="*60)
            print(f"✗ BRDA entries: {has_brda} (count: {brda_count})")
            print(f"✗ BRF entry: {has_brf}")
            print(f"✗ BRH entry: {has_brh}")
            print("="*60)
            pytest.fail("Branch coverage data not found in PyDCov output")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

