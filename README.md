# Demo Kimya ERP

A comprehensive ERP system for chemical production management built with FastAPI + PostgreSQL + Vue 3.

## Tech Stack

**Backend:** FastAPI + SQLAlchemy + Alembic + PostgreSQL + Celery/Redis  
**Frontend:** Vue 3 + Vite + Pinia + Vuetify

## Quick Start

### Database Setup
```bash
cd backend
python reset_db.py      # Reset database schema
python minimal_seed.py  # Create admin user only
```

### Login
- **Email**: admin@demo.com
- **Password**: admin123

### Add Data
- All users, customers, products, etc. are added through the frontend
- No mock data - everything is created via the UI

### Docker Setup (Alternative)
1. Start infrastructure services:
```bash
docker compose up -d db redis
```

2. Run migrations and seed data:
```bash
docker compose exec api alembic upgrade head
docker compose exec api python minimal_seed.py
```

3. Start all services:
```bash
docker compose up -d
```

4. Access the applications:
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Flower (Celery monitoring): http://localhost:5556

## Development

Use F5 in VSCode to start the full stack with hot reload and debugging support.

## Default Login

- **Email**: admin@demo.com
- **Password**: admin123
