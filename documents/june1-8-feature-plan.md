Great! Here's a clear and structured **project bootstrap guide** for your **ParcelMyBox (PMB)** system using the following tech stack:

* **Backend**: Django (REST API)
* **Database**: MariaDB
* **Admin Pages**: Django with Jinja Templates
* **Customer Pages**: React SPA (Single Page App)
* **Layout**: Sidebar-based navigation

---

# 🚀 ParcelMyBox Project Bootstrap Guide

## 📦 Tech Stack Overview

| Layer       | Technology                     |
| ----------- | ------------------------------ |
| Backend API | Django (Django REST Framework) |
| Database    | MariaDB                        |
| Admin UI    | Django + Jinja Templates       |
| Customer UI | React + Tailwind (optional)    |
| Auth        | Token-based or JWT             |

---

## 🛠️ 1. Environment Setup

### Install Core Tools

```bash
# System packages
sudo apt install python3 python3-pip python3-venv mariadb-server nodejs npm

# Optional: Use nvm for Node version management
```

---

## 📁 2. Project Structure

```bash
parcelmybox/
├── backend/
│   ├── manage.py
│   ├── pmb/                    # Django Project
│   ├── core/                   # Main App (users, quotes, carriers)
│   ├── templates/              # Jinja Templates for Admin
│   └── static/                 # Admin static files
├── frontend/                   # React App
│   ├── public/
│   └── src/
└── requirements.txt
```

---

## 🧱 3. Backend (Django + MariaDB + Jinja)

### Step 1: Initialize Django

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework mysqlclient
django-admin startproject pmb .
python manage.py startapp core
```

### Step 2: Configure MariaDB

1. Create DB and user:

```sql
CREATE DATABASE parcelmybox;
CREATE USER 'pmbuser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON parcelmybox.* TO 'pmbuser'@'localhost';
```

2. Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'parcelmybox',
        'USER': 'pmbuser',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Step 3: Add Jinja Templates for Admin UI

In `settings.py`:

```python
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']
```

Create folder: `backend/templates/admin/`

Use `{% extends 'admin/base.html' %}` to create admin pages.

---

## 🌐 4. Frontend (React with Sidebar)

### Step 1: Create React App

```bash
cd ..
npx create-react-app frontend
cd frontend
npm install react-router-dom axios
```

### Step 2: Set Up Routing and Sidebar

#### File: `src/App.js`

```jsx
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Quote from './pages/Quote';
import Profile from './pages/Profile';

function App() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/quote" element={<Quote />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </div>
    </div>
  );
}
```

#### File: `src/components/Sidebar.js`

```jsx
import { Link } from 'react-router-dom';

export default function Sidebar() {
  return (
    <div className="w-64 h-screen bg-gray-800 text-white p-4 space-y-4">
      <h2 className="text-xl font-bold">ParcelMyBox</h2>
      <Link to="/">Dashboard</Link>
      <Link to="/quote">Request Quote</Link>
      <Link to="/profile">Profile</Link>
    </div>
  );
}
```

---

## 🔗 5. Django REST API

Install DRF:

```bash
pip install djangorestframework
```

In `settings.py`:

```python
INSTALLED_APPS += ['rest_framework', 'core']
```

### Example API: `views.py`

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def get_quote(request):
    return Response({"price": "₹2500", "carrier": "DHL"})
```

### URL Routing

```python
# backend/core/urls.py
from django.urls import path
from .views import get_quote

urlpatterns = [
    path('quote/', get_quote),
]

# backend/pmb/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls')),
]
```

---

## 🧪 6. Dev Run Commands

### Start Backend

```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Start Frontend

```bash
cd frontend
npm start
```

---

## ✅ 7. Navigation Layout (Customer React App)

**Sidebar Links:**

* Dashboard
* Request Quote
* Profile
* Track Shipment
* Support

---

## 📌 8. Optional Enhancements

* JWT or Token Auth using `djangorestframework-simplejwt`
* `.env` support for React + Django
* TailwindCSS in React for styling
* Docker for containerized dev

---

Let me know if you want a `docker-compose` setup, GitHub Actions CI pipeline, or production deployment steps!
