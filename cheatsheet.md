
# 🛠️ Git + Docker Compose Cheat Sheet

## 🔀 Branching & PR Workflow

![Branching Commit Process](examples/branching-commit-process.png)

### 🌿 Feature Branch Workflow

```bash
# Start from latest main
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature_<name>

# Make changes
# Stage & commit
git add .
git commit -m "feat: <your feature description>"

# Push and raise PR
git push origin feature_<name>
# Go to GitHub/GitLab and create PR to `main`
```

### 🔄 Weekly Release Process

```bash
# From main branch
git checkout main
git pull origin main

# Create release branch
git checkout -b release-<YYYY-MM-DD>
git push origin release-<YYYY-MM-DD>

# Tag release (optional)
git tag v<version> -m "Release on <YYYY-MM-DD>"
git push origin v<version>
```

---

## 🐳 Docker Compose Commands

### 🚀 Run the Stack

```bash
docker-compose up         # Start all services
docker-compose up -d      # Start in detached mode
```

### 🧹 Clean & Rebuild

```bash
docker-compose down       # Stop and remove containers
docker-compose build      # Rebuild images
docker-compose up --build # Rebuild and run
```

### 🔍 Debugging & Logs

```bash
docker-compose logs               # View logs for all services
docker-compose logs <service>    # Logs for a specific service
docker-compose exec <service> sh # Shell into a container
```

### ⚙️ Useful Options

```bash
docker-compose ps         # List running services
docker-compose stop       # Stop services
docker-compose restart    # Restart services
```

---

## ✅ Best Practices

* Keep feature branches focused and short-lived.
* Rebase or pull main before pushing to avoid merge conflicts.
* Review PR thoroughly and ensure all checks pass.
* Use `.env` files to manage local configurations.
* Run `docker-compose down -v` to clear volumes if needed.

---

> 📌 Tip: Use `git status`, `git diff`, and `git log --oneline` frequently to stay in control of your changes.

---


---

## 🧪 Validate a PR in Your Local System

### 🔄 Pull the Latest Changes

![image](https://github.com/user-attachments/assets/b0f231e1-70b5-4a77-8229-128ed901162b)

#### Command:

```bash
git pull
```

Before validating a PR, ensure your local repository is up to date with the latest changes from `mainline` or your working branch.

> ✅ **Why this step?**  
> Keeping your local branch updated ensures there are no conflicts and that you’re testing the PR against the most recent codebase.

---

### 📥 Fetch the PR Branch Locally

![image](https://github.com/user-attachments/assets/61c2fb65-1970-4bdc-9966-514b4c535d00)

#### Command:

```bash
git fetch origin pull/(PR Tag Number [123])/head:your branch name
```

Replace : your branch name WITH your desired Branch Name.

> 🛠️ **Why this step?**  

> This command fetches the code from the PR and creates a new local branch (`Your Branch Name`) for you to test it. It allows you to isolate and test the PR without affecting your main branches.

---

### 🔀 Check and Switch to the Fetched Branch

![image](https://github.com/user-attachments/assets/c926739b-ee4f-4467-9367-c1a800e5ffc6)

#### Command:

```bash
git branch              # To confirm the branch was created
git switch your branch name
```

> 🔍 **Why switch branches?**  
> You must switch to the created PR branch locally so you can run the code and validate the changes made in that specific pull request.

---

### 🐳 Docker Compose – Clean Build & Run

![Screenshot 2025-07-05 092803](https://github.com/user-attachments/assets/24c59301-c710-4aee-a4ae-327fe85135ba)

#### Run the Docker Commands

```bash
docker-compose down        # Stop all running containers
docker-compose build       # Rebuild images with PR changes
docker-compose up          # Start services
```

> 🧼 **Why this step?**  
> Rebuilding ensures you’re testing the exact environment with the new PR changes, avoiding cached/stale builds.

Docker compose cheatsheet : https://devhints.io/docker-compose
Docker references for knowledge and trouble shooting:
  https://devhints.io/dockerfile
  https://docs.docker.com/reference/compose-file/
  https://github.com/docker/awesome-compose/tree/master/django
  DJANGO SAMPLE : https://github.com/docker/awesome-compose/tree/master/official-documentation-samples/django/
  REACT SAMPLE : https://github.com/docker/awesome-compose/tree/master/react-express-mysql
  WORDPRESS SAMPLE : https://github.com/docker/awesome-compose/tree/master/wordpress-mysql
---

### 🔎 Validate PR Changes in Browser

#### ⚛️ React Frontend:

```bash
http://localhost:3000
```
#### 🐍 Django Backend:

```bash
http://localhost:8000
```

Open your browser and go to the relevant local URLs to test the app behavior.

> 🧪 **What to test:**  
> - Ensure the **features added in the PR** work as expected  
> - Check **existing functionality** (like mainline pages) to confirm nothing is broken  
> - Look out for **console errors**, **style issues**, and **backend failures**

---

### ✅ If everything works smoothly:

Leave a positive comment on the PR confirming it’s been tested.

The PR owner can now **merge it into `mainline`**.

![image](https://github.com/user-attachments/assets/234cc032-4d2c-4f9e-b9b1-afaad2876bd6)

### ❌ If there are issues:

Add a comment describing the problem.

Optionally attach screenshots/logs to help the developer fix it.
