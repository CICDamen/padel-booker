# 🎾 padel-booker

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
  "player_candidates": ["John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson"]
}
```

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

## 🤝 Contributing

Pull requests and suggestions are welcome! Please open an issue to discuss your ideas or report bugs.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
