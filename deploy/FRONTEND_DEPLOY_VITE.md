# Frontend Deployment Plan: Vite + React on e2-micro VM

Deploy your **Vite + React + TypeScript** frontend on the same e2-micro VM as the backend. nginx serves the Vite build (`dist/`) + proxies API calls. No extra cost, no domain needed.

---

## Architecture

```
User Browser (http://34.74.106.149)
    ↓
nginx
    ├─ / → serves Vite build (dist/ folder)
    ├─ /api/* → proxies to Django backend
    └─ /admin/* → proxies to Django admin
```

Both frontend and backend run in the same docker-compose stack on the VM.

---

## Prerequisites (from backend setup)

You already have:
- ✅ VM IP: `34.74.106.149`
- ✅ SSH access: `ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149`
- ✅ Project path: `/opt/missions/app`
- ✅ Docker & docker-compose running
- ✅ Backend (Django) healthy on `missions_backend:8000`

---

## Critical: Vite Build Environment

Your `src/config/env.ts` reads `VITE_API_BASE_URL` at **build time**. You must set this to `/api` for production:

```bash
# In your React frontend project root
VITE_API_BASE_URL=/api npm run build
# NOT: npm run build (which falls back to http://127.0.0.1:9050/api)
```

This ensures your axios client hits nginx's `/api/` proxy, not a hardcoded localhost IP.

---

## Step-by-step Implementation

### **STEP 1: Update your React project**

Create `.env.production` in your React project root:

```env
VITE_API_BASE_URL=/api
```

This ensures production builds use relative `/api` paths.

---

### **STEP 2: Build locally with production env**

In your React project:

```bash
npm install  # if needed
VITE_API_BASE_URL=/api npm run build
# Creates dist/ folder with optimized static files
```

Verify the build completed:
```bash
ls -la dist/
# Should see index.html, assets/, etc.
```

---

### **STEP 3: Prepare deployment files**

In your React project root, you should have:
- ✅ `dist/` (build output)
- ✅ `.env.production` (created above)

Compress everything:

```bash
tar -czf frontend-build.tar.gz dist/
```

---

### **STEP 4: Copy to the VM**

From your React project directory:

```bash
scp -i ~/.ssh/missions_deploy frontend-build.tar.gz deployer@34.74.106.149:/tmp/
rm frontend-build.tar.gz
```

Also copy the backend repo's nginx config:

```bash
# From the BACKEND repo (missions_backend)
scp -i ~/.ssh/missions_deploy deploy/nginx-frontend-vite.conf deployer@34.74.106.149:/tmp/nginx.conf
```

Or if you're doing this from the frontend project, you can manually create the nginx config on the VM (see **Appendix: Manual nginx config**).

---

### **STEP 5: On the VM: Extract and update docker-compose**

SSH into the VM and prepare the stack:

```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app

# Extract React build
mkdir -p frontend
tar -xzf /tmp/frontend-build.tar.gz -C frontend/
# Now you have: /opt/missions/app/frontend/dist/

# Backup original nginx config
cp nginx.conf nginx.conf.backend-only

# Use the new nginx config for frontend + API
cp /tmp/nginx.conf nginx.conf

# Verify nginx config syntax
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t
EOF
```

---

### **STEP 6: Update docker-compose.yaml with volume mount**

The nginx service needs to mount the frontend build folder. SSH in and update `docker-compose.yaml`:

```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app

# Edit docker-compose.yaml
# Find the nginx service volumes section and add the frontend mount
# Current:
#   volumes:
#     - ./nginx.conf:/etc/nginx/nginx.conf:ro
#     - media_volume:/app/media
#     - static_volume:/app/static
#
# Change to:
#   volumes:
#     - ./nginx.conf:/etc/nginx/nginx.conf:ro
#     - ./frontend/dist:/app/frontend/dist:ro
#     - media_volume:/app/media
#     - static_volume:/app/static

# Quick way: use sed to add the volume
sed -i '/- \.\/nginx.conf/a\      - .\/frontend\/dist:\/app\/frontend\/dist:ro' docker-compose.yaml

# Verify the change:
grep -A 5 "nginx:" docker-compose.yaml
EOF
```

Or manually edit it. The key addition is:
```yaml
nginx:
  image: nginx:latest
  container_name: missions_nginx
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./frontend/dist:/app/frontend/dist:ro    # ← ADD THIS LINE
    - media_volume:/app/media
    - static_volume:/app/static
  depends_on:
    backend:
      condition: service_healthy
  restart: unless-stopped
```

---

### **STEP 7: Restart the stack**

```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app
docker compose restart nginx
sleep 10
docker compose ps
EOF
```

Verify nginx is up:
```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 "cd /opt/missions/app && docker logs missions_nginx | tail -15"
```

---

### **STEP 8: Test the frontend in browser**

Open: **http://34.74.106.149/**

You should see:
- ✅ React app loads (Vite build)
- ✅ No console errors
- ✅ Network tab shows `/api/...` requests (not to hardcoded IP)

