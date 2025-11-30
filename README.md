# 🎾 padel-booker

[![CI](https://github.com/CICDamen/padel-booker/actions/workflows/ci.yml/badge.svg)](https://github.com/CICDamen/padel-booker/actions/workflows/ci.yml)
[![Docker Build](https://github.com/CICDamen/padel-booker/actions/workflows/docker.yml/badge.svg)](https://github.com/CICDamen/padel-booker/actions/workflows/docker.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automated padel court booking API for Sportclub Houten, powered by FastAPI and Selenium.

---

## 🚀 Features

- **RESTful API** for automated court booking
- **Basic Authentication** for secure access
- **Background processing** for booking operations
- Smart slot and player selection with rotation and error handling
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
  "player_candidates": ["John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson"],
  "device_mode": "mobile"
}
```

**Parameters:**
- `login_url`: URL to the booking website
- `booking_date`: Date to book in YYYY-MM-DD format
- `start_time`: Start time in HH:MM format
- `duration_hours`: Duration in hours (e.g., 1.5 for 90 minutes)
- `booker_first_name`: First name of the person making the booking
- `player_candidates`: Array of player names to try for the booking
- `device_mode` (optional): Either `"mobile"` (default) or `"desktop"`
  - **Mobile mode**: Allows booking 29 days in advance, uses mobile-optimized navigation
  - **Desktop mode**: Allows booking 28 days in advance, uses calendar-based navigation

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

# Start booking (mobile mode - 29 days advance)
curl -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "login_url": "https://houten.baanreserveren.nl/",
    "booking_date": "2025-07-28",
    "start_time": "21:30",
    "duration_hours": 1.5,
    "booker_first_name": "John",
    "player_candidates": ["John Smith", "Jane Doe", "Mike Johnson"],
    "device_mode": "mobile"
  }' \
  http://localhost:8080/api/book

# Start booking (desktop mode - 28 days advance)
curl -u admin:password \
  -H "Content-Type: application/json" \
  -d '{
    "login_url": "https://houten.baanreserveren.nl/",
    "booking_date": "2025-07-28",
    "start_time": "21:30",
    "duration_hours": 1.5,
    "booker_first_name": "John",
    "player_candidates": ["John Smith", "Jane Doe", "Mike Johnson"],
    "device_mode": "desktop"
  }' \
  http://localhost:8080/api/book

# Check status
curl -u admin:password http://localhost:8080/api/status
```

---

## 🧪 Testing

The project uses pytest with comprehensive test coverage across all modules.

### Test Summary

**75 tests total:**
- **66 unit tests** (fast, no browser) - 2.7s
- **9 integration tests** (requires browser) - 18.4s

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run only unit tests (fast, no browser needed):**
```bash
pytest -m unit
```

**Run only integration tests (requires browser and credentials):**
```bash
pytest -m integration
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest tests/test_api.py
pytest tests/test_utils.py
pytest tests/test_models.py
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Pytest fixtures and configuration
├── test_api.py                    # FastAPI endpoint tests (12 tests)
├── test_booker.py                 # PadelBooker class tests (11 tests)
├── test_device_modes.py           # Integration tests for mobile/desktop (11 tests)
├── test_exceptions.py             # Custom exception tests (6 tests)
├── test_models.py                 # Pydantic model tests (10 tests)
├── test_navigation_strategy.py    # Navigation strategy tests (9 tests)
└── test_utils.py                  # Utility function tests (16 tests)
```

### Test Coverage by Module

- **api.py**: Endpoint authentication, booking flow, status checks
- **booker.py**: Initialization, slot finding, player selection, context manager
- **models.py**: Pydantic validation, device mode, field requirements
- **utils.py**: Driver setup, logging, authentication, booking enabled flag
- **navigation_strategy.py**: Mobile/desktop strategies, factory pattern
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

**CI Workflow** (runs on PRs and main branch):
- **Lint**: Code formatting check with black
- **Unit Tests**: Fast tests without browser (66 tests, ~3s)
- **Integration Tests**: Full browser tests (9 tests, ~20s)
- **Test Summary**: Aggregated results

**Docker Workflow** (runs on PRs and main branch):
- **Build**: Verify Docker image builds successfully
- **Test**: Run unit tests inside Docker container

### Required Secrets

For integration tests to run in CI, configure these GitHub secrets:
- `BOOKER_USERNAME`: Booking platform username
- `BOOKER_PASSWORD`: Booking platform password

**Note**: Integration tests are automatically skipped if credentials are not configured.

### Branch Protection

Recommended branch protection rules for `main`:
- ✅ Require pull request reviews
- ✅ Require status checks (CI, Docker Build)
- ✅ Require branches to be up to date

---

## 🤝 Contributing

Pull requests and suggestions are welcome! Please open an issue to discuss your ideas or report bugs.

**All PRs will automatically run:**
- Code formatting checks (black)
- Unit tests (66 tests)
- Integration tests (9 tests, if credentials configured)
- Docker build verification

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

