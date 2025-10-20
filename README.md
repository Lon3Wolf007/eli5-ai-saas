# ELI5.ai - AI-Powered Learning Assistant

A full-stack SaaS application that explains complex topics in simple, friendly language using AI.

## 🚀 Features

- **Multiple Complexity Levels**: From "Like I'm 5" to Expert explanations
- **AI-Powered**: Uses OpenAI GPT-4o-mini for intelligent responses
- **Beautiful UI**: Modern, responsive design with smooth animations
- **Dockerized**: Easy deployment with Docker Compose
- **RESTful API**: FastAPI backend with automatic documentation

## 🛠️ Tech Stack

**Backend:**

- FastAPI (Python)
- OpenAI API
- Pydantic for validation
- Uvicorn ASGI server

**Frontend:**

- HTML5/CSS3/JavaScript
- Responsive design
- Real-time API integration

**Infrastructure:**

- Docker & Docker Compose
- Nginx web server

## 🏃 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- OpenAI API key

### Setup

1. Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/eli5-ai-saas.git
cd eli5-ai-saas
```

2. Create `.env` file in root directory:

```bash
OPENAI_API_KEY=your_api_key_here
```

3. Run with Docker:

```bash
docker-compose up --build
```

4. Open your browser:

```
http://localhost:3000
```

## 📸 Screenshots

Coming soon!

## 🎯 Future Enhancements

- [ ] User authentication
- [ ] Save conversation history
- [ ] Rate limiting per user
- [ ] Analytics dashboard
- [ ] Kubernetes deployment configs

## 📝 License

MIT

## 👨‍💻 Author

Created as an advanced full-stack learning project showcasing modern DevOps practices.
