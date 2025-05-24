

Teams : 
								
| S.No | Category       | Team     | Member 1     | Member 2  | Member 3     | Member 4     |
|------|----------------|----------|--------------|-----------|--------------|--------------|
| 1    | Document       | Team 1   | Sahiti       | Lokesh    | Srujan       | Vedin        |
| 2    | Medicine       | Team 2   | Sandeep      | Yuvaraj   | Sateesh      |              |
| 3    | Package        | Team 3   | Guru         | Sanchit   | Bharat       |              |
| 4    | UI/UX          | Team 4   | Amrita       | Amruth    | Sri Lakshmi  |              |
| 5    | Github/DevOPS  | Team 5   | Sahiti       | Sri Lakshmi|             |              |




  Here is a **clean, structured, and well-worded Markdown document** for your project setup and planning steps. This version is ideal for sharing in a project README or onboarding doc:

---

# 🚀 PMB Portal Setup & Team Kickoff Guide

This guide will help you and your team get set up with the development environment and begin planning for the **PMB Portal** project.

---

## ✅ Development Environment Setup

1. ### 🔗 GitHub Account & Access

   * Create a GitHub account (if you don’t already have one).
   * Share your GitHub username with the team lead.
   * Get added as a **collaborator** to the project repository.

2. ### 💻 Install Visual Studio Code

   * Download and install [VS Code](https://code.visualstudio.com/).
   * Recommended extensions: Python, GitLens, Jinja.

3. ### 🛢️ Install MariaDB and MySQL Client

   * Install [MariaDB](https://mariadb.org/download/) for your database server.
   * Ensure you have the **MySQL client** installed for CLI access.

4. ### 🐬 Install DBeaver (Database GUI)

   * Download and install [DBeaver](https://dbeaver.io/) to interact with databases visually.

5. ### 🐍 Install Latest Versions of Python & Node.js

   * Python 3.10 or later recommended: [Download here](https://www.python.org/)
   * Node.js LTS version: [Download here](https://nodejs.org/)

6. ### 🧪 Set Up Virtual Environment (virtualenv)

   * Create a virtual environment for project isolation:

     ```bash
     python -m venv env
     source env/bin/activate  # On Windows: .\env\Scripts\activate
     ```

7. ### 📦 Install Django & Database Packages

   ```bash
   pip install django mysqlclient
   ```

---

## 🛠️ Project Setup

8. ### 🌐 Create Django Project

   * Start a new Django project named `pmb_hello`:

     ```bash
     django-admin startproject pmb_hello
     ```

9. ### 🧩 Create Django App: `category`

   * Inside the project, create an app called `category`:

     ```bash
     python manage.py startapp category
     ```
   * Create a **dummy table** in the database (e.g., `Category`) and connect it using Django models.

10. ### 🖼️ Create Jinja Template for Frontend

* Use Jinja templates to display category documentation.
* Example documentation: **Shipping Requirements & Processes**

11. ### 📦 Add Shipping Logic (Views)

* Implement a simple shipping calculator in `views.py`.
* Inputs:

  * Source PIN code (India)
  * Destination ZIP code (USA)
  * Package weight
* Output: Estimated shipping price

---

## 💡 Team Brainstorming & Research

12. ### 🧠 Collaboration & Research Plan

Begin collecting real-world data and ideas:

#### a) 📞 How can the team gather requirements?

* Research online
* Call/email/chat with existing shipping carriers (e.g., DHL, FedEx, Blue Dart)

#### b) 📈 How are logistics companies generating leads?

* SEO
* Paid ads
* Partner networks
* Website lead forms

#### c) 🌐 What information is publicly accessible on carrier websites?

* Rate calculators
* Branch locators
* Transit time estimators
* Documentation checklists

#### d) 🏢 How to locate a branch for a given source PIN code?

* Look up branch locators from known carrier APIs or websites
* Store mapping of PIN code to branch in your database

#### e) 🧾 How to structure & store all this information efficiently?

* Plan your database schema to support:

  * Branch data
  * Lead records
  * Serviceable ZIP/PIN codes
  * Pricing logic
  * User-submitted inquiries

---

Let me know if you'd like this as a downloadable `.md` file or to turn this into a shared onboarding wiki page for your team.
