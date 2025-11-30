# Architecture Documentation

## System Overview

ELI5.ai follows a **client-server architecture** with clear separation of concerns between frontend presentation and backend API logic.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User's Browser                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Frontend (Static HTML/CSS/JS)                         │  │
│  │  - Responsive UI                                       │  │
│  │  - Input validation                                    │  │
│  │  - API communication                                   │  │
│  └───────────────────┬────────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │ HTTPS
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                    Backend API (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  API Layer                                             │  │
│  │  - Request validation (Pydantic)                       │  │
│  │  - CORS handling                                       │  │
│  │  - Error handling                                      │  │
│  └───────────────────┬────────────────────────────────────┘  │
│                      │                                        │
│  ┌───────────────────▼────────────────────────────────────┐  │
│  │  Business Logic                                        │  │
│  │  - Complexity-based prompt engineering                │  │
│  │  - Token limit enforcement                            │  │
│  │  - Response formatting                                │  │
│  └───────────────────┬────────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────┘
                         │ HTTPS
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                      OpenAI API                               │
│  - GPT-4o-mini model                                          │
│  - Token-based billing                                        │
│  - Completion endpoint                                        │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Frontend (Static Site)

**Technology**: Vanilla HTML5, CSS3, JavaScript (ES6+)

**Responsibilities**:

- User interface rendering
- Input collection and client-side validation
- Complexity level selection
- API request formation
- Response display and formatting
- Error handling and user feedback

**Key Files**:

- `index.html` - Single-page application
- Inline CSS - Styling and responsive design
- Inline JavaScript - Business logic and API calls

**Why No Build Process?**

- Simple application doesn't need bundling
- Faster development iteration
- Smaller final size (<50KB)
- No dependency management overhead

---

### Backend (FastAPI Service)

**Technology**: Python 3.11, FastAPI, Uvicorn

**Responsibilities**:

- REST API endpoints
- Request validation
- OpenAI API integration
- Token limit enforcement
- Error handling
- CORS configuration

**Key Files**:

```
backend/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── .env                # Environment variables (not in git)
```

**API Endpoints**:

| Endpoint   | Method | Purpose                   |
| ---------- | ------ | ------------------------- |
| `/`        | GET    | Health check and API info |
| `/health`  | GET    | Service health status     |
| `/explain` | POST   | Main explanation endpoint |

---

## Data Flow

### Request Flow

```
1. User Input
   └─> Client-side validation
       └─> Fetch API call to backend
           └─> FastAPI receives request
               └─> Pydantic validates payload
                   └─> Construct prompt with complexity config
                       └─> OpenAI API call with token limit
                           └─> Receive AI response
                               └─> Format and return to frontend
                                   └─> Display to user
```

### Request/Response Schema

**Request** (`/explain`):

```json
{
  "topic": "string",
  "complexity": "eli5" | "eli10" | "teen" | "college" | "expert"
}
```

**Response**:

```json
{
  "success": true,
  "topic": "string",
  "complexity": "string",
  "explanation": "string",
  "tokens_used": 150,
  "model": "GPT-4o-mini",
  "cost": "$0.000225"
}
```

---

## Complexity Configuration System

Each complexity level has:

- **Custom system prompt** - Tailored to audience level
- **Token limit** - Cost control
- **Temperature** - Creativity control

```python
{
    "eli5": {
        "instruction": "Explain in 2-3 short sentences...",
        "max_tokens": 150,
        "temperature": 0.7
    },
    "expert": {
        "instruction": "Provide technical explanation...",
        "max_tokens": 350,
        "temperature": 0.5
    }
}
```

**Design Rationale**:

- Lower temperature for expert (more precise)
- Higher tokens for complex topics
- Clear instruction differences ensure distinct outputs

---

## Deployment Architecture

### Development Environment

```
Docker Compose
├── Backend Container (Python:3.11)
│   ├── Port 8000
│   └── Volume mounted source code
├── Frontend Container (Nginx:alpine)
│   ├── Port 3000 (mapped to 80)
│   └── Static file serving
└── Shared Network
    └── Docker bridge network
```

### Production Environment (Render.com)

```
Backend Service
├── Auto-deploy from GitHub main branch
├── Environment: Python 3
├── Build: pip install -r requirements.txt
├── Start: python main.py
└── Port: 8000 (auto-assigned)

Frontend Service
├── Auto-deploy from GitHub main branch
├── Type: Static Site
├── Build: None (static files)
└── CDN: Render's CDN
```

---

## Security Architecture

### Current Implementation

**1. API Key Protection**

- Stored in environment variables
- Never committed to repository
- Accessed via `os.getenv()`

**2. CORS Configuration**

```python
allow_origins=["*"]  # Production should be specific
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**3. Input Validation**

- Pydantic models enforce types
- String sanitization
- Length limits (implicit via token limits)

**4. Error Handling**

- Generic error messages to client
- Detailed logging server-side
- No stack trace exposure

### Future Security Enhancements

**Phase 1** (If >1K requests/day):

- IP-based rate limiting (slowapi)
- Specific CORS origins
- Request logging

**Phase 2** (If >10K requests/day):

- Redis-backed distributed rate limiting
- Cloudflare proxy (DDoS protection)
- API key authentication
- Usage monitoring

**Phase 3** (If production with users):

- JWT authentication
- User account system
- Usage quotas per user
- Payment integration

---

## Cost Management Architecture

### Token Limiting Strategy

**Problem**: OpenAI charges per token, costs can spiral

**Solution**: Hard token limits per complexity level

```python
MAX_TOKENS = {
    "eli5": 150,    # Simple = short
    "college": 300, # Moderate detail
    "expert": 350   # Technical = more tokens needed
}
```

**Impact**:

- Predictable costs per request
- Budget protection
- Still provides quality responses

### Cost Breakdown

| Complexity | Avg Tokens | Cost/Request | $5 Budget Gets   |
| ---------- | ---------- | ------------ | ---------------- |
| ELI5       | 150        | $0.000225    | ~22,000 requests |
| College    | 300        | $0.000450    | ~11,000 requests |
| Expert     | 350        | $0.000525    | ~9,500 requests  |

**Overall Average**: ~$0.0004 per request = **12,500 requests per $5**

---

## Scaling Strategy

### Current State (0-100 req/day)

- **Hosting**: Render free tier
- **Caching**: None
- **Database**: None
- **Rate limiting**: None
- **Cost**: $0/month + API usage

### Scale Level 1 (100-1,000 req/day)

- **Hosting**: Render paid ($7/month - no sleep)
- **Caching**: In-memory (FastAPI middleware)
- **Rate limiting**: Simple (slowapi)
- **Cost**: ~$10/month

### Scale Level 2 (1K-10K req/day)

- **Hosting**: Render Pro ($25/month)
- **Caching**: Redis ($10/month)
- **Database**: PostgreSQL (usage tracking)
- **Rate limiting**: Distributed (Redis)
- **CDN**: Cloudflare (free tier)
- **Cost**: ~$50/month

### Scale Level 3 (10K-100K req/day)

- **Hosting**: Multiple instances + load balancer
- **Caching**: Multi-region Redis
- **Database**: Managed PostgreSQL
- **Rate limiting**: Advanced (per-user quotas)
- **CDN**: Cloudflare Pro
- **Monitoring**: Datadog/Sentry
- **Cost**: ~$200-500/month

### Scale Level 4 (100K+ req/day)

- **Container Orchestration**: Kubernetes (GKE/EKS)
- **Multi-region deployment**
- **Advanced caching strategies**
- **Dedicated support**
- **Cost**: $1,000+/month

**Key Principle**: Scale infrastructure when metrics justify it, not based on potential future needs.

---

## Design Decisions & Trade-offs

### Why FastAPI?

**Pros**:

- Fast (async support)
- Automatic API docs
- Type safety
- Modern Python

**Cons**:

- Newer ecosystem vs Flask
- Requires async understanding

**Decision**: Pros outweigh cons for modern API

---

### Why Vanilla JS?

**Pros**:

- No build process
- Smaller bundle
- Faster load times
- Learning value

**Cons**:

- Manual DOM manipulation
- No component reusability
- Less structure for large apps

**Decision**: Appropriate for single-page simple UI

---

### Why NOT Kubernetes?

**Reality Check**:

- Current traffic: <100 req/day
- K8s minimum cost: $50-200/month
- Management overhead: significant
- Value provided: none at this scale

**When to reconsider**:

- Traffic > 10K req/day
- Multi-region needed
- High availability requirements
- Team has K8s expertise

**Lesson**: Right tool for the job, not most advanced tool

---

## Monitoring & Observability

### Current (Minimal)

- Render's built-in logs
- FastAPI console output
- No structured logging
- No metrics collection

### Recommended (If scaling)

- **Logging**: Structured JSON logs
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Alerts**: PagerDuty/Opsgenie
- **Costs**: ~$20-50/month

**When to implement**: When downtime costs more than monitoring costs

---

## Testing Strategy

### Current State

- Manual testing
- No automated tests
- Browser-based validation

### Production-Ready Testing

- **Unit tests**: pytest for backend logic
- **Integration tests**: API endpoint testing
- **E2E tests**: Playwright/Cypress
- **Load tests**: Locust for performance

**Why not implemented yet**: Portfolio project scope, manual testing sufficient for current scale

---

## Disaster Recovery

### Current Backups

- Code: GitHub (version controlled)
- Environment: .env documented in README
- No data persistence needed (stateless)

### If User Data Added

- Daily database backups
- Point-in-time recovery
- Backup retention: 30 days
- Recovery time objective (RTO): <4 hours

---

## Future Architecture Considerations

### If Adding User Accounts

```
Frontend → API Gateway → Auth Service → Backend API
                            ↓
                        User Database
```

### If Adding Caching

```
Request → API → Check Cache → Return if hit
                     ↓
                  Miss? → OpenAI → Cache result → Return
```

### If Multi-Region

```
User → DNS (Geo-routing) → Closest Region
                              ↓
                         Regional Backend
                              ↓
                         Shared Cache Layer
                              ↓
                         OpenAI API
```

---

## Lessons Learned

1. **Start simple, scale when needed**
2. **Cost awareness from day one**
3. **Documentation is as important as code**
4. **Over-engineering hurts more than helps**
5. **Make decisions based on data, not hype**

---

**Last Updated**: 30th November 2025
**Author**: Kethoju Hari Vardhan
