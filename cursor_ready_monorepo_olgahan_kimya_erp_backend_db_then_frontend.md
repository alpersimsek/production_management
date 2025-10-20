# Cursor‑Ready Monorepo — Demo Kimya ERP

Aşağıdaki içerik **Cursor** ile otomasyon için hazırdır. Önce **Backend & DB** (tam dosya ağacı ve içerikleri), ardından **Frontend** bölümü gelir. Kopyala‑yapıştırla dosyaları oluşturabilir veya Cursor’a topluca uygulatabilirsin.

> Yığın: FastAPI + SQLAlchemy + Alembic + PostgreSQL + Celery/Redis | Vue 3 + Vite + Pinia + Vuetify

---

## 0) Kök Dizin Yapısı
```
demo-erp/
  backend/
  frontend/
  docker-compose.yml
  README.md
```

---

# I) Backend & DB

## 1) Docker ve Servisler (DB/Redis/API/Worker/Flower)

**`docker-compose.yml` (kök)**
```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: demo
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: demo
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7
    ports: ["6379:6379"]

  api:
    build: ./backend
    env_file: ./backend/.env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    ports: ["8000:8000"]
    volumes:
      - ./backend:/app

  worker:
    build: ./backend
    command: ["celery", "-A", "app.celery_app:celery", "worker", "--loglevel=info"]
    env_file: ./backend/.env
    depends_on:
      - api
      - redis
    volumes:
      - ./backend:/app

  flower:
    image: mher/flower:1.2.0
    command: ["flower", "--port=5555", "--broker=redis://redis:6379/0"]
    ports: ["5555:5555"]
    depends_on:
      - redis

volumes:
  pgdata:
```

**`backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`backend/requirements.txt`**
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
SQLAlchemy==2.0.35
psycopg[binary]==3.2.1
alembic==1.13.2
pydantic==2.9.2
python-multipart==0.0.9
passlib[bcrypt]==1.7.4
PyJWT==2.9.0
celery==5.4.0
redis==5.0.7
python-slugify==8.0.4
```

**`backend/.env`**
```dotenv
DATABASE_URL=postgresql+psycopg://demo:demo@db:5432/demo
JWT_SECRET=change_me
JWT_EXPIRES_MIN=60
REFRESH_EXPIRES_MIN=1440
REDIS_URL=redis://redis:6379/0
ENV=dev
```

## 2) Backend Kaynak Ağacı
```
backend/
  app/
    __init__.py
    main.py
    config.py
    db.py
    celery_app.py
    security/
      __init__.py
      auth.py
      rbac.py
    models/
      __init__.py
      base.py
      user.py
      settings.py
      product.py
      order.py
      production.py
      warehouse.py
      shipment.py
      attachment.py
    routers/
      __init__.py
      auth.py
      settings.py
      orders.py
      production.py
      lots.py
      packaging.py
      warehouse.py
      shipments.py
      analytics.py
    schemas/
      __init__.py
      auth.py
      common.py
      order.py
  alembic/
    env.py
    script.py.mako
    versions/
  requirements.txt
  Dockerfile
  .env
```

## 3) Çekirdek Kodlar

**`app/config.py`**
```python
from pydantic import BaseModel
import os

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change_me")
    JWT_EXPIRES_MIN: int = int(os.getenv("JWT_EXPIRES_MIN", "60"))
    REFRESH_EXPIRES_MIN: int = int(os.getenv("REFRESH_EXPIRES_MIN", "1440"))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
```

**`app/db.py`**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`app/main.py`**
```python
from fastapi import FastAPI
from .routers import auth, settings as settings_router, orders, production, lots, packaging, warehouse, shipments, analytics

app = FastAPI(title="Demo Kimya ERP API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(settings_router.router, prefix="/settings", tags=["settings"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(production.router, prefix="/production-jobs", tags=["production"])
app.include_router(lots.router, prefix="/lots", tags=["lots"])
app.include_router(packaging.router, prefix="/packaging", tags=["packaging"])
app.include_router(warehouse.router, prefix="/warehouses", tags=["warehouses"])
app.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
```

**`app/celery_app.py`**
```python
from celery import Celery
from .config import settings

celery = Celery(
    "demo",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

@celery.task
def optimize_image(attachment_id: int):
    return {"status": "ok", "attachment_id": attachment_id}
```

### 3.1 Modeller (özet)

**`models/base.py`**
```python
from ..db import Base
```

