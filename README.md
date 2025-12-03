# 🎾 padel-booker

[![CI](https://github.com/CICDamen/padel-booker/actions/workflows/test.yml/badge.svg)](https://github.com/CICDamen/padel-booker/actions/workflows/test.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automated padel court booking API for Sportclub Houten, powered by FastAPI and Selenium.

---

## 🚀 Features

- **RESTful API** for automated court booking
- **Basic Authentication** for secure access
- **Background processing** for booking operations
- **Smart slot fallback**: Automatically searches backwards through workdays if preferred date unavailable
- Smart player selection with rotation and error handling
- **Flexible booking parameters** passed directly via API
- Headless browser automation (no UI required)
- **Docker support** for easy deployment
- Comprehensive logging and error reporting

---

## 📦 Project Structure

```
padel-booker/
├── src/
│   ├── api.py              # FastAPI application
│   ├── models.py           # Pydantic models for API
│   ├── booker.py           # Main booking automation logic
│   ├── utils.py            # Utilities (driver, logging, auth, background tasks)
│   └── exceptions.py       # Custom exceptions
├── Dockerfile              # Container configuration
├── pyproject.toml          # Project metadata & dependencies
└── README.md               # This file
```

---

## ⚙️ Installation

### 🐳 Docker (Recommended)

1. **Clone the repo:**
   ```bash
   git clone https://github.com/yourusername/padel-booker.git
   cd padel-booker
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t padel-booker .
   ```

3. **Run with environment variables:**
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e API_USERNAME=your_api_user \
     -e API_PASSWORD=your_api_password \
     -e BOOKER_PASSWORD=your_booking_password \
     -e BOOKER_USERNAME=your_booking_username \
     -e ENABLE_BOOKING=true \  # Set to true to enable actual bookings
     -e MAX_BOOKING_ATTEMPTS=number_of_attempts \ # Optional: max attempts for booking - if players are not available
     -t padel-booker
   ```

### 🐍 Local Development

1. **Install dependencies (Python 3.12+):**
   ```bash
   pip install uv
   uv sync
   ```

2. **Run the API server:**
   ```bash
   uvicorn src.api:app --host 0.0.0.0 --port 8080
   ```

---

## 🛠️ Configuration

### Environment Variables

**Required:**
- `API_USERNAME`: Username for API authentication  
- `API_PASSWORD`: Password for API authentication
- `BOOKER_USERNAME`: Username for the booking platform
- `BOOKER_PASSWORD`: Password for the booking platform

**Optional:**
- `ENABLE_BOOKING`: Set to `true` to enable actual booking confirmation. When not set or set to any other value, the system runs in dry-run mode (simulates booking without final confirmation)
- `MAX_BOOKING_ATTEMPTS`: Maximum number of attempts for booking if players are not available

**Example:**
```bash
export API_USERNAME="admin"
export API_PASSWORD="secure_password"
export ENABLE_BOOKING="true"  # Enable actual bookings (omit for dry-run mode)
```

---

## 📡 API Usage

The API runs on port **8080** and requires **Basic Authentication** for all endpoints except `/health`.

### Authentication
All API endpoints require HTTP Basic Authentication using the credentials set in `API_USERNAME` and `API_PASSWORD`.

### Endpoints

#### 🏥 Health Check
```bash
GET /health
```
```json
{
  "status": "healthy",
  "service": "padel-booker"
}
```

#### 🎾 Start Booking
```bash
POST /api/book
Authorization: Basic base64(username:password)
Content-Type: application/json

{
  "login_url": "https://houten.baanreserveren.nl/",
  "booking_date": "2025-07-28",
  "start_time": "21:30",
  "duration_hours": 1.5,
  "booker_first_name": "John",
  "player_candidates": ["John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson"]
}
```

**Parameters:**
- `login_url`: URL to the booking website
- `booking_date`: Date to book in YYYY-MM-DD format (automatically searches backwards through workdays if unavailable)
- `start_time`: Start time in HH:MM format
- `duration_hours`: Duration in hours (e.g., 1.5 for 90 minutes)
- `booker_first_name`: First name of the person making the booking
- `player_candidates`: Array of player names to try for the booking

**Response:**
```json
{
  "status": "started",
  "message": "Booking process started",
  "started_at": "2025-01-20T14:30:00"
}
```

#### 📊 Check Booking Status
```bash
GET /api/status
Authorization: Basic base64(username:password)
```

**While running:**
```json
{
  "running": true,
  "result": null,
  "started_at": "2025-01-20T14:30:00"
}
```

**Success result:**
```json
{
  "running": false,
  "result": {
    "status": "success",
    "message": "Booking successful with players: ['John Smith', 'John']",
    "players": ["John Smith", "John"],
    "booking_date": "2025-07-28"
  },
  "started_at": "2025-01-20T14:30:00"
}
```

**Error result:**
```json
{
  "running": false,
  "result": {
    "status": "error",
    "message": "Login failed"
  },
  "started_at": "2025-01-20T14:30:00"
}
```

### Example Usage with curl

```bash
# Check health
curl http://localhost:8080/health

# Start booking
curl -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "login_url": "https://houten.baanreserveren.nl/",
    "booking_date": "2025-07-28",
    "start_time": "21:30",
    "duration_hours": 1.5,
    "booker_first_name": "John",
    "player_candidates": ["John Smith", "Jane Doe", "Mike Johnson"]
  }' \
  http://localhost:8080/api/book

# Check status
curl -u admin:password http://localhost:8080/api/status
```

---

## 🧪 Testing

The project uses pytest with comprehensive test coverage across all modules.

### Test Summary

**61 tests total:**
- **59 unit tests** (fast, no browser, mocked) - ~2.3s
- **2 integration tests** (requires browser and credentials) - ~varies

### Running Tests

**Run all tests:**
```bash
uv run pytest
```

**Run only unit tests (fast, no browser needed):**
```bash
uv run pytest -m unit
```

**Run only integration tests (requires browser and credentials):**
```bash
uv run pytest -m integration
```

**Run with verbose output:**
```bash
uv run pytest -v
```

**Run specific test file:**
```bash
uv run pytest tests/test_api.py
uv run pytest tests/test_booker.py
uv run pytest tests/test_utils.py
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                           # Pytest fixtures and configuration
├── test_api.py                           # FastAPI endpoint tests (9 tests)
├── test_booker.py                        # PadelBooker class tests (14 tests)
├── test_integration_booking_flow.py      # Integration tests (2 tests)
├── test_exceptions.py                    # Custom exception tests (6 tests)
├── test_models.py                        # Pydantic model tests (7 tests)
├── test_navigation_strategy.py           # Navigation strategy tests (9 tests)
└── test_utils.py                         # Utility function tests (13 tests)
```

### Integration Tests

Integration tests require:
- Real browser (ChromeDriver)
- Valid credentials (BOOKER_USERNAME, BOOKER_PASSWORD)
- Network access to booking website

**What they test:**
- `test_full_booking_flow_without_confirmation`: Tests the complete booking flow (login → navigate → find slot → select players → reach confirmation) **without** clicking the final "Bevestigen" button, so no actual booking is made
- `test_booking_flow_with_fallback_dates`: Tests the backwards day search functionality with real website interaction

**Note**: Integration tests will be skipped if credentials are not provided.

### Test Coverage by Module

- **api.py**: Endpoint authentication, booking flow, status checks
- **booker.py**: Initialization, slot finding, player selection, context manager, backwards day search
- **models.py**: Pydantic validation, field requirements
- **utils.py**: Driver setup, logging, authentication, booking enabled flag
- **navigation_strategy.py**: Desktop navigation strategies, factory pattern
- **exceptions.py**: Custom exception behavior and inheritance

### Configuration

Pytest configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`.

Test markers:
- `@pytest.mark.unit` - Fast tests with mocks (no browser)
- `@pytest.mark.integration` - Full tests with real browser
- `@pytest.mark.slow` - Long-running tests

### Running Tests in Docker

```bash
docker run --rm \
  -v "$(pwd)/tests:/app/tests" \
  -v "$(pwd)/pyproject.toml:/app/pyproject.toml" \
  -e BOOKER_USERNAME="your_username" \
  -e BOOKER_PASSWORD="your_password" \
  -e CHROMEDRIVER_PATH="/usr/bin/chromedriver" \
  padel-booker \
  uv run pytest
```

---

## 🔄 CI/CD

The project uses GitHub Actions for continuous integration and deployment.

### Workflows

**Docker Build & Test Workflow** (runs on PRs):
- **Build**: Verify Docker image builds successfully
- **Import Test**: Verify Python imports work correctly
- **Unit Tests**: Fast tests without browser (59 tests, ~2.3s)
- **Integration Tests**: Full browser tests (2 tests, if credentials configured)
- **Test Summary**: Aggregated results

### Required Secrets

For integration tests to run in CI, configure these GitHub secrets:
- `BOOKER_USERNAME`: Booking platform username
- `BOOKER_PASSWORD`: Booking platform password

**Note**: Integration tests are automatically skipped if:
- Credentials are not configured
- No integration tests exist in the test suite

### Branch Protection

Recommended branch protection rules for `main`:
- ✅ Require pull request reviews
- ✅ Require status checks (CI, Docker Build)
- ✅ Require branches to be up to date

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Please open an issue to discuss your ideas or report bugs.

**All PRs will automatically run:**
- Docker build verification
- Import tests
- Unit tests (59 tests)
- Integration tests (2 tests, if credentials configured)

---

## 📜 License

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2025 Casper Damen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

