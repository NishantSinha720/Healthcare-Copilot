# Healthcare Copilot

**Healthcare Copilot** is a full-stack healthcare management platform built by **Nishant Sinha**, combining production-oriented software engineering with practical AI integration.

The platform provides secure healthcare management APIs, authentication and authorization, appointment management, medical records, prescriptions, document processing, background jobs, real-time notifications, audit logging, and AI-powered document search and assistance.

The primary focus of the project is **software engineering and backend architecture**, with AI integrated as a practical product capability.

---

## 👨‍💻 Author

**Nishant Sinha**

GitHub: [NishantSinha720](https://github.com/NishantSinha720)

---

# 🎯 Project Focus

Healthcare Copilot is designed to demonstrate how a modern software product can integrate AI without making the entire application dependent on AI.

### Primary focus

* Backend engineering
* REST API development
* Authentication and authorization
* Database design
* Business logic
* Asynchronous processing
* Real-time communication
* Security
* Testing
* Containerization
* CI/CD

### AI integration

* Retrieval-Augmented Generation
* Semantic search
* Embeddings
* FAISS
* Local LLM inference
* AI agents
* Tool calling
* Human confirmation for sensitive actions

---

# 🏗️ Architecture

```text
                         React + TypeScript
                                │
                                ▼
                             Nginx
                                │
                                ▼
                    Django REST Framework
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
      MySQL                   Redis                  AI Layer
        │                       │                        │
        │                 ┌─────┴─────┐           ┌──────┴──────┐
        │                 ▼           ▼           ▼             ▼
        │              Celery     Channels      RAG          AI Agent
        │                 │           │           │             │
        │                 ▼           ▼           ▼             ▼
        │          Background     WebSocket     FAISS         Tools
        │          Processing                    │             │
        │                                       ▼             ▼
        │                                     Ollama      Permission
        │                                                   Checks
        │
        └────────────────────────────────────────────────────────
```

---

# 🚀 Features

## 🔐 Authentication & Authorization

* JWT authentication
* Access and refresh tokens
* Refresh-token rotation
* Refresh-token blacklisting
* Custom Django User model
* Role-Based Access Control
* Protected REST APIs
* Object-level authorization
* Organization-level access control
* Password hashing
* Secure production configuration

Supported roles:

```text
ADMIN
DOCTOR
PATIENT
```

Public registration cannot escalate a user to an administrative role.

---

# 🏥 Healthcare Management

## Organizations

Healthcare organizations represent hospitals and clinics.

Each organization can contain doctors and patients.

---

## Doctors

Doctor profiles support:

* Specialization
* Organization association
* Doctor-patient relationships

---

## Patients

Patient profiles support:

* Organization association
* Blood group
* Healthcare relationships

---

## Appointments

The appointment system supports:

* Appointment creation
* Appointment retrieval
* Appointment updates
* Appointment cancellation
* Status management
* Double-booking prevention
* Role-based access

---

## Medical Records

Medical records contain:

* Diagnosis
* Symptoms
* Treatment
* Clinical notes
* Record date
* Doctor
* Patient
* Organization

Patients cannot directly create medical records.

---

## Prescriptions

Prescriptions contain:

* Medication
* Dosage
* Frequency
* Duration
* Instructions
* Doctor
* Patient
* Medical record
* Organization

---

# 🌐 REST API

The core application is built using **Django REST Framework**.

Healthcare Copilot exposes RESTful APIs for:

* Authentication
* Users
* Organizations
* Doctors
* Patients
* Doctor-patient relationships
* Appointments
* Medical records
* Prescriptions
* Documents
* AI
* Notifications
* Auditing

Examples:

```text
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/me/

GET/POST /api/healthcare/appointments/
GET/POST /api/healthcare/medical-records/
GET/POST /api/healthcare/prescriptions/

GET/POST /api/documents/

POST /api/ai/ask/
POST /api/ai/agent/
POST /api/ai/agent/confirm/

GET /api/notifications/
GET /api/audit/
```

---

# 🤖 AI Integration

AI is integrated into the platform as a supporting software capability rather than replacing the core business logic.

The AI layer provides:

* Healthcare document search
* RAG-based question answering
* Local LLM inference
* AI agent workflows
* Tool calling
* Human confirmation

---

# 📄 Document Processing

The platform supports:

* PDF
* DOCX

Document processing pipeline:

```text
Upload
  ↓
Validation
  ↓
Database Metadata
  ↓
Celery
  ↓
Text Extraction
  ↓
Text Cleaning
  ↓
Chunking
  ↓
Embeddings
  ↓
FAISS
  ↓
READY
```

Libraries:

* PyMuPDF
* python-docx
* Sentence Transformers
* FAISS

---

# 🔎 RAG

The RAG system uses:

```text
all-MiniLM-L6-v2
        ↓
384-dimensional embeddings
        ↓
FAISS IndexFlatIP
```

Query flow:

```text
User Question
      ↓
Authentication
      ↓
Authorization
      ↓
Embedding
      ↓
FAISS Search
      ↓
Relevant Chunks
      ↓
Context
      ↓
Ollama
      ↓
Grounded Answer
```

Document retrieval is restricted according to the authenticated user's access scope.

---

# 🧠 Local LLM

The project uses **Ollama** for local AI inference.

Example:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama2:7b
```

This allows the AI functionality to run locally without requiring a paid external AI provider.

---

# 🧑‍💻 AI Agent

The AI agent can select application tools based on user requests.

Available tools include:

```text
search_medical_documents
get_my_appointments
get_my_medical_records
get_my_prescriptions
request_cancel_appointment
confirm_cancel_appointment
```

The agent does **not** directly access MySQL.

Instead:

```text
AI Agent
   ↓
Tool
   ↓
Permission Check
   ↓
Service Layer
   ↓
Django ORM
   ↓
MySQL
```

This keeps business logic and authorization under application control.

---

# ✋ Human-in-the-Loop

Sensitive actions require explicit user confirmation.

For example:

```text
User
 ↓
"Cancel my appointment"
 ↓
AI Agent
 ↓
Find appointment
 ↓
Request confirmation
 ↓
User confirms
 ↓
Confirmation endpoint
 ↓
Permission check
 ↓
Cancellation
```

This prevents the AI agent from silently performing sensitive operations.

---

# ⚡ Background Processing

Celery handles asynchronous operations.

Current background workflows include:

```text
process_document_task
create_notification_task
```

Redis is used as the Celery broker/result backend.

---

# 🔔 Real-Time Notifications

The application uses:

* Django Channels
* WebSockets
* Redis

WebSocket endpoint:

```text
/ws/notifications/?token=<JWT_ACCESS_TOKEN>
```

Notification flow:

```text
Application Event
      ↓
Celery
      ↓
Notification Database
      ↓
Redis Channel Layer
      ↓
WebSocket
      ↓
Frontend
```

---

# 📋 Audit Logging

Important application activity is recorded through an audit system.

Supported actions include:

```text
LOGIN
LOGOUT
CREATE
UPDATE
DELETE
VIEW
AI_QUERY
AI_ACTION
AI_CONFIRM
UPLOAD
CANCEL
```

Audit records can include:

* User
* Action
* Resource
* Resource ID
* Description
* IP address
* Metadata
* Timestamp

---

# 📚 API Documentation

OpenAPI schema is generated using **drf-spectacular**.

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI:

```text
http://127.0.0.1:8000/api/schema/
```

Docker/Nginx:

```text
http://127.0.0.1:8080/api/docs/
```

---

# 🧪 Testing

The project uses:

* pytest
* pytest-django

Test coverage includes:

* Authentication
* JWT protection
* RBAC
* Patient authorization
* Medical record permissions
* Prescription permissions
* Appointment access
* Audit authorization
* Notification ownership
* AI agent authentication
* AI agent confirmation
* Registration role escalation

Run:

```bash
pytest -q
```

Additional checks:

```bash
python manage.py check
```

```bash
python manage.py check --deploy
```

```bash
python manage.py makemigrations --check --dry-run
```

---

# 🐳 Docker

The project is containerized using Docker Compose.

Services:

```text
MySQL
Redis
Django
Celery
Nginx
```

Start:

```bash
docker compose up -d --build
```

Check:

```bash
docker compose ps
```

Logs:

```bash
docker compose logs -f web
```

Docker ports:

```text
MySQL  → localhost:3307
Redis  → localhost:6380
Nginx  → localhost:8080
Django → internal port 8000
```

Swagger through Nginx:

```text
http://127.0.0.1:8080/api/docs/
```

---

# 🔄 CI/CD

GitHub Actions validates the project automatically.

Pipeline:

```text
Checkout
   ↓
Python Setup
   ↓
Install Dependencies
   ↓
MySQL
   ↓
Redis
   ↓
Django Check
   ↓
Migration Check
   ↓
Migrations
   ↓
pytest
```

Workflow:

```text
.github/workflows/ci.yml
```

---

# 🛡️ Security Architecture

Security is implemented at multiple layers.

```text
Request
  ↓
JWT Authentication
  ↓
Role Check
  ↓
Object-Level Permission
  ↓
Organization / Patient Scope
  ↓
Service Layer
  ↓
Database
```

The AI agent follows the same security boundaries.

The LLM cannot bypass application authorization.

---

# 📁 Project Structure

```text
Healthcare-Copilot/
│
├── apps/
│   ├── accounts/
│   ├── healthcare/
│   ├── documents/
│   │   ├── services/
│   │   └── tasks/
│   ├── ai/
│   │   ├── services/
│   │   └── tools/
│   ├── notifications/
│   └── audit/
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── asgi.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
│
├── nginx/
│   └── nginx.conf
│
├── requirements/
│   └── base.txt
│
├── tests/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── manage.py
├── .env.example
├── .gitignore
└── README.md
```

---

# 🧰 Technology Stack

## Backend

* Python
* Django
* Django REST Framework
* SimpleJWT

## Database

* MySQL

## Async & Real-Time

* Redis
* Celery
* Django Channels
* WebSockets
* Daphne

## AI / ML

* Ollama
* Llama-family LLM
* Sentence Transformers
* FAISS
* RAG
* AI Agents
* Tool Calling

## Document Processing

* PyMuPDF
* python-docx

## Testing

* pytest
* pytest-django

## API Documentation

* OpenAPI
* Swagger UI
* drf-spectacular

## Frontend

* React
* TypeScript
* Vite

## DevOps

* Docker
* Docker Compose
* Nginx
* GitHub Actions

---

# ⚙️ Local Development

Clone:

```bash
git clone https://github.com/NishantSinha720/Healthcare-Copilot.git
cd Healthcare-Copilot
```

Create environment:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements/base.txt
```

Configure `.env` using `.env.example`.

Run migrations:

```bash
python manage.py migrate
```

Create administrator:

```bash
python manage.py createsuperuser
```

Start Django:

```bash
python manage.py runserver
```

Start Celery:

```bash
celery -A config.celery worker --loglevel=info --pool=solo
```

Start Redis separately or through Docker.

---

# 🧠 Ollama Setup

Install Ollama and download the configured model:

```bash
ollama pull llama2:7b
```

Start Ollama:

```bash
ollama serve
```

Verify:

```bash
ollama list
```

---

# 🎓 Engineering Concepts Demonstrated

Healthcare Copilot demonstrates practical experience with:

* Software architecture
* RESTful API design
* Django
* Django REST Framework
* Authentication
* Authorization
* RBAC
* Database modeling
* MySQL
* Redis
* Celery
* WebSockets
* Event-driven workflows
* File processing
* Background jobs
* Vector search
* RAG
* Embeddings
* Local LLM integration
* AI agents
* Tool calling
* Human-in-the-loop workflows
* Security
* Audit logging
* Automated testing
* API documentation
* Docker
* Nginx
* CI/CD
* React
* TypeScript

---

# 🚧 Project Status

Healthcare Copilot is being developed as an end-to-end portfolio application.

### Completed

* Core Django architecture
* REST API
* Authentication
* Authorization
* Healthcare domain
* Appointments
* Medical records
* Prescriptions
* Documents
* Celery
* Redis
* RAG
* FAISS
* Ollama
* AI agent
* Tool calling
* Human confirmation
* Notifications
* WebSockets
* Audit logging
* Swagger/OpenAPI
* Automated tests
* Docker
* Nginx
* CI/CD configuration

### Final Development

* React + TypeScript frontend
* Full frontend/backend integration
* End-to-end verification
* Final security inspection
* Deployment verification
* Portfolio cleanup

---

# ⚠️ Disclaimer

Healthcare Copilot is an educational and portfolio project.

It is **not a medical device** and does not replace professional medical advice, diagnosis, or treatment.

AI-generated information should be reviewed by an appropriately qualified healthcare professional before being used for clinical decisions.

---

# 📄 License

This project is currently intended for educational and portfolio purposes.

An appropriate open-source license can be added before public redistribution.

---

## Built by Nishant Sinha

Healthcare Copilot is a software-engineering-focused application demonstrating how modern backend systems can integrate AI, asynchronous processing, real-time communication, security, testing, and containerized deployment into a single product.