Test an API call in browser console:
```javascript
fetch('/api/missions/')
  .then(r => r.json())
  .then(data => console.log(data))
```

---

## Continuous Updates (Every time you change the frontend)

Whenever you update your React app:

```bash
# Step 1: Build locally with production env
cd /path/to/your/react/project
VITE_API_BASE_URL=/api npm run build

# Step 2: Compress
tar -czf frontend-build.tar.gz dist/

# Step 3: Copy to VM
scp -i ~/.ssh/missions_deploy frontend-build.tar.gz deployer@34.74.106.149:/tmp/
rm frontend-build.tar.gz

# Step 4: Deploy on VM
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app
rm -rf frontend/dist
mkdir -p frontend
tar -xzf /tmp/frontend-build.tar.gz -C frontend/
docker compose restart nginx
sleep 5
docker logs missions_nginx | tail -5
EOF
```

---

## Automation: GitHub Actions (Optional)

If you want auto-deploy when you merge to `main` on your **frontend** repo:

Create `.github/workflows/deploy-frontend-vite.yaml` in your frontend repo:

```yaml
name: Deploy Frontend (Vite)

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Node
        uses: actions/setup-node@v4
        with:
          node-version: "18"
      
      - name: Install dependencies
        run: npm install
      
      - name: Build (production env)
        run: VITE_API_BASE_URL=/api npm run build
      
      - name: Compress dist
        run: tar -czf frontend-build.tar.gz dist/
      
      - name: Copy to VM
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          source: "frontend-build.tar.gz"
          target: "/tmp/"
      
      - name: Deploy on VM
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/missions/app
            rm -rf frontend/dist
            mkdir -p frontend
            tar -xzf /tmp/frontend-build.tar.gz -C frontend/
            docker compose restart nginx
            sleep 5
            docker logs missions_nginx | tail -5
```

Then add these secrets to your **frontend** repo (GitHub → Settings → Secrets):
- `HOST`: `34.74.106.149`
- `USERNAME`: `deployer`
- `SSH_PRIVATE_KEY`: contents of `~/.ssh/missions_deploy`

---

## Troubleshooting

**Q: React app loads but shows 404 or blank page**
- Check browser console for errors
- Verify nginx is serving from the right path: `ssh deployer@34.74.106.149 "ls -la /opt/missions/app/frontend/dist/"`
- Ensure volume mount is in docker-compose: `docker inspect missions_nginx | grep frontend`

**Q: API calls fail (404 or network error)**
- Check that `.env.production` has `VITE_API_BASE_URL=/api`
- Verify you built with `VITE_API_BASE_URL=/api npm run build`
- Check nginx config: `docker logs missions_nginx`
- Test backend directly: `curl http://34.74.106.149:9050/api/missions/` (should work)

**Q: nginx won't start after volume mount change**
- Check syntax: `docker run --rm -v /opt/missions/app/nginx.conf:/etc/nginx/nginx.conf nginx nginx -t`
- Check docker-compose syntax: `docker compose config -q`
- Check logs: `docker logs missions_nginx`

**Q: "dist folder not found" or 404 on every page**
- Verify extraction: `ssh deployer@34.74.106.149 "ls -la /opt/missions/app/frontend/dist/index.html"`
- Verify volume mount is active: `docker inspect missions_nginx | grep -A 5 Mounts`
- Restart nginx: `docker compose restart nginx`

**Q: Page refresh returns 404 (but / works)**
- This means React Router routing is broken
- Verify nginx config has `try_files $uri $uri/ /index.html;`
- Restart nginx after config change: `docker compose restart nginx`

---

## Summary

1. **Build locally** with `VITE_API_BASE_URL=/api npm run build` (production env)
2. **Compress dist/** and copy to VM
3. **Extract to /opt/missions/app/frontend/dist/**
4. **Update docker-compose.yaml** with volume mount (critical!)
5. **Update nginx.conf** to use `nginx-frontend-vite.conf`
6. **Restart nginx**
7. **Test at http://34.74.106.149/**

Every update: build → tar → scp → extract → restart nginx

---

## Appendix: Manual nginx config (if you don't have backend repo access)

If you're deploying from just the frontend repo, manually create the nginx config on the VM:

```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cat > /opt/missions/app/nginx.conf << 'CONFEOF'
user  nginx;
worker_processes  auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout  65;

    gzip on;
    gzip_types text/plain application/xml application/javascript application/json;
    gzip_min_length 256;

    upstream django_backend {
        server missions_backend:8000;
    }

    server {
        listen 80;
        server_name _;

        root /app/frontend/dist;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://django_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /admin/ {
            proxy_pass http://django_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            proxy_pass http://django_backend;
        }

        location /media/ {
            proxy_pass http://django_backend;
        }
    }
}
CONFEOF

# Verify
docker run --rm -v /opt/missions/app/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t
EOF
```

Then proceed from **STEP 6** onward.
