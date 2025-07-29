# Testing Guide for Pi-hole MCP Server

This project has comprehensive unit tests with 100% code coverage. This guide explains how to run the tests and understand the testing setup.

## Quick Start

### Install Dependencies

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or use make
make install
```

### Run Tests

```bash
# Run all tests with coverage (requires 100% coverage)
make test

# Or directly with pytest
python -m pytest --cov=pihole_mcp_server --cov-report=term-missing --cov-fail-under=100 -v
```

## Test Commands

### Basic Testing

```bash
# Run all tests with 100% coverage requirement
make test

# Run tests without coverage for faster feedback
make test-fast

# Run tests with coverage but don't fail on coverage threshold
make test-cov

# Generate HTML coverage report
make test-html
```

### Selective Testing

```bash
# Run only unit tests (skip integration tests)
make test-unit

# Run only integration tests
make test-integration
```

### Using the Test Script

```bash
# Run with the provided script
./scripts/run_tests.sh

# Run specific test files
./scripts/run_tests.sh tests/test_pihole_client.py

# Run tests matching a pattern
./scripts/run_tests.sh -k "test_config"
```

## Test Structure

The test suite is organized as follows:

```
tests/
├── conftest.py              # Shared fixtures and utilities
├── test_pihole_config.py    # Tests for PiHoleConfig and models
├── test_pihole_client.py    # Tests for PiHoleClient class
├── test_credential_manager.py # Tests for CredentialManager
├── test_server.py           # Tests for PiHoleMCPServer
├── test_cli.py              # Tests for CLI commands
└── test_package.py          # Tests for package imports
```

## Coverage Requirements

This project maintains **100% code coverage**. The tests cover:

### PiHoleConfig (`test_pihole_config.py`)
- Configuration validation
- Property calculations (base_url, api_url)
- Serialization/deserialization
- Error handling

### PiHoleClient (`test_pihole_client.py`)
- HTTP client initialization
- Session management and caching
- API version detection (legacy vs modern)
- Authentication (API key and web password)
- All API endpoints (status, enable, disable, version, etc.)
- Error handling and exception mapping
- Connection and authentication testing

### CredentialManager (`test_credential_manager.py`)
- Secure credential storage and retrieval
- Encryption/decryption operations
- Keyring integration with fallback to file storage
- Machine ID generation
- Configuration directory management
- Error handling for storage/retrieval failures

### PiHoleMCPServer (`test_server.py`)
- MCP server initialization
- Tool registration and handling
- Async operations
- Client management
- All tool handlers (status, enable, disable, stats, etc.)
- Error handling and tool error responses

### CLI (`test_cli.py`)
- All CLI commands (login, status, test, enable, disable, logout, info)
- Command-line argument parsing
- User interaction (prompts, confirmations)
- Error handling and exit codes
- Integration with other components

### Package (`test_package.py`)
- Package imports and exports
- Module structure
- Class instantiation through package imports
- Exception inheritance

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `sample_pihole_config`: Sample PiHoleConfig instances
- `sample_pihole_status`: Sample status responses
- `sample_stored_credentials`: Sample credential objects
- `temp_config_dir`: Temporary directories for testing
- `mock_*`: Various mock objects for external dependencies
- `responses_mock`: HTTP response mocking
- Utility functions for assertions

## Running Tests in Development

### Continuous Testing

```bash
# Install pytest-xdist for parallel testing
pip install pytest-xdist

# Run tests in parallel
python -m pytest -n auto

# Watch for file changes (requires pytest-watch)
pip install pytest-watch
ptw
```

### Debugging Tests

```bash
# Run with verbose output and stop on first failure
python -m pytest -v -x

# Run specific test
python -m pytest tests/test_pihole_client.py::TestPiHoleClient::test_init_basic

# Run with pdb debugger on failures
python -m pytest --pdb

# Show local variables in traceback
python -m pytest -l
```

## Test Environment

### Mocking Strategy

Tests use extensive mocking to avoid external dependencies:

- **HTTP Requests**: Mocked using `responses` library and `unittest.mock`
- **File System**: Mocked using `tempfile` and `unittest.mock`
- **Keyring**: Mocked to test both success and failure scenarios
- **System Calls**: Mocked for cross-platform compatibility
- **Time**: Mocked for testing time-dependent behavior

### Test Isolation

Each test is isolated and doesn't depend on:

- External Pi-hole servers
- Real file system operations (except temporary directories)
- Network connectivity
- System keyring services
- Other tests

## Coverage Reports

### Terminal Report

```bash
make test
# Shows coverage percentage and missing lines
```

### HTML Report

```bash
make test-html
# Opens htmlcov/index.html in browser (on macOS)
```

### XML Report (for CI)

```bash
make ci-test
# Generates reports/coverage.xml for CI systems
```

## CI Integration

The project includes CI-specific targets:

```bash
# Run tests in CI environment
make ci-test

# Run linting in CI environment
make ci-lint

# Run all CI checks
make ci-test ci-lint
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've installed the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Coverage Below 100%**: Check the terminal output for missing lines:
   ```bash
   make test-cov  # Don't fail on coverage
   ```

3. **Mock Issues**: Ensure mocks are properly set up in `conftest.py`

4. **Async Test Issues**: Make sure async tests are marked with `@pytest.mark.asyncio`

### Getting Help

- Check test output for specific error messages
- Run individual test files to isolate issues
- Use `pytest --tb=long` for detailed tracebacks
- Check the fixture definitions in `conftest.py`

## Writing New Tests

When adding new features:

1. **Add tests first** (TDD approach recommended)
2. **Maintain 100% coverage** - tests will fail if coverage drops
3. **Use existing fixtures** from `conftest.py` when possible
4. **Mock external dependencies** appropriately
5. **Test both success and failure scenarios**
6. **Follow existing test naming conventions**

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>`

Example:
```python
class TestPiHoleClient:
    def test_init_basic(self):
        """Test basic initialization."""
        pass
    
    def test_init_with_ssl_disabled(self):
        """Test initialization with SSL disabled."""
        pass
``` 