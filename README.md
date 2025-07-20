# 🎾 padel-booker

Automated padel court booking API for Sportclub Houten, powered by FastAPI and Selenium.

---

## 🚀 Features

- **RESTful API** for automated court booking
- **Basic Authentication** for secure access
- **Background processing** for booking operations
- Smart slot and player selection with rotation and error handling
- Configurable booking date, time, duration, and player list
- Headless browser automation (no UI required)
- **Docker support** for easy deployment
- Comprehensive logging and error reporting

---

## 📦 Project Structure

```
padel-booker/
├── data/
│   └── config.json         # Booking configuration (date, time, players, etc.)
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
     -e BOOKER_FIRST_NAME="Your Name" \
     -e PLAYER_CANDIDATES="Player 1,Player 2,Player 3" \
     padel-booker
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
- `BOOKER_FIRST_NAME`: Your first name for booking
- `PLAYER_CANDIDATES`: Comma-separated list of player names
- `API_USERNAME`: Username for API authentication  
- `API_PASSWORD`: Password for API authentication

**Example:**
```bash
export API_USERNAME="admin"
export API_PASSWORD="secure_password"
export BOOKER_FIRST_NAME="John"
export PLAYER_CANDIDATES="John Smith,Jane Doe,Mike Johnson,Sarah Wilson"
```

### Booking Configuration

The API uses `data/config.json` for booking settings:

```json
{
  "login_url": "https://houten.baanreserveren.nl/",
  "booking_date": "2025-07-24",
  "start_time": "21:30",
  "duration_hours": 1.5
}
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

#### 📋 Get Configuration
```bash
GET /api/config
Authorization: Basic base64(username:password)
```
```json
{
  "login_url": "https://houten.baanreserveren.nl/",
  "booking_date": "2025-07-24",
  "start_time": "21:30",
  "duration_hours": 1.5
}
```

#### ⚙️ Update Configuration
```bash
POST /api/config
Authorization: Basic base64(username:password)
Content-Type: application/json

{
  "login_url": "https://houten.baanreserveren.nl/",
  "booking_date": "2025-07-25",
  "start_time": "20:00",
  "duration_hours": 2.0
}
```

#### 🎾 Start Booking
```bash
POST /api/book
Authorization: Basic base64(username:password)
Content-Type: application/json

{
  "username": "your_club_username",
  "password": "your_club_password"
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
    "players": ["John Smith", "John"]
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

# Get config
curl -u admin:password http://localhost:8080/api/config

# Start booking
curl -u admin:password \
  -H "Content-Type: application/json" \
  -d '{"username":"club_user","password":"club_pass"}' \
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
