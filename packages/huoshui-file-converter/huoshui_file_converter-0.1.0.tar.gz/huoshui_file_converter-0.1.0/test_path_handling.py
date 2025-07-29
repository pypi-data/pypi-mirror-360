#!/usr/bin/env python3
"""
Comprehensive test suite for path handling logic in server/main.py
Tests various scenarios including edge cases, security, and cross-platform compatibility
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from unittest.mock import patch

# Add the server directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Import the functions we want to test
from main import _validate_path, _detect_format_by_extension, _detect_format_by_content
from fastmcp.exceptions import ToolError


class PathHandlingTester:
    """Test suite for path handling logic"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Create temporary test files and directories"""
        self.temp_dir = tempfile.mkdtemp(prefix="path_test_")
        print(f"Created test directory: {self.temp_dir}")
        
        # Create test files with various extensions
        test_files = {
            "test.md": "# Test Markdown\nThis is a test.",
            "test.txt": "This is plain text.",
            "test.docx": "DOCX placeholder",  # Won't be a real DOCX
            "test.html": "<html><body>Test HTML</body></html>",
            "test.unknown": "Unknown file type",
            "test with spaces.md": "# File with spaces",
            "test-unicode-文件.txt": "Unicode filename test",
            "": "Empty filename",  # This will be renamed
        }
        
        for filename, content in test_files.items():
            if filename == "":
                filename = "empty_name"
            file_path = Path(self.temp_dir) / filename
            file_path.write_text(content, encoding='utf-8')
        
        # Create subdirectory structure
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()
        (subdir / "nested.md").write_text("# Nested file")
        
        # Create symlink if supported
        try:
            link_path = Path(self.temp_dir) / "link.md"
            target_path = Path(self.temp_dir) / "test.md"
            link_path.symlink_to(target_path)
        except (OSError, NotImplementedError):
            print("Symlinks not supported on this platform")
    
    def cleanup(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up test directory: {self.temp_dir}")
    
    def run_test(self, test_name: str, test_func) -> Dict:
        """Run a single test and record results"""
        try:
            result = test_func()
            status = "PASS" if result.get("success", False) else "FAIL"
            self.test_results.append({
                "test": test_name,
                "status": status,
                "details": result
            })
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "ERROR",
                "details": {"error": str(e)}
            })
            return {"success": False, "error": str(e)}
    
    def test_path_resolution_logic(self) -> Dict:
        """Test 1: Path Resolution Logic"""
        results = []
        
        # Test different input types
        test_cases = [
            # (input_path, expected_behavior, description)
            ("Desktop/file.txt", "relative_to_home", "Relative path"),
            ("/absolute/path/file.txt", "absolute", "Absolute Unix path"),
            ("~/file.txt", "tilde_expansion", "Tilde expansion"),
            ("../file.txt", "parent_directory", "Parent directory reference"),
            ("./file.txt", "current_directory", "Current directory reference"),
            ("", "empty_path", "Empty path"),
            ("file.txt", "home_directory", "Simple filename"),
        ]
        
        if os.name == 'nt':  # Windows
            test_cases.extend([
                ("C:\\Users\\file.txt", "absolute_windows", "Absolute Windows path"),
                ("Desktop\\file.txt", "relative_windows", "Relative Windows path"),
            ])
        
        for input_path, expected_behavior, description in test_cases:
            try:
                if input_path == "":
                    # Empty path should raise an error
                    try:
                        result = _validate_path(input_path)
                        results.append({
                            "input": input_path,
                            "description": description,
                            "result": f"Unexpected success: {result}",
                            "status": "UNEXPECTED"
                        })
                    except Exception as e:
                        results.append({
                            "input": input_path,
                            "description": description,
                            "result": f"Expected error: {e}",
                            "status": "EXPECTED"
                        })
                else:
                    result = _validate_path(input_path)
                    results.append({
                        "input": input_path,
                        "description": description,
                        "result": str(result),
                        "is_absolute": result.is_absolute(),
                        "exists": result.exists(),
                        "status": "SUCCESS"
                    })
            except Exception as e:
                results.append({
                    "input": input_path,
                    "description": description,
                    "result": f"Error: {e}",
                    "status": "ERROR"
                })
        
        return {
            "success": True,
            "test_cases": results,
            "summary": f"Tested {len(test_cases)} path resolution scenarios"
        }
    
    def test_security_validation(self) -> Dict:
        """Test 2: Security Validation"""
        results = []
        
        # Test restricted directories
        restricted_paths = [
            "/etc/passwd",
            "/sys/kernel",
            "/proc/version",
            "/dev/null",
            "/boot/vmlinuz",
            "/root/.bashrc",
            "/System/Library/CoreServices",
            "/Library/System/Library",
            "/private/etc/hosts",
        ]
        
        if os.name == 'nt':  # Windows
            restricted_paths.extend([
                "C:\\Windows\\System32\\config",
                "C:\\Program Files\\test",
                "C:\\Program Files (x86)\\test",
                "C:\\Windows\\System32\\drivers",
            ])
        
        for path in restricted_paths:
            try:
                result = _validate_path(path)
                results.append({
                    "path": path,
                    "result": f"SECURITY ISSUE: Access allowed to {result}",
                    "status": "SECURITY_FAIL"
                })
            except ToolError as e:
                if "Access to system directory not allowed" in str(e):
                    results.append({
                        "path": path,
                        "result": f"Correctly blocked: {e}",
                        "status": "SECURITY_PASS"
                    })
                else:
                    results.append({
                        "path": path,
                        "result": f"Unexpected error: {e}",
                        "status": "UNEXPECTED"
                    })
            except Exception as e:
                results.append({
                    "path": path,
                    "result": f"Other error: {e}",
                    "status": "ERROR"
                })
        
        # Test bypass attempts
        bypass_attempts = [
            "/etc/../etc/passwd",
            "/home/../etc/passwd",
            "/../etc/passwd",
            "/etc/./passwd",
            "/etc//passwd",
        ]
        
        for path in bypass_attempts:
            try:
                result = _validate_path(path)
                # Check if the resolved path is in restricted area
                resolved_str = str(result)
                is_restricted = any(resolved_str.startswith(restricted) for restricted in ['/etc', '/sys', '/proc', '/dev', '/boot', '/root'])
                
                results.append({
                    "path": path,
                    "resolved": resolved_str,
                    "result": "BYPASS DETECTED" if is_restricted else "Safe resolution",
                    "status": "SECURITY_FAIL" if is_restricted else "SECURITY_PASS"
                })
            except ToolError as e:
                results.append({
                    "path": path,
                    "result": f"Correctly blocked: {e}",
                    "status": "SECURITY_PASS"
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "result": f"Error: {e}",
                    "status": "ERROR"
                })
        
        security_passes = sum(1 for r in results if r["status"] == "SECURITY_PASS")
        security_fails = sum(1 for r in results if r["status"] == "SECURITY_FAIL")
        
        return {
            "success": security_fails == 0,
            "test_cases": results,
            "summary": f"Security tests: {security_passes} passed, {security_fails} failed"
        }
    
    def test_cross_platform_compatibility(self) -> Dict:
        """Test 3: Cross-Platform Compatibility"""
        results = []
        
        # Test path separator handling
        test_paths = [
            "folder/file.txt",
            "folder\\file.txt",
            "folder/subfolder/file.txt",
            "folder\\subfolder\\file.txt",
            "folder/subfolder\\file.txt",  # Mixed separators
        ]
        
        for path in test_paths:
            try:
                result = _validate_path(path)
                results.append({
                    "input": path,
                    "result": str(result),
                    "normalized": str(result).replace('\\', '/'),
                    "status": "SUCCESS"
                })
            except Exception as e:
                results.append({
                    "input": path,
                    "result": f"Error: {e}",
                    "status": "ERROR"
                })
        
        # Test platform-specific paths
        platform_tests = []
        if os.name == 'nt':  # Windows
            platform_tests = [
                "C:\\Users\\test\\file.txt",
                "D:\\Documents\\file.txt",
                "\\\\server\\share\\file.txt",  # UNC path
            ]
        else:  # Unix-like
            platform_tests = [
                "/home/user/file.txt",
                "/tmp/file.txt",
                "/var/log/file.txt",
            ]
        
        for path in platform_tests:
            try:
                result = _validate_path(path)
                results.append({
                    "input": path,
                    "result": str(result),
                    "platform": os.name,
                    "status": "SUCCESS"
                })
            except Exception as e:
                results.append({
                    "input": path,
                    "result": f"Error: {e}",
                    "platform": os.name,
                    "status": "ERROR"
                })
        
        return {
            "success": True,
            "test_cases": results,
            "summary": f"Cross-platform tests completed for {os.name}"
        }
    
    def test_error_scenarios(self) -> Dict:
        """Test 4: Error Scenarios"""
        results = []
        
        # Test malformed paths
        malformed_paths = [
            "\x00invalid",  # Null byte
            "con.txt" if os.name == 'nt' else "/dev/tty",  # Reserved names
            "file\nwith\nnewlines.txt",
            "file\twith\ttabs.txt",
            "file<with>invalid:chars.txt" if os.name == 'nt' else "file|with|pipes.txt",
        ]
        
        for path in malformed_paths:
            try:
                result = _validate_path(path)
                results.append({
                    "input": repr(path),
                    "result": f"Unexpectedly succeeded: {result}",
                    "status": "UNEXPECTED"
                })
            except Exception as e:
                results.append({
                    "input": repr(path),
                    "result": f"Expected error: {e}",
                    "status": "EXPECTED"
                })
        
        # Test non-existent paths (should still validate but not exist)
        non_existent_paths = [
            "nonexistent/file.txt",
            "/tmp/nonexistent/file.txt",
            "~/nonexistent/file.txt",
        ]
        
        for path in non_existent_paths:
            try:
                result = _validate_path(path)
                results.append({
                    "input": path,
                    "result": str(result),
                    "exists": result.exists(),
                    "status": "SUCCESS" if not result.exists() else "UNEXPECTED"
                })
            except Exception as e:
                results.append({
                    "input": path,
                    "result": f"Error: {e}",
                    "status": "ERROR"
                })
        
        # Test permission scenarios (simulate)
        try:
            # Try to access a system directory we don't have permission to
            restricted_path = "/root/private.txt" if os.name != 'nt' else "C:\\System Volume Information\\test.txt"
            result = _validate_path(restricted_path)
            results.append({
                "input": restricted_path,
                "result": f"Permission test: {result}",
                "status": "PERMISSION_TEST"
            })
        except Exception as e:
            results.append({
                "input": restricted_path,
                "result": f"Permission error: {e}",
                "status": "PERMISSION_ERROR"
            })
        
        return {
            "success": True,
            "test_cases": results,
            "summary": f"Error scenario tests completed"
        }
    
    def test_format_detection(self) -> Dict:
        """Test 5: Format Detection"""
        results = []
        
        # Test files in our temp directory
        test_files = [
            ("test.md", "markdown"),
            ("test.txt", "txt"),
            ("test.html", "html"),
            ("test.docx", "docx"),
            ("test.unknown", "unknown"),
            ("test with spaces.md", "markdown"),
            ("test-unicode-文件.txt", "txt"),
        ]
        
        for filename, expected_format in test_files:
            file_path = Path(self.temp_dir) / filename
            if not file_path.exists():
                continue
                
            try:
                # Test extension-based detection
                ext_format = _detect_format_by_extension(file_path)
                
                # Test content-based detection
                try:
                    content_format = _detect_format_by_content(file_path)
                except Exception as e:
                    content_format = f"Error: {e}"
                
                results.append({
                    "file": filename,
                    "expected": expected_format,
                    "extension_detection": ext_format,
                    "content_detection": content_format,
                    "status": "SUCCESS"
                })
            except Exception as e:
                results.append({
                    "file": filename,
                    "expected": expected_format,
                    "result": f"Error: {e}",
                    "status": "ERROR"
                })
        
        return {
            "success": True,
            "test_cases": results,
            "summary": f"Format detection tests completed"
        }
    
    def test_user_experience_scenarios(self) -> Dict:
        """Test 6: User Experience Scenarios"""
        results = []
        
        # Test common user input patterns
        user_patterns = [
            ("Desktop/report.docx", "Common desktop file"),
            ("Documents/MyFile.txt", "Common documents file"),
            ("Downloads/file.pdf", "Common downloads file"),
            ("Pictures/image.jpg", "Common pictures file"),
            ("Music/song.mp3", "Common music file"),
            ("file.txt", "File in home directory"),
            ("./file.txt", "Current directory file"),
            ("../file.txt", "Parent directory file"),
            ("~/Desktop/file.txt", "Tilde expansion"),
            ("C:\\Users\\Me\\Desktop\\file.txt" if os.name == 'nt' else "/Users/me/Desktop/file.txt", "Full path"),
        ]
        
        for pattern, description in user_patterns:
            try:
                result = _validate_path(pattern)
                results.append({
                    "pattern": pattern,
                    "description": description,
                    "result": str(result),
                    "user_friendly": True,
                    "status": "SUCCESS"
                })
            except Exception as e:
                results.append({
                    "pattern": pattern,
                    "description": description,
                    "result": f"Error: {e}",
                    "user_friendly": False,
                    "status": "ERROR"
                })
        
        # Test error message clarity
        error_patterns = [
            ("/etc/passwd", "Should give clear security error"),
            ("nonexistent.txt", "Should handle non-existent file gracefully"),
            ("", "Should handle empty path"),
        ]
        
        for pattern, expectation in error_patterns:
            try:
                result = _validate_path(pattern)
                results.append({
                    "pattern": pattern,
                    "expectation": expectation,
                    "result": f"Unexpected success: {result}",
                    "error_clarity": "N/A",
                    "status": "UNEXPECTED"
                })
            except Exception as e:
                error_msg = str(e)
                is_clear = len(error_msg) > 10 and not error_msg.startswith("Traceback")
                results.append({
                    "pattern": pattern,
                    "expectation": expectation,
                    "result": error_msg,
                    "error_clarity": "Clear" if is_clear else "Unclear",
                    "status": "EXPECTED"
                })
        
        return {
            "success": True,
            "test_cases": results,
            "summary": f"User experience tests completed"
        }
    
    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 60)
        print("PATH HANDLING COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        
        test_suites = [
            ("Path Resolution Logic", self.test_path_resolution_logic),
            ("Security Validation", self.test_security_validation),
            ("Cross-Platform Compatibility", self.test_cross_platform_compatibility),
            ("Error Scenarios", self.test_error_scenarios),
            ("Format Detection", self.test_format_detection),
            ("User Experience Scenarios", self.test_user_experience_scenarios),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n{'-' * 40}")
            print(f"Running: {suite_name}")
            print(f"{'-' * 40}")
            
            result = self.run_test(suite_name, test_func)
            
            if result.get("success"):
                print(f"✅ {suite_name}: PASSED")
            else:
                print(f"❌ {suite_name}: FAILED")
            
            if "summary" in result:
                print(f"   {result['summary']}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print overall test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "FAIL")
        error_tests = sum(1 for r in self.test_results if r["status"] == "ERROR")
        
        print(f"Total Test Suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        
        if failed_tests > 0 or error_tests > 0:
            print("\nFailed/Error Tests:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"  - {result['test']}: {result['status']}")
                    if "error" in result["details"]:
                        print(f"    Error: {result['details']['error']}")
        
        print("\nDETAILED ANALYSIS:")
        self.analyze_results()
    
    def analyze_results(self):
        """Analyze test results and provide recommendations"""
        print("\n" + "=" * 60)
        print("DETAILED ANALYSIS & RECOMMENDATIONS")
        print("=" * 60)
        
        # Security Analysis
        print("\n1. SECURITY ANALYSIS:")
        security_results = next((r for r in self.test_results if r["test"] == "Security Validation"), None)
        if security_results:
            security_cases = security_results["details"].get("test_cases", [])
            security_fails = [c for c in security_cases if c["status"] == "SECURITY_FAIL"]
            
            if security_fails:
                print("   ⚠️  SECURITY ISSUES FOUND:")
                for fail in security_fails:
                    print(f"     - {fail['path']}: {fail['result']}")
            else:
                print("   ✅ Security validation appears robust")
        
        # Path Resolution Analysis
        print("\n2. PATH RESOLUTION ANALYSIS:")
        path_results = next((r for r in self.test_results if r["test"] == "Path Resolution Logic"), None)
        if path_results:
            path_cases = path_results["details"].get("test_cases", [])
            errors = [c for c in path_cases if c["status"] == "ERROR"]
            
            if errors:
                print("   ⚠️  PATH RESOLUTION ISSUES:")
                for error in errors:
                    print(f"     - {error['input']}: {error['result']}")
            else:
                print("   ✅ Path resolution working correctly")
        
        # User Experience Analysis
        print("\n3. USER EXPERIENCE ANALYSIS:")
        ux_results = next((r for r in self.test_results if r["test"] == "User Experience Scenarios"), None)
        if ux_results:
            ux_cases = ux_results["details"].get("test_cases", [])
            unclear_errors = [c for c in ux_cases if c.get("error_clarity") == "Unclear"]
            
            if unclear_errors:
                print("   ⚠️  ERROR MESSAGE CLARITY ISSUES:")
                for error in unclear_errors:
                    print(f"     - {error['pattern']}: {error['result']}")
            else:
                print("   ✅ Error messages appear clear and helpful")
        
        # Recommendations
        print("\n4. RECOMMENDATIONS:")
        print("   • Consider adding tilde expansion (~) support if not already present")
        print("   • Implement better error messages for common user mistakes")
        print("   • Add support for drag-and-drop file paths with spaces")
        print("   • Consider adding path validation hints in error messages")
        print("   • Test with very long file paths (>260 chars on Windows)")
        print("   • Add support for UNC paths on Windows if needed")
        print("   • Consider case-insensitive path handling on Windows")


def main():
    """Main test execution"""
    tester = PathHandlingTester()
    
    try:
        tester.run_all_tests()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()