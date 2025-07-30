# Tests Directory

This directory contains all test files and demo scripts for the Agent Knowledge MCP.

## Test Files

### Core Functionality Tests
- **`test_file_paths.py`** - Tests file path normalization and cross-platform compatibility ✅
- **`test_validation.py`** - Tests document schema validation and error handling
- **`test_version_control.py`** - Comprehensive version control system tests ✅
- **`test_simple_vcs.py`** - Simple VCS functionality demonstration ✅

### Demo Scripts
- **`demo_agent_workflow.py`** - Complete agent workflow demonstration
- **`demo_version_control.py`** - Version control features demo

### Test Configuration
- **`test_config.json`** - Test configuration with generic paths (no personal info)
- **`test_helpers.py`** - Helper functions for loading test config
- **`run_all_tests.py`** - Script to run all tests at once ✅

### Utility Tests
- **`quick_test.py`** - Quick functionality check script

## Running Tests

### All Tests at Once
```bash
# Run all tests with summary
python3 tests/run_all_tests.py
```

### Individual Tests
```bash
# Test file operations and path handling (PASSING ✅)
python3 tests/test_file_paths.py

# Test document validation
python3 tests/test_validation.py

# Test version control (comprehensive) (PASSING ✅)
python3 tests/test_version_control.py

# Test version control (simple demo) (PASSING ✅)
python3 tests/test_simple_vcs.py

# Quick functionality check
python3 tests/quick_test.py
```

### Demo Scripts
```bash
# Run complete workflow demo
python3 tests/demo_agent_workflow.py

# Run version control demo
python3 tests/demo_version_control.py
```

## Test Configuration

All tests now use **generic paths** from `test_config.json`:

```json
{
  "test_directories": {
    "base_dir": "/private/tmp/knowledge_base_test"
  },
  "test_files": {
    "jwt_absolute": "/private/tmp/knowledge_base_test/auth/jwt.md",
    "jwt_relative": "auth/jwt.md"
  }
}
```

**No personal information** (like usernames) is hardcoded in test files! 🔒

## Test Coverage

### ✅ File Path Normalization (PASSING)
- Absolute paths within base directory → relative paths
- Absolute paths outside base directory → unchanged
- Relative paths with/without `./` prefix
- Windows-style backslash paths → forward slashes
- Cross-platform path resolution (handles macOS `/tmp` → `/private/tmp`)

### ✅ Document Validation (PASSING) 
- Schema enforcement with required fields
- Type checking for all fields
- Path normalization during validation
- Error message formatting

### ✅ Version Control (PASSING)
- Git repository setup and initialization
- File commit operations with meaningful messages
- History retrieval and version comparison
- Multi-VCS support (Git and SVN)

### ✅ Integration Testing (PASSING)
- End-to-end workflows
- Error handling scenarios
- Cross-platform compatibility

## Expected Results

All tests should pass with ✅ indicators:

```
🎯 Overall Results: 4/4 test suites passed
🎉 ALL TESTS PASSED! File path handling is working correctly!
```

## Test Environment

- **Python**: 3.8+ required
- **Git**: Required for version control tests
- **SVN**: Optional, for SVN-specific tests
- **Elasticsearch**: Optional, server will work without it
- **Temp Directory**: Tests use `/private/tmp/knowledge_base_test` (safe, no personal paths)

## Recent Updates

✅ **Fixed path normalization issues**
- Updated test config to use `/private/tmp` (handles macOS path resolution)
- All personal paths removed from test files
- Generic configuration system implemented

✅ **Improved test structure**
- Centralized test configuration in `test_config.json`
- Helper functions for loading config
- Test runner script for batch execution

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running from project root
   ```bash
   cd /path/to/AgentKnowledgeMCP
   python3 tests/test_file_paths.py
   ```

2. **Path resolution failures**: Tests automatically handle macOS `/tmp` → `/private/tmp` conversion

3. **Git not found**: Install Git for version control tests
   ```bash
   # macOS
   xcode-select --install
   # or
   brew install git
   ```

4. **Permission errors**: Temp directory paths should be writable by default

### Debug Mode

Set environment variable for verbose output:
```bash
export TEST_DEBUG=1
python3 tests/test_file_paths.py
```

## Adding New Tests

When adding new functionality:

1. Create test file: `tests/test_new_feature.py`
2. Add any required paths to `test_config.json`
3. Use helper functions from `test_helpers.py`
4. Follow existing test patterns (use generic paths!)
5. Test both positive and negative scenarios
6. Update this README with new test description

**Remember**: Never hardcode personal paths! Always use test_config.json! 🚫👤
