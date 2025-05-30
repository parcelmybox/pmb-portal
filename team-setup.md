
# Complete this course

CS50’s Web Programming with Python and JavaScript : https://cs50.harvard.edu/web/2020/



Teams : 
								
| S.No | Category       | Team     | Member 1     | Member 2  | Member 3     | Member 4     |
|------|----------------|----------|--------------|-----------|--------------|--------------|
| 1    | Document  shipping     | Team 1   | Sahithi       | Lokesh    | Srujan       | Vedin        |
| 2    | Medicine  shipping    | Team 2   | Sandeep      | Yuvaraj   | Sateesh      |              |
| 3    | Package  shipping      | Team 3   | Guru         | Sanchit   | Bharat       |              |
| 4    | UI/UX  Design        | Team 4   | Amrita       | Amruth    | Sri Lakshmi  |              |
| 5    | Github/DevOPS  | Team 5   | Sahithi       | Sri Lakshmi|             |              |
| 6   | Customer Portal  | Team 1  | Sahithi       | Lokesh    | Srujan       | Vedin        |
| 6   | Admin Portal  | Team 2,3 | Sandeep      | Yuvaraj   |  Guru         | Sanchit   | Bharat       | 






# 🚀 PMB Portal Setup & Team Kickoff Guide

This guide will help your team set up the development environment and begin designing the **PMB Portal** with scalability and mobile-readiness in mind.

---

## ✅ Development Environment Setup

1. ### 🔗 GitHub Account & Access

   * Create a GitHub account.
   * Share your username to be added as a **collaborator** on the project repository.
   * Github flow : https://docs.github.com/en/get-started/using-github/github-flow

2. ### 💻 Install Visual Studio Code

   * [Download VS Code](https://code.visualstudio.com/)
   * Recommended extensions: Python, GitLens, Jinja.

3. ### 🐋 Install Docker & Learn Fundamentals

   * [Install Docker](https://www.docker.com/products/docker-desktop/)
   * Learn basics: containers, images, and common commands.
   * Tutorial: [Docker Getting Started](https://docs.docker.com/get-started/)

4. ### 🛢️ Install MariaDB and MySQL Client

   * Backend: [MariaDB](https://mariadb.org/download/)
   * CLI: Install the **MySQL client**

5. ### 🐬 Install DBeaver (DB GUI)

   * [Download DBeaver](https://dbeaver.io/) for easier DB access

6. ### 🐍 Install Python & Node.js

   * Python 3.10+: [Python.org](https://www.python.org/)
   * Node.js (LTS): [Node.js Downloads](https://nodejs.org/)

7. ### 🧪 Set Up Python Virtual Environment

   ```bash
   python -m venv env
   source env/bin/activate  # Windows: .\env\Scripts\activate
   ```

8. ### 📦 Install Django & DB Packages

   ```bash
   pip install django mysqlclient
   ```

---

## 🛠️ Project Setup Tasks

1. ### 🌐 Create Django Project

   ```bash
   django-admin startproject pmb_hello
   ```

2. ### 🧩 Create Django App: `category`

   ```bash
   python manage.py startapp category
   ```

   * Create a dummy model (e.g., `Category`)
   * Apply migrations and connect with MariaDB
    
Set Up Your MariaDB Database
Start your MariaDB server, then log in using the MariaDB client:
 ```bash
mysql -u root -p
```
 ```bash
Create a database and user:

CREATE DATABASE pmb_db;
CREATE USER 'pmb_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON pmb_db.* TO 'pmb_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```
⚙️  Update settings.py in Django Project
In pmb_hello/settings.py, set the database configuration to use MariaDB:
 ```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pmb_db',
        'USER': 'pmb_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

🧩  Define Your Dummy Model
In category/models.py:
 ```bash
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
```
✅  Make Migrations and Migrate
In your terminal (with venv activated):
 ```bash
python manage.py makemigrations category
python manage.py migrate
```
If everything is configured correctly, Django will create the required tables in your MariaDB database.

🧪 Optional: Test It in Django Shell
 ```bash
python manage.py shell
```
Then run:
 ```bash
from category.models import Category
Category.objects.create(name="Test Category")
```
3. ### 🧠 Learn Responsive Design: Bootstrap or Tailwind CSS

   * Choose one CSS framework to design mobile-friendly templates:

     * [Bootstrap Docs](https://getbootstrap.com/)
     * [Tailwind Docs](https://tailwindcss.com/docs)
   * Apply responsive layouts in Jinja templates

4. ### 🖼️ Build Jinja Template

   * Use responsive layout to show documentation for categories
   * Example: shipping requirements, customs forms, etc.

5. ### 📦 Add Shipping Logic in `views.py`

   * Inputs: Source PIN (India), Destination ZIP (USA), Weight
   * Output: Estimated price (basic formula)

---

## 💡 Team Brainstorming & Research

1. ### 🔍 Requirement Gathering

   * Explore shipping workflows by:

     * Internet research
     * Phone/email/chat with logistics providers

2. ### 📈 Lead Generation Strategies

   * How do shipping companies get clients?

     * SEO, ads, website forms

3. ### 🌐 Explore Competitor Websites

   * Information to study:

     * Price estimators
     * Branch locators
     * Delivery timelines
     * Required documentation

4. ### 🏢 Locate Branches by PIN Code

   * Use APIs or static mapping for PIN → nearest branch

5. ### 🗂️ Data Structuring

   * Plan your DB schema:

     * Leads, categories, documents, shipping logic
     * Branches and service coverage


Optional references:
CS50’s Introduction to Artificial Intelligence with Python : https://cs50.harvard.edu/ai/2024/weeks/1/ 
CS50’s Introduction to Programming with Python : https://cs50.harvard.edu/python/2022/weeks/0/
Week 8 HTML, CSS, JavaScript : https://cs50.harvard.edu/x/2025/weeks/8/
Flask : https://cs50.harvard.edu/x/2025/shorts/flask/
Ajax: https://cs50.harvard.edu/x/2025/shorts/ajax/