**`models/user.py`**
```python
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    permissions = Column(JSONB, nullable=False, server_default='{}')

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

**`models/settings.py`**
```python
from sqlalchemy import Column, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from ..db import Base

class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(Text, unique=True, nullable=False)
    value = Column(JSONB, nullable=False)
```

> Diğer tablolar Alembic migration’da oluşur; istersen SQLAlchemy modellerini de ekleyebiliriz.

### 3.2 Router Örnekleri

**`routers/auth.py`** (iskelet)
```python
from fastapi import APIRouter
router = APIRouter()

@router.post('/login')
async def login():
    return {"access":"FAKE","refresh":"FAKE"}
```

**`routers/settings.py`** (fire eşiği/termin/depo ayarları için placeholder)
```python
from fastapi import APIRouter
router = APIRouter()

@router.get('/fire-thresholds')
async def get_fire_thresholds():
    return {
        "poset": {"level1_percent": 3, "level1_kg": 15, "level2_percent": 6, "level2_kg": 30},
        "deterjan": {"level1_percent": 2, "level1_kg": 10, "level2_percent": 4, "level2_kg": 20}
    }
```

## 4) Alembic Kurulum ve İlk Migration

**`backend/alembic/env.py`**
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config import settings
from app.db import Base

config = context.config
if config.get_main_option('sqlalchemy.url', default=None) is None:
    config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**`backend/alembic/script.py.mako`** (standart)
```mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = ${repr(down_revision)}
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
```

**İlk migration (özet) —** `backend/alembic/versions/20251013_0001_init.py`  
> (Önceden verdiğimiz migration’ın birebir sürümü; burada tekrar etmiyoruz. Cursor’a o dosyayı da eklet.)

## 5) Seed Script (Admin, Depolar, Fire Eşikleri)

**`backend/seed.py`**
```python
import json
from sqlalchemy import text
from app.db import engine

DEFAULT_SETTINGS = {
  "fire_thresholds": {
    "poset": {"level1_percent": 3, "level1_kg": 15, "level2_percent": 6, "level2_kg": 30},
    "deterjan": {"level1_percent": 2, "level1_kg": 10, "level2_percent": 4, "level2_kg": 20}
  },
  "termin": {"minimum_days": 7},
  "warehouses": [
    {"code": "MERKEZ", "name": "Merkez Depo"},
    {"code": "YAN", "name": "Yan Depo"}
  ]
}

with engine.begin() as conn:
    # roles
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"admin"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"manager"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"operator"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"packaging"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"warehouse"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"sales"})

    # admin user (şifre hash’i örnek, prod’da değiştir)
    conn.execute(text("""
      INSERT INTO users (full_name,email,password_hash,role_id)
      VALUES ('Admin','admin@local','$2b$12$2r8Q0z2b1f1r5W1ZQbE1A.3n8cKjQ1p6Z/2tps7H3Sxh0bW3oXl9u',
              (SELECT id FROM roles WHERE name='admin'))
      ON CONFLICT (email) DO NOTHING
    """))

    # settings
    for k,v in DEFAULT_SETTINGS.items():
        conn.execute(text("INSERT INTO settings (key,value) VALUES (:k, :v) ON CONFLICT (key) DO UPDATE SET value=:v"), {"k":k, "v":json.dumps(v)})

    # warehouses
    for wh in DEFAULT_SETTINGS["warehouses"]:
        conn.execute(text("INSERT INTO warehouses (code,name) VALUES (:c,:n) ON CONFLICT (code) DO NOTHING"), {"c": wh["code"], "n": wh["name"]})

print("Seed completed")
```

## 6) Çalıştırma
```bash
# 1) Servisleri kaldır
docker compose up -d db redis

# 2) Alembic
docker compose exec api alembic upgrade head

# 3) Seed
docker compose exec api python seed.py

# 4) API
open http://localhost:8000/docs
```

---

# II) Frontend (Vue 3 + Vite + Pinia + Vuetify)

## 1) Paketler ve Vite

**`frontend/package.json`**
```json
{
  "name": "demo-erp-frontend",
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview --port 5173"
  },
  "dependencies": {
    "pinia": "^2.1.7",
    "vue": "^3.5.10",
    "vue-router": "^4.4.5",
    "vuetify": "^3.7.2",
    "jwt-decode": "^4.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "vite": "^5.4.8",
    "sass": "^1.79.4",
    "sass-embedded": "^1.79.4",
    "typescript": "^5.6.2"
  }
}
```

**`frontend/vite.config.ts`**
```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') }
  },
  server: { host: true, port: 5173 }
})
```

## 2) Kaynak Ağacı
```
frontend/
  src/
    main.ts
    App.vue
    plugins/vuetify.ts
    router/
      index.ts
      guards.ts
    store/
      auth.ts
    layouts/
      DefaultLayout.vue
    pages/
      Login.vue
      Orders.vue
