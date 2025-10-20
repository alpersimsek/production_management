# Database Setup for Demo Kimya ERP

## 🗄️ Database Management Scripts

### 1. Reset Database Schema
```bash
cd backend
python reset_db.py
```
- Drops all existing tables
- Creates fresh database schema
- Removes all data

### 2. Create Admin User
```bash
cd backend
python minimal_seed.py
```
- Creates essential roles (admin, manager, operator)
- Creates only admin user
- No mock data

### 3. Clean Database (Alternative)
```bash
cd backend
python clean_database.py
```
- Removes all data but keeps existing schema
- Use if you want to keep existing tables

## 🔑 Admin Login
- **Email**: admin@demo.com
- **Password**: admin123

## 📱 Frontend Data Entry
After running the scripts:
1. Login with admin credentials
2. Add all users through Settings page
3. Add all data through frontend interface
4. No mock data - everything from frontend!

## 🚀 Quick Setup
```bash
# 1. Reset database
python reset_db.py

# 2. Create admin
python minimal_seed.py

# 3. Start application
# Login with admin@demo.com / admin123
# Add everything from frontend!
```
