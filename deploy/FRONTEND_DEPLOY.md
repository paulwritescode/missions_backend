# Frontend Deployment Plan: React on e2-micro VM

Deploy your React frontend on the same e2-micro VM as the backend. nginx serves the React build + proxies API calls. No extra cost, no domain needed.

---

## Architecture

```
User Browser
    ↓
nginx (34.74.106.149:80)
    ├─ / → serves React build (static)
    └─ /api/* → proxies to Django backend (internal)
```

Both frontend and backend run in the same docker-compose stack. nginx routes traffic:
- `/` and `/static/*` → React app (from build folder)
- `/api/*` and `/admin/*` → Django backend container

---

## Prerequisites (from backend setup)

You already have:
- ✅ VM IP: `34.74.106.149`
- ✅ SSH access: `ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149`
- ✅ Project path: `/opt/missions/app`
- ✅ Docker & docker-compose running on the VM
- ✅ nginx configured as reverse proxy

---

## Step-by-step Implementation

### **1. Build your React app locally**

On your laptop, in your React frontend project:

```bash
npm run build
# Creates a `build/` folder with optimized static files
```

---

### **2. Create `nginx-frontend.conf` in your React project**

This tells nginx how to serve the React app + proxy API calls.

Create file: `nginx-frontend.conf`

```nginx
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

        # === React app (static files) ===
        root /app/frontend/build;

        # Handle React Router: any non-file request → index.html
        location / {
            try_files $uri $uri/ /index.html;
        }

        # === API calls: proxy to Django backend ===
        location /api/ {
            proxy_pass http://django_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # === Admin panel: proxy to Django ===
        location /admin/ {
            proxy_pass http://django_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # === Static files from backend (if any) ===
        location /static/ {
            proxy_pass http://django_backend;
        }

        # === Media uploads ===
        location /media/ {
            proxy_pass http://django_backend;
        }
    }
}
```

---

### **3. Update your React app's API base URL**

Make sure all API calls use **relative paths** (no hardcoded IP):

**Good:**
```javascript
// In your React app (e.g., api.js or services)
const API_BASE = '/api';  // or just fetch('/api/...')

fetch(`${API_BASE}/missions/`)
```

**Not good:**
```javascript
const API_BASE = 'http://34.74.106.149/api';  // ❌ hardcoded IP
```

If you have hardcoded URLs, search and replace:
```bash
# In your React project
grep -r "34.74.106.149" src/
grep -r "http://localhost:8000" src/  # if any dev URLs
```

Change them to relative paths: `/api/...`

---

### **4. Copy frontend build to the VM**

On your laptop, compress your React build and copy it:

```bash
# In your React project root (has build/ folder)
tar -czf build.tar.gz build/
scp -i ~/.ssh/missions_deploy build.tar.gz deployer@34.74.106.149:/tmp/
rm build.tar.gz

# Also copy the nginx config
scp -i ~/.ssh/missions_deploy nginx-frontend.conf deployer@34.74.106.149:/tmp/
```

---

### **5. On the VM: extract build and update nginx**

```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app

# Extract React build
mkdir -p frontend
tar -xzf /tmp/build.tar.gz -C frontend/
# Now you have: frontend/build/ with React static files

# Backup old nginx config
cp nginx.conf nginx.conf.backup

# Replace with frontend-aware config
cp /tmp/nginx-frontend.conf nginx.conf

# Verify nginx config syntax
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t
EOF
```

---

### **6. Restart nginx and the stack**

```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app
docker compose restart nginx
sleep 10
docker compose ps
EOF
```

Verify nginx is up and healthy:
```bash
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 "cd /opt/missions/app && docker logs missions_nginx | tail -10"
```

---

### **7. Test the frontend in a browser**

Open: **http://34.74.106.149/**

You should see:
- ✅ React app loads
- ✅ Console has no CORS errors
- ✅ API calls work (network tab shows `/api/...` requests)

Test an API call in browser console:
```javascript
fetch('/api/missions/')
  .then(r => r.json())
  .then(data => console.log(data))
```

---

## Continuous Updates

Every time you update the frontend, repeat steps 1–2–4–5–6:

```bash
# On your laptop (frontend project)
npm run build
scp -i ~/.ssh/missions_deploy -r build/ deployer@34.74.106.149:/tmp/

# On the VM
ssh -i ~/.ssh/missions_deploy deployer@34.74.106.149 << 'EOF'
cd /opt/missions/app
rm -rf frontend/build
mkdir -p frontend
tar -xzf /tmp/build.tar.gz -C frontend/ 2>/dev/null || cp -r /tmp/build frontend/
docker compose restart nginx
EOF
```

---

## Automation (Optional): GitHub Actions

If you want auto-deploy (frontend builds & deploys on every merge to `main`):

Create `.github/workflows/deploy-frontend.yaml` in your **frontend** repo:

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        run: npm install
      
      - name: Build
        run: npm run build
      
      - name: Compress build
        run: tar -czf build.tar.gz build/
      
      - name: Copy to VM
        uses: appleboy/scp-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          source: "build.tar.gz,nginx-frontend.conf"
          target: "/tmp/"
      
      - name: Deploy on VM
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/missions/app
            rm -rf frontend/build
            mkdir -p frontend
            tar -xzf /tmp/build.tar.gz -C frontend/
            cp /tmp/nginx-frontend.conf nginx.conf
            docker compose restart nginx
```

Then add the same secrets to your **frontend** repo (same VM details).

---

## Troubleshooting

**Q: React app loads but API calls fail**
- Check browser console for CORS errors
- Verify nginx config: `docker logs missions_nginx`
- Make sure API URLs are relative (`/api/...`, not absolute)

**Q: 404 on page refresh**
- nginx config has `try_files $uri $uri/ /index.html` — should handle this
- Verify nginx config syntax: `docker run --rm -v /opt/missions/app/nginx.conf:/etc/nginx/nginx.conf nginx nginx -t`

**Q: nginx won't start**
- Check syntax: `docker run --rm -v /opt/missions/app/nginx.conf:/etc/nginx/nginx.conf nginx nginx -t`
- Check logs: `docker logs missions_nginx`

**Q: Build folder not found**
- SSH in and verify: `ls -la /opt/missions/app/frontend/build/`
- Re-run the tar extract step

---

## Summary

- React build → compressed → copied to VM → extracted → nginx serves it
- nginx routes `/api/*` to Django backend (same container)
- No mixed content issues (same HTTP host)
- No domain, no extra cost
- Both frontend and backend on the $0 e2-micro