```

## 3) Çekirdek Kodlar

**`src/main.ts`**
```ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'

createApp(App).use(createPinia()).use(router).use(vuetify).mount('#app')
```

**`src/App.vue`**
```vue
<template>
  <v-app>
    <router-view />
  </v-app>
</template>
```

**`src/plugins/vuetify.ts`**
```ts
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
export default createVuetify({})
```

**`src/router/guards.ts`**
```ts
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/store/auth'

export function authGuard(to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return next({ name: 'login', query: { redirect: to.fullPath } })
  next()
}

export function roleGuard(roles: string[]) {
  return (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) return next({ name: 'login' })
    if (!roles.includes(auth.user?.role ?? '')) return next({ name: 'orders' })
    next()
  }
}
```

**`src/router/index.ts`**
```ts
import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const Login = () => import('@/pages/Login.vue')
const Orders = () => import('@/pages/Orders.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      beforeEnter: authGuard,
      children: [
        { path: '', redirect: { name: 'orders' } },
        { path: 'orders', name: 'orders', component: Orders },
      ]
    },
  ]
})

export default router
```

**`src/store/auth.ts`**
```ts
import { defineStore } from 'pinia'
import jwtDecode from 'jwt-decode'

interface User { id: number; name: string; role: string }
interface Tokens { access: string; refresh: string }

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null as User | null, tokens: null as Tokens | null }),
  getters: { isAuthenticated: (s) => !!s.tokens?.access },
  actions: {
    login(tokens: Tokens) {
      this.tokens = tokens
      const payload: any = jwtDecode(tokens.access)
      this.user = { id: payload.sub, name: payload.name, role: payload.role }
    },
    logout() { this.tokens = null; this.user = null }
  }
})
```

**`src/layouts/DefaultLayout.vue`**
```vue
<template>
  <v-app>
    <v-app-bar app flat>
      <v-toolbar-title>Demo ERP</v-toolbar-title>
      <v-spacer />
      <v-btn to="/orders" variant="text">Sipariş</v-btn>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
```

**`src/pages/Login.vue`**
```vue
<template>
  <v-container class="py-10" style="max-width:420px">
    <v-card>
      <v-card-title>Giriş</v-card-title>
      <v-card-text>
        <v-text-field v-model="email" label="E-posta" />
        <v-text-field v-model="password" label="Şifre" type="password" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="doLogin" :loading="loading">Giriş</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const email = ref('admin@local')
const password = ref('admin')
const loading = ref(false)

async function doLogin(){
  loading.value = true
  // TODO: API çağrısı; şimdilik sahte token
  auth.login({ access: 'FAKE.JWT', refresh: 'FAKE.REFRESH' })
  loading.value = false
}
</script>
```

**`src/pages/Orders.vue`**
```vue
<template>
  <v-container>
    <v-toolbar flat>
      <v-text-field v-model="q" label="Ara" density="comfortable" />
      <v-spacer/>
      <v-btn>Yeni Sipariş</v-btn>
    </v-toolbar>
    <v-data-table :items="items" :headers="headers" />
  </v-container>
