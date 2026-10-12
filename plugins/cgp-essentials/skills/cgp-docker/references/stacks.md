# Adapting the templates to a stack

Pick the template closest to the project, then change only what this file says for that stack.

## Contents

- [Node.js package managers](#nodejs-package-managers)
- [Next.js](#nextjs)
- [Static sites: Vite, React, Vue, Astro](#static-sites-vite-react-vue-astro)
- [Python with requirements.txt](#python-with-requirementstxt)
- [Django](#django)
- [Bots, workers and scripts without a port](#bots-workers-and-scripts-without-a-port)
- [Other languages](#other-languages)
- [Choosing base image versions](#choosing-base-image-versions)

## Node.js package managers

| Lock file | Copy | Install |
|---|---|---|
| `package-lock.json` | `package.json package-lock.json` | `npm ci` (`--omit=dev` for the runtime stage) |
| `pnpm-lock.yaml` | `package.json pnpm-lock.yaml` | `corepack enable && pnpm install --frozen-lockfile` (`--prod` for runtime) |
| `yarn.lock` | `package.json yarn.lock` (+ `.yarnrc.yml`, `.yarn/` for Yarn 2+) | `corepack enable && yarn install --immutable` |
| `bun.lock` | `package.json bun.lock` | use `oven/bun:1-slim` as base, `bun install --frozen-lockfile` |
| none | | Create one first (`npm install` locally) and commit it. Without a lock file builds are not repeatable. |

Native modules (`bcrypt`, `sharp`, `better-sqlite3`) need build tools in the build stage on `-slim` images: `apt-get update && apt-get install -y --no-install-recommends python3 make g++ && rm -rf /var/lib/apt/lists/*`. Keep them out of the final stage by installing dependencies in a build stage and copying `node_modules` over.

## Next.js

Set `output: "standalone"` in `next.config.js`, then:

```dockerfile
FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM node:24-slim
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0
WORKDIR /app
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
```

`NEXT_PUBLIC_*` variables are baked in at build time. They must be passed as build args and are visible to every visitor, so never put secrets there.

## Static sites: Vite, React, Vue, Astro

The result is plain files, so the final image is a small web server, not Node:

```dockerfile
FROM node:24-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
```

`nginx-unprivileged` runs as a normal user and listens on 8080. For client-side routing (React Router), add an nginx config with `try_files $uri /index.html;`. `VITE_*` variables are baked in at build time and public.

## Python with requirements.txt

Replace the uv build stage:

```dockerfile
FROM python:3.14-slim AS build
WORKDIR /app
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY . .
```

The runtime stage stays as in the template. If `requirements.txt` has no pinned versions (`fastapi` instead of `fastapi==0.118.0`), say so: builds can break when a new version comes out. Suggest `pip freeze > requirements.txt` or moving to uv.

## Django

- Start with gunicorn, not `runserver`: `CMD ["gunicorn", "mysite.wsgi", "--bind", "0.0.0.0:8000"]` (add `gunicorn` to the dependencies).
- `collectstatic` in the build stage: `RUN python manage.py collectstatic --noinput` (needs a dummy `SECRET_KEY` at build time: `RUN SECRET_KEY=build python manage.py collectstatic --noinput`).
- Migrations at start, not at build: a compose service `migrate` with `command: python manage.py migrate` and the app `depends_on` it with `condition: service_completed_successfully`.
- `ALLOWED_HOSTS` and `DEBUG=False` from `.env`.

## Bots, workers and scripts without a port

- No `EXPOSE`, no `ports:` in compose.
- The HTTP health check does not apply. Either drop `HEALTHCHECK` or check something the bot does (for example a file it touches every minute: `test: ["CMD", "find", "/tmp/alive", "-mmin", "-2"]`).
- `restart: unless-stopped` so it comes back after a crash or a server reboot.
- Python: keep `PYTHONUNBUFFERED=1` or the logs appear late.
- Scheduled scripts: prefer the host's cron or a scheduler service calling `docker compose run --rm job`; cron inside a container is a common source of silent failures.

## Other languages

Same rules, different images:

| Language | Build stage | Final stage |
|---|---|---|
| Go | `golang:1.25` with `CGO_ENABLED=0 go build` | `gcr.io/distroless/static-debian12:nonroot` |
| Rust | `rust:1-slim` with `cargo build --release` | `debian:bookworm-slim` + `useradd` |
| Java | `eclipse-temurin:25-jdk` with the Maven or Gradle wrapper | `eclipse-temurin:25-jre` |
| PHP | `composer:2` for `composer install --no-dev` | `php:8.4-fpm-alpine` (+ nginx) or `php:8.4-apache` |

## Choosing base image versions

- Node: the current Active LTS (even major). Node 24 until late October 2026, then Node 26. Schedule: https://github.com/nodejs/Release
- Python: the newest stable minor the project's dependencies support (`requires-python` in `pyproject.toml`).
- Postgres: the major the project already uses. A new project gets the newest major. Never change the major of an existing database volume without a dump and restore: the new version cannot read the old data files.
- `-slim` (Debian) is the safe default. `-alpine` is smaller, but its different C library breaks some native Node and Python packages. Use it for databases and Redis, where it is the common choice.
- Check a tag exists before using it: `docker manifest inspect node:24-slim`.
