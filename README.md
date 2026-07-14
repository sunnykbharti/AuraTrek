# 📦 AuraTrek — Technical Management & Expedition Roster Platform

AuraTrek is a modern, decoupled Single Page Application (SPA) designed to manage trek routes, staff dashboards, and user rosters. The application utilizes a high-performance microservices architecture featuring an asynchronous background processing engine, reactive data states, and automated email reporting pipelines.

---

## 🛠️ Project Architecture & Organization

The repository follows a clean, decoupled structure separating the backend API service layers from the modular frontend client:

*   **`backend/`**: Core API suite built with a micro-framework structure.
    *   `routes/`: Houses independent routing blueprinted controllers (e.g., `user_py`, `admin.py`).
    *   `models.py`: Defines relational schemas and primary/foreign key mappings using an ORM layer.
    *   `tasks.py`: Contains asynchronous worker task loops and messaging functions.
*   **`frontend/`**: Decoupled Client application built with Vue.js 3.
    *   `src/views/`: Contains page dashboard layouts (e.g., Admin, Staff, and User portals).
    *   `src/components/`: Reusable reactive UI components.
    *   `src/stores/`: Dynamic Pinia configuration modules for managing persistent user sessions.

---

## 💻 Technical Stack Ecosystem

| Layer Component | Technology / Library | Core Purpose & Utility |
| :--- | :--- | :--- |
| **Frontend Framework** | Vue.js 3 | Renders a modular, reactive, and component-based Single Page Application (SPA) user interface. |
| **State Management** | Pinia | Manages persistent global state, authentication tokens, and user sessions across frontend routes. |
| **Build Tool & Bundler** | Vite | Provides a modern frontend build tool for rapid hot-reloading and lightning-fast asset bundling. |
| **Backend Framework** | Flask (Python) | Serves as the core micro-framework to build the RESTful API endpoints and backend request-handling logic. |
| **Database ORM Layer** | Flask-SQLAlchemy | Maps database structures to Python objects (ORM) for secure, seamless SQL database queries and management. |
| **Async Task Engine** | Celery | Offloads heavy, time-consuming operations like dynamic file compilations into the background as asynchronous jobs. |
| **Message Broker** | Redis | Acts as an in-memory message broker to handle communications and route queues between Flask and Celery. |
| **Authentication Module** | PyJWT | Secures API communication by issuing and validating cryptographically signed JSON Web Tokens for role-based access. |
| **Server Cache Layer** | Flask-Caching | Lowers server load and decreases database access latency by storing frequently requested data profiles in an active server cache. |

---

## 🚀 Key Features

### 1. Core Platform Features (Default)
*   **Role-Based Security Protocols**: Implemented via `PyJWT` strings. Client states are evaluated through local storage keys, and specific endpoint methods are wrapped with custom `@user_required` route decorators.
*   **Relational Database Mapping**: Managed via `Flask-SQLAlchemy` utilizing linked primary/foreign keys across `Users`, `Trekker`, `Staff`, and `Treks` datasets with automatic cascade deletions (`cascade="all, delete-orphan"`).
*   **Interactive Operational Panels**: Independent portals designed for users to apply for expeditions, and specialized workflows for staff profiles to inspect assigned rosters.

### 2. Advanced Performance Features (Additional)
*   **Non-Blocking Asynchronous Background Tasks**: Resource-heavy actions, such as compiling dataset matrices into physical `.csv` archives, are managed through non-blocking asynchronous calls via `Celery` workers using `Redis`.
*   **Automated Verification Despatch**: Integrates a file generation workflow that instantly pairs background export results with an internal mailer pipeline to attach compiled data sheets to the target recipient's address.
*   **Server-Side Latency Optimization**: Employs an abstract cache framework via `Flask-Caching` to store static schema structures, reducing redundant database hits.

---

## 🛠️ Local Development Installation Setup

### Prerequisite Checklist
*   Python 3.10+
*   Node.js (v18+)
*   Redis Server (Running locally)

### 1. Backend API Configuration Setup
Navigate to the backend application module directory and instantiate a clean environment:
```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 app.py (mac)
```

### 2. Frontend 
```bash
cd frontend
npm install
npm run dev
```

### 3. Redis
```bash
cd backend
brew services restart redis
```

### 4. Celery
```bash
cd backend
source env/bin/activate
celery -A app.celery_app worker --pool=solo --loglevel=info
```

### 5. Celery beat
```bash
cd backend
source env/bin/activate
celery -A app.celery_app beat --loglevel=info
```

##📊 Database Schema Relationships
The underlying application architecture handles data bindings using the following relationship constraints:
Staff managers assign tracking metrics to individual entries inside the Treks metadata logs (Many-to-One).
Registrations and status changes are captured dynamically through the unified mapping table TrekApplications.