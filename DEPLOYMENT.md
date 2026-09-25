# LexGuard Production Deployment Guide

This guide provides step-by-step instructions for deploying the **LexGuard AI Legal Document Intelligence Platform** using the modern cloud stack:

- **Database**: [Supabase](https://supabase.com) or [Neon](https://neon.tech) (PostgreSQL 16 with `pgvector`)
- **Backend API**: [Render](https://render.com) or [Railway](https://railway.app) (FastAPI + Uvicorn)
- **Frontend App**: [Vercel](https://vercel.com) (Next.js 14 App Router)

---

## Architecture Overview

```
+---------------------------+       HTTPS API       +-------------------------------+
|  Next.js 14 Frontend      |  ==================>  |  FastAPI Backend Service      |
|  Hosted on Vercel         |                       |  Hosted on Render or Railway  |
|  (App Router + Stitch UI) |  <==================  |  (Python 3.11 + Uvicorn)      |
+---------------------------+     PDF/DOCX Stream   +-------------------------------+
                                                                    |
                                        +---------------------------+---------------------------+
                                        |                                                       |
                                        v                                                       v
                       +---------------------------------+                     +---------------------------------+
                       |  PostgreSQL 16 + pgvector       |                     |  Google Gemini 1.5 Flash AI     |
                       |  Hosted on Supabase or Neon     |                     |  text-embedding-004 (3,072-dim) |
                       |  VECTOR(3072) Cosine Distance   |                     |  Dual-Key Automated Failover    |
                       +---------------------------------+                     +---------------------------------+
```

---

## Step 1: Deploy Database (Supabase or Neon)

LexGuard requires PostgreSQL 15+ with the `pgvector` extension enabled for 3,072-dimensional embedding storage.

### Option A: Supabase (Recommended Free Tier)
1. Sign in to [Supabase](https://supabase.com) and click **New project**.
2. Set a name (e.g., `lexguard-db`) and generate a secure database password.
3. Once the database is provisioned, go to the **SQL Editor** in the left sidebar and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Navigate to **Project Settings** -> **Database** -> **Connection String**.
5. Copy the **URI** (Connection pooling URI on port `6543` or direct on `5432`):
   ```
   postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### Option B: Neon (Serverless Postgres)
1. Sign in to [Neon](https://neon.tech) and create a project (`lexguard-db`).
2. Open the **SQL Editor** in Neon and execute:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy your project connection string from the dashboard.

---

## Step 2: Deploy Backend API (Render or Railway)

### Option A: Render
1. Sign in to [Render](https://render.com) and click **New +** -> **Web Service**.
2. Connect your GitHub repository: `https://github.com/ayus1234/LexGuard`.
3. Configure service settings:
   - **Name**: `lexguard-backend`
   - **Region**: Choose the region closest to your database (e.g., US East / Oregon / Frankfurt).
   - **Root Directory**: `backend`
   - **Environment**: `Python 3` (or choose `Docker` to use the included `backend/Dockerfile`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Under **Environment Variables**, add the following:

   | Key | Value / Description |
   | :--- | :--- |
   | `APP_ENV` | `production` |
   | `DATABASE_URL` | Your Supabase or Neon PostgreSQL connection URI |
   | `GEMINI_API_KEY_PRIMARY` | Your primary Google Gemini API Key |
   | `GEMINI_API_KEY_FALLBACK` | Your backup Google Gemini API Key |
   | `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app,http://localhost:3000` |
   | `APP_URL` | `https://your-frontend.vercel.app` |

5. Click **Create Web Service**.
   - Render will build the environment, execute `alembic upgrade head` to apply all database tables, and start Uvicorn.
   - Note down your backend URL (e.g. `https://lexguard-backend.onrender.com`).

---

## Step 3: Deploy Frontend (Vercel)

1. Sign in to [Vercel](https://vercel.com) and click **Add New...** -> **Project**.
2. Import the Git repository: `https://github.com/ayus1234/LexGuard`.
3. Configure project settings:
   - **Framework Preset**: `Next.js` (automatically detected)
   - **Root Directory**: `./` (leave default)
   - **Build Command**: `npm run build` (leave default)
   - **Output Directory**: `.next` (leave default)
4. Under **Environment Variables**, add:

   | Key | Value |
   | :--- | :--- |
   | `NEXT_PUBLIC_API_BASE_URL` | `https://lexguard-backend.onrender.com` (Your deployed backend URL) |

5. Click **Deploy**.
   - Vercel will build and deploy the Next.js application in ~60 seconds.
   - You will receive your public URL: `https://lexguard.vercel.app`.

---

## Step 4: Finalize CORS Configuration

Once Vercel gives you your production frontend URL (e.g. `https://lexguard.vercel.app`):

1. Go back to your **Render** (or Railway) backend dashboard.
2. Update the `ALLOWED_ORIGINS` environment variable to include your actual Vercel URL:
   ```env
   ALLOWED_ORIGINS=https://lexguard.vercel.app,https://your-project.vercel.app,http://localhost:3000
   ```
3. Update `APP_URL`:
   ```env
   APP_URL=https://lexguard.vercel.app
   ```
4. Save and trigger a redeploy (or wait for the environment reload).

---

## Step 5: Verification & Health Check

Test that your live deployment is healthy and operational:

1. **Backend Health Probe**:
   Visit: `https://lexguard-backend.onrender.com/api/health`
   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "lexguard-backend",
     "version": "1.0.0",
     "database": {
       "connected": true,
       "vector_extension": true,
       "status": "healthy"
     }
   }
   ```

2. **Frontend Walkthrough**:
   - Open your Vercel URL in the browser.
   - Select any contract from the **Sample Library** (e.g., Enterprise SaaS MSA).
   - Verify the **Analysis Dossier**, **Vendor Tilt Gauge**, and **Clause Ledger**.
   - Test **Ask LexGuard** grounded Q&A with citation badges (§).
   - Test the binary downloads: **Export Executive Brief (PDF)** and **Export Word Checklist (.docx)**.