</template>
<script setup lang="ts">
import { ref } from 'vue'
const q = ref('')
const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Müşteri', key: 'customer' },
  { title: 'Termin', key: 'due' },
  { title: 'Durum', key: 'status' },
]
const items: any[] = []
</script>
```

## 4) Çalıştırma
```bash
# Backend/DB zaten ayakta: db + api + redis
# Frontend
cd frontend
npm i
npm run dev
open http://localhost:5173
```

---

Hepsi bu. Cursor’a "monorepoyu oluştur, dosyaları bu içerikle yaz ve docker compose’u çalıştır" şeklinde komut vererek tek seferde kurabilirsin. Sonraki adımda istersen **Auth (JWT) gerçek akış**, **Settings API** ve **Operatör/Paket/Depo** akışlarının endpoint + sayfa bağlamalarını ekleyeyim.



---

## III) VSCode — Full‑Stack F5 Debug (Hot Reload) for Cursor

> Aşağıdaki `.vscode/launch.json` ve `.vscode/tasks.json` dosyalarını **kök dizine** ekle. Tek tuşla (**F5**) tüm stack başlar; debug oturumunu durdurduğunda Docker altyapısı otomatik kapanır. Hot‑reload FastAPI ve Vue için aktif, Celery’de breakpoint destekli.

### 1) `.vscode/launch.json`
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI (uvicorn, hot‑reload)",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "jinja": true,
      "console": "integratedTerminal",
      "preLaunchTask": "Start Infrastructure (db+redis+flower)",
      "postDebugTask": "Stop Infrastructure"
    },
    {
      "name": "Celery Worker (debug)",
      "type": "python",
      "request": "launch",
      "module": "celery",
      "args": ["-A", "app.celery_app:celery", "worker", "--loglevel=info"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env",
      "console": "integratedTerminal",
      "postDebugTask": "Stop Infrastructure"
    },
    {
      "name": "Vue Dev Server (HMR)",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/frontend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev", "--", "--host"],
      "port": 5173,
      "console": "integratedTerminal",
      "postDebugTask": "Stop Infrastructure"
    }
  ],
  "compounds": [
    {
      "name": "Full Stack — Start All (F5)",
      "configurations": [
        "FastAPI (uvicorn, hot‑reload)",
        "Celery Worker (debug)",
        "Vue Dev Server (HMR)"
      ],
      "stopAll": true
    },
    {
      "name": "Full Stack — Stop All",
      "configurations": [
        "FastAPI (uvicorn, hot‑reload)"
      ],
      "preLaunchTask": "Stop Infrastructure"
    }
  ]
}
```

### 2) `.vscode/tasks.json`
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Infrastructure (db+redis+flower)",
      "type": "shell",
      "command": "docker compose up -d db redis flower",
      "problemMatcher": []
    },
    {
      "label": "Stop Infrastructure",
      "type": "shell",
      "command": "docker compose down",
      "problemMatcher": []
    }
  ]
}
```

### 3) Cursor’a vereceğin kısa talimat (kopyala‑yapıştır)
```
1) Kök dizinde `.vscode/launch.json` ve `.vscode/tasks.json` dosyalarını aşağıdaki içerikle oluştur.
2) `docker compose up -d db redis` komutunu çalıştırmana gerek yok; F5 öncesi otomatik yapılacak.
3) Cursor’da Run and Debug menüsünden **Full Stack — Start All (F5)** seç ve F5’e bas.
4) API (8000) ve Vue (5173) hot‑reload ile çalışır; Celery breakpoint’leri destekler.
5) Durdurmak için debug oturumunu **Stop** et (Shift+F5). Docker altyapısı otomatik kapanır.
6) Alternatif olarak **Full Stack — Stop All** compound’unu çalıştırarak docker’ı manuel kapatabilirsin.
```

> Notlar:
> - Frontend’in API adresi `.env` veya `VITE_API_URL` üzerinden `http://localhost:8000` olmalı.
> - İlk kurulumda migration ve seed için: `docker compose up -d db redis` → `docker compose up -d api` → `docker compose exec api alembic upgrade head` → `docker compose exec api python seed.py`. Sonraki çalıştırmalarda F5 akışı yeterlidir.



---

## IV) Frontend — TypeScript yerine **JavaScript** kullanımı (Cursor‑Ready)
Aşağıdaki değişikliklerle frontend’i tamamen **JS** (Typescript’siz) çalıştırabilirsiniz.

### 1) Paketler
**`frontend/package.json` (JS sürümü)**
```json
{
  "name": "demo-erp-frontend",
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview --port 5173"
  },
  "dependencies": {
    "pinia": "^2.1.7",
    "vue": "^3.5.10",
    "vue-router": "^4.4.5",
    "vuetify": "^3.7.2",
    "jwt-decode": "^4.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "vite": "^5.4.8",
    "sass": "^1.79.4",
    "sass-embedded": "^1.79.4"
  }
}
```
> Not: `typescript` devDependency’sini kaldırdık.

### 2) Vite yapılandırması
**`frontend/vite.config.js`**
```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: { host: true, port: 5173 }
})
```

