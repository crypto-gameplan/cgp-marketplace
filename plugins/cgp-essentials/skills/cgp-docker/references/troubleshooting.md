# Docker errors and their causes

Find the error message, fix the cause, run again. Explain the fix to the person in one plain sentence.

## Docker itself

| Message | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` | Docker Desktop is not running | `open -a Docker`, wait until `docker info` works |
| `docker: command not found` | Docker is not installed | `cgp-ai setup --change` (choose Docker Desktop) or docker.com |
| `no space left on device` | Old images and build cache fill Docker's disk | Show `docker system df`. Offer `docker builder prune` (cache only, safe). `docker system prune` or anything with volumes only after the person agrees, since volumes hold data |

## Building

| Message | Cause | Fix |
|---|---|---|
| `failed to compute cache key: "/package-lock.json": not found` | The file is missing or listed in `.dockerignore` | Check the file exists and is not ignored; create the lock file if there is none |
| `npm ci` ... `package.json and package-lock.json are not in sync` | Lock file outdated | `npm install` locally, commit the lock file, build again |
| `uv sync --locked` ... `lockfile needs to be updated` | `uv.lock` outdated | `uv lock` locally, commit, build again |
| `gyp ERR!`, `node-gyp`, `error: command 'gcc' failed` | Native module needs build tools | Add build tools in the build stage (see stacks.md, Native modules) |
| `exec format error` when the container starts | Image built for another processor (Apple Silicon = arm64, most servers = amd64) | Build on the server, or `docker build --platform linux/amd64` (see deploy.md) |
| Build takes ages, `Sending build context` is huge | No or weak `.dockerignore` | Add `node_modules`, `.venv`, `.git`, data and media folders |
| Code change has no effect | Old image still running | `docker compose up -d --build` |

## Starting and running

| Message | Cause | Fix |
|---|---|---|
| `port is already allocated` / `address already in use` | Something else uses that port on the computer (often a local Postgres or another project) | `lsof -i :5432` shows what. Change the left number in `ports:` (`"5433:5432"`), or stop the other program |
| `ECONNREFUSED 127.0.0.1:5432`, `connection refused` to `localhost` | The app inside a container uses `localhost`, which is the container itself | Use the service name: `postgres:5432` |
| Same error with the service name, only right after start | The database is not ready yet | `depends_on` with `condition: service_healthy` and a health check; for Postgres `pg_isready -h 127.0.0.1`, since without `-h` it reports ready too early on the first start |
| App on the host cannot reach a service in Docker | Port not published | `ports: ["127.0.0.1:5432:5432"]` on that service |
| Container must reach something on the computer | `localhost` points into the container | `host.docker.internal` (works in Docker Desktop) |
| `password authentication failed` | Credentials changed after the volume was created; Postgres set them on the first start only | Use the original credentials, change them inside the database, or reset the volume after the person agrees (data is lost) |
| Postgres 18 exits: data in `/var/lib/postgresql/data` ... unused mount | Volume mounted at the pre-18 path | Mount at `/var/lib/postgresql` |
| `EACCES: permission denied` / `PermissionError` writing a file | The app runs as a normal user and the folder belongs to root | `COPY --chown=...` for the app folder; for a writable folder, create it and `chown` it in the Dockerfile before `USER` |
| Container `Restarting` over and over | The app crashes at start | `docker compose logs app`, fix the first error printed |
| `unhealthy` | Health check fails: wrong port or path, or the app has no route at `/` | Check the health URL with `docker compose exec app ...`, adjust the path or add a `/health` route |
| Variables empty inside the container | `.env` missing, wrong name, or not passed with `env_file`/`environment` | `docker compose config` shows the final values (it prints secrets, so do not paste the output anywhere public) |
| Data gone after restart | No volume, or `docker compose down -v` was used | Named volume on the data path (compose.md). Without a named volume, the old data often still sits in an anonymous volume: `docker volume ls -f dangling=true`, then look inside before anyone runs a prune. Tell the person this before saying the data is lost |
| Logs appear late or never (Python) | Output buffering | `ENV PYTHONUNBUFFERED=1` |
