# Running it on a server

The simplest path that works for most people: a small Linux server (VPS), Docker installed there, the project copied over with git, and the same `docker compose up -d --build`.

## Steps

1. **Server**: a VPS with Ubuntu LTS, 2 GB RAM or more for an app with a database. Log in with an SSH key, not a password.
2. **Docker on the server**: Docker Engine from Docker's official instructions for the distribution (`https://docs.docker.com/engine/install/ubuntu/`). Docker Desktop is for your own computer, not for servers.
3. **Code**: `git clone` the repository on the server. Since `.env` is not in git, create it there from `.env.example` with production values (new, strong passwords; not the ones from development).
4. **Start**: `docker compose up -d --build`. `restart: unless-stopped` brings everything back after a reboot.
5. **Updates**: `git pull && docker compose up -d --build`.

## What is different on a server

- **Database ports**: remove `ports:` from the database (or keep it on `127.0.0.1`). A database reachable from the internet gets attacked within hours.
- **Firewall**: allow only SSH (22), HTTP (80) and HTTPS (443). Docker's published ports bypass `ufw` rules, so not publishing a port is the reliable protection.
- **HTTPS**: put a reverse proxy in front that gets certificates automatically. Caddy is the easiest:

  ```yaml
  caddy:
    image: caddy:2-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
    restart: unless-stopped
  ```

  `Caddyfile`: `example.com { reverse_proxy app:3000 }`. Then the app needs no published port at all.
- **Processor type**: a Mac with Apple Silicon builds `arm64` images; most servers are `amd64`. Building on the server avoids the problem. If you build elsewhere and push to a registry, use `docker buildx build --platform linux/amd64`.
- **Backups**: a volume is not a backup. For Postgres, a daily `docker compose exec -T postgres pg_dump -U <user> <db> > backup.sql` from the host's cron, copied off the server.
- **Logs**: Docker keeps logs forever by default. Limit them per service:

  ```yaml
  logging:
    driver: local
    options:
      max-size: "10m"
      max-file: "3"
  ```

## With an image registry instead of building on the server

When builds are slow on a small server or several servers run the same image: build in GitHub Actions, push to GitHub Container Registry (`ghcr.io/<owner>/<app>:<version>`), and on the server use `image:` instead of `build:` in compose.yaml and `docker compose pull && docker compose up -d`. Tag with versions or commit hashes, not only `latest`, so a bad release can be rolled back.
