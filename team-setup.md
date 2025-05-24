

Teams : 
								
| S.No | Category       | Team     | Member 1     | Member 2  | Member 3     | Member 4     |
|------|----------------|----------|--------------|-----------|--------------|--------------|
| 1    | Document  shipping     | Team 1   | Sahiti       | Lokesh    | Srujan       | Vedin        |
| 2    | Medicine  shipping    | Team 2   | Sandeep      | Yuvaraj   | Sateesh      |              |
| 3    | Package  shipping      | Team 3   | Guru         | Sanchit   | Bharat       |              |
| 4    | UI/UX  Design        | Team 4   | Amrita       | Amruth    | Sri Lakshmi  |              |
| 5    | Github/DevOPS  | Team 5   | Sahiti       | Sri Lakshmi|             |              |





# 🚀 PMB Portal Setup & Team Kickoff Guide

This guide helps you prepare your development environment and begin collaborative work on the **PMB Portal** project.

---

## ✅ Development Environment Setup

1. ### 🔗 GitHub Account & Access

   * Create a GitHub account (if needed).
   * Share your GitHub username to be added as a **collaborator** on the repository.

2. ### 💻 Install Visual Studio Code

   * Download and install [VS Code](https://code.visualstudio.com/).
   * Recommended extensions: Python, GitLens, Jinja.

3. ### 🐋 Install Docker & Learn Fundamentals

   * Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
   * Learn core Docker concepts:

     * Containers vs. Images
     * Basic commands (`docker build`, `docker run`, `docker-compose`)
   * Helpful guide: [Docker Getting Started](https://docs.docker.com/get-started/)

4. ### 🛢️ Install MariaDB and MySQL Client

   * Install [MariaDB](https://mariadb.org/download/) for backend database.
   * Ensure **MySQL client** is also installed for command-line access.

5. ### 🐬 Install DBeaver (Database GUI)

   * Use [DBeaver](https://dbeaver.io/) for easy database management and inspection.

6. ### 🐍 Install Latest Python & Node.js

   * Install Python 3.10 or newer: [Python Downloads](https://www.python.org/)
   * Install Node.js (LTS): [Node.js Downloads](https://nodejs.org/)

7. ### 🧪 Set Up Python Virtual Environment

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   ```

8. ### 📦 Install Django & DB Packages

   ```bash
   pip install django mysqlclient
   ```

---

## 🛠️ Project Setup Tasks

1. ### 🌐 Create Django Project

   * Start the project named `pmb_hello`:

     ```bash
     django-admin startproject pmb_hello
     ```

2. ### 🧩 Create Django App: `category`

   * Navigate into the project folder:

     ```bash
     python manage.py startapp category
     ```
   * Define a **dummy model** (e.g., `Category`) and apply migrations to your DB.

3. ### 🖼️ Build Jinja Template for Frontend

   * Display content related to the `category` model.
   * Example use case: “Document shipping requirements and processes.”

4. ### 📦 Implement Shipping Logic in `views.py`

   * Handle the following inputs:

     * **Source PIN code** (India)
     * **Destination ZIP code** (USA)
     * **Package weight**
   * Output: A calculated shipping price using simple business logic.

---

## 💡 Team Brainstorming & Research

1. ### 🧠 Requirement Gathering

   * How will the team gather shipping/logistics data?

     * Research online
     * Call or email carriers
     * Use web chat or support channels

2. ### 📈 Lead Generation Strategies

   * How do companies get new clients?

     * Website lead forms
     * Digital ads
     * SEO and content

3. ### 🌐 Explore Competitor Websites

   * What info can you access?

     * Branch locators
     * Pricing tools
     * Delivery timelines
     * Documentation requirements

4. ### 🏢 Branch Lookup by PIN Code

   * Investigate how to map source PIN codes to nearest branches.
   * Use APIs or maintain your own mapping in the DB.

5. ### 🧾 Data Structuring & Storage

   * Plan how to store:

     * Branch data
     * ZIP/PIN code mappings
     * Lead information
     * Documentation and pricing rules


