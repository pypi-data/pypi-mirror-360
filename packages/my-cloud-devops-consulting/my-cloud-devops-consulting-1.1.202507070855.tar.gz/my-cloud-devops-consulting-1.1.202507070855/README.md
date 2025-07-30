# Project‑Root

A full‑stack web application with an **API‑driven Python backend**, a **static/templated frontend**, and complete **container/Kubernetes** deployment workflows.  
Security gates (Gitleaks) and CI/CD are handled through GitHub Actions.

---
##
crontab -e
#####



## Table of Contents
1. [Architecture](#architecture)
2. [Directory Layout](#directory-layout)
3. [Local Development](#local-development)
4. [Docker Usage](#docker-usage)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [CI/CD & Secret Scanning](#cicd--secret-scanning)
7. [Environment Variables](#environment-variables)
8. [Contributing](#contributing)
9. [License](#license)

---

## Architecture
```text
 ┌─────────────┐      HTTP      ┌──────────────┐
 │   Browser   │  ───────────▶ │  Flask API   │
 │  (frontend) │               │  (backend)   │
 └─────────────┘               └──────────────┘
        ▲                              │
        │ Static assets / Jinja        │
        └───────────────┬──────────────┘
                        ▼
                ┌──────────────┐
                │   Database   │
                └──────────────┘


### 🔧 Tech Stack at a Glance

| Layer | What We Use | Where It Lives |
|-------|-------------|----------------|
| **Frontend** | HTML • CSS • JavaScript | `static/`, `templates/` |
| **Backend** | Flask (`app.py`) | project root |
| **Container** | Docker (single image) | `Dockerfile` |
| **Orchestration** | Kubernetes manifests | `kubernetes/` |
| **Automation / CI · CD** | GitHub Actions | `.github/workflows/` |


# 1. Clone & install deps
git clone https://github.com/your-org/project-root.git
cd project-root
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Set env vars (see .env.example)
export FLASK_ENV=development
export SECRET_KEY=changeme
# …

# 3. Run the server
python app.py
# → http://localhost:5000



/etc/nginx/nginx.conf
#

#

####################################################
pending pod disk space
# See what images are present
clear
ctr -n k8s.io images list

# Remove unused containerd images (be cautious)
ctr -n k8s.io images prune

# Or for Docker users (if running Docker instead):
docker system prune -a
####################################################