# Cloud Deployment Guide - Smart Expense & Finance Tracker

This repository is fully configured for zero-friction cloud deployment. Follow any of the options below to go live.

---

## 1. Option A: Deploy on Render (Recommended - Free & Easy)

1. **Push your code to GitHub**:
   ```bash
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** > **Web Service**.
3. Connect your GitHub repository.
4. Render will automatically detect [`render.yaml`](render.yaml) or you can manually configure:
   - **Environment:** `Python` (or `Docker`)
   - **Build Command:** `pip install -r backend/requirements.txt && python backend/train_classifier.py`
   - **Start Command:** `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Your app will be live at `https://<service-name>.onrender.com`.

---

## 2. Option B: Deploy on Railway

1. Go to [Railway](https://railway.app/) and click **New Project**.
2. Select **Deploy from GitHub repo** and pick this repository.
3. Railway automatically detects the [`Dockerfile`](Dockerfile) or [`Procfile`](Procfile).
4. Go to **Settings** > **Generate Domain** to get a public URL (`https://<app>.up.railway.app`).

---

## 3. Option C: Deploy on Fly.io

1. Install Fly CLI:
   - Windows PowerShell: `iwr https://fly.io/install.ps1 -useb | iex`
2. Authenticate:
   ```bash
   fly auth login
   ```
3. Launch and deploy using the included [`fly.toml`](fly.toml):
   ```bash
   fly launch
   fly deploy
   ```

---

## 4. Option D: Run with Docker (Local or Any VPS)

1. Build the image:
   ```bash
   docker build -t smart-expense-tracker .
   ```
2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name expense-app smart-expense-tracker
   ```
3. Open your browser at `http://localhost:8000`.

---

## Environment Variables (Optional)

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `8000` | Port assigned dynamically by cloud providers |
| `DATABASE_URL` | Local SQLite | Connection string for external MySQL / PostgreSQL / SQLite |
| `DB_HOST` | `localhost` | MySQL host (when not using `DATABASE_URL`) |
| `DB_USER` | `root` | MySQL user |
| `DB_PASSWORD` | *(empty)* | MySQL password (leaves SQLite as default if empty) |
| `DB_NAME` | `finance_db` | MySQL database name |