### 3) Kaynak dosyalarını JS’e çevirin
Dizin yapısı aynı, sadece `.ts` → `.js` ve `<script setup>` bloklarında `lang="ts"` kaldırılıyor.
```
frontend/
  src/
    main.js
    App.vue
    plugins/vuetify.js
    router/
      index.js
      guards.js
    store/
      auth.js
    layouts/
      DefaultLayout.vue
    pages/
      Login.vue
      Orders.vue
```

**`src/main.js`**
```js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'

createApp(App).use(createPinia()).use(router).use(vuetify).mount('#app')
```

**`src/plugins/vuetify.js`**
```js
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
export default createVuetify({})
```

**`src/router/guards.js`**
```js
import { useAuthStore } from '@/store/auth'

export function authGuard(to, from, next) {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return next({ name: 'login', query: { redirect: to.fullPath } })
  next()
}

export function roleGuard(roles) {
  return (to, from, next) => {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) return next({ name: 'login' })
    if (!roles.includes(auth.user?.role ?? '')) return next({ name: 'orders' })
    next()
  }
}
```

**`src/router/index.js`**
```js
import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const Login = () => import('@/pages/Login.vue')
const Orders = () => import('@/pages/Orders.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      beforeEnter: authGuard,
      children: [
        { path: '', redirect: { name: 'orders' } },
        { path: 'orders', name: 'orders', component: Orders },
      ]
    },
  ]
})

export default router
```

**`src/store/auth.js`**
```js
import { defineStore } from 'pinia'
import jwtDecode from 'jwt-decode'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    tokens: null,
  }),
  getters: {
    isAuthenticated: (s) => !!(s.tokens && s.tokens.access),
  },
  actions: {
    login(tokens) {
      this.tokens = tokens
      try {
        const payload = jwtDecode(tokens.access)
        this.user = { id: payload.sub, name: payload.name, role: payload.role }
      } catch (e) {
        this.user = { id: 1, name: 'Dev', role: 'admin' }
      }
    },
    logout() {
      this.tokens = null
      this.user = null
    },
  }
})
```

**`src/pages/Login.vue`**
```vue
<template>
  <v-container class="py-10" style="max-width:420px">
    <v-card>
      <v-card-title>Giriş</v-card-title>
      <v-card-text>
        <v-text-field v-model="email" label="E-posta" />
        <v-text-field v-model="password" label="Şifre" type="password" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="doLogin" :loading="loading">Giriş</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>
<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const email = ref('admin@local')
const password = ref('admin')
const loading = ref(false)

async function doLogin(){
  loading.value = true
  // TODO: API çağrısı; şimdilik sahte token
  auth.login({ access: 'FAKE.JWT', refresh: 'FAKE.REFRESH' })
  loading.value = false
}
</script>
```

**`src/pages/Orders.vue`**
```vue
<template>
  <v-container>
    <v-toolbar flat>
      <v-text-field v-model="q" label="Ara" density="comfortable" />
      <v-spacer/>
      <v-btn>Yeni Sipariş</v-btn>
    </v-toolbar>
    <v-data-table :items="items" :headers="headers" />
  </v-container>
</template>
<script setup>
import { ref } from 'vue'
const q = ref('')
const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Müşteri', key: 'customer' },
  { title: 'Termin', key: 'due' },
  { title: 'Durum', key: 'status' },
]
const items = []
</script>
```

### 4) Cursor’a vereceğin JS talimatı (kopyala‑yapıştır)
```
Frontend’i TypeScript yerine JavaScript kullanacak şekilde dönüştür:
1) `frontend/package.json` içeriğini JS sürümüyle değiştir; `typescript` bağımlılığını kaldır.
2) `frontend/vite.config.ts` dosyasını `vite.config.js` olarak yeniden oluştur (JS içeriğiyle).
3) `src` altındaki tüm `.ts` dosyalarını `.js` olarak değiştir ve `<script setup lang="ts">` -> `<script setup>` yap.
4) Aşağıdaki dosyaları JS içerikleriyle oluştur/güncelle:
   - `src/main.js`, `src/plugins/vuetify.js`
   - `src/router/index.js`, `src/router/guards.js`
   - `src/store/auth.js`
   - `src/pages/Login.vue`, `src/pages/Orders.vue`
5) `npm i` çalıştır ve `npm run dev` ile başlat.
```

> Not: VSCode F5/compound debug ayarları değişmez; Node hedefi JS ile de aynen çalışır.

