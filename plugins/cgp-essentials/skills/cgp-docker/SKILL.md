---
name: cgp-docker
description: Put a project into Docker the safe and clean way and keep it running, for people who are new to Docker. Writes a Dockerfile, .dockerignore, compose.yaml and .env.example from tested templates, adds databases like Postgres or Redis, builds and starts everything to prove it works, fixes Docker errors, and leaves a short how-to-run guide. Use whenever someone mentions Docker, a Dockerfile, docker compose, containers, images, "make it run on my server / VPS", "so my friend can start it too", a local database without installing it, or pastes a Docker error, even if they never say "Docker".
---

The people using this skill are often new to programming and to Docker. They want a project that starts with one command, keeps its data, and does not leak secrets. They do not want a lecture. Do the work, prove it works, and explain only what they need to run and change it.

## 1. Check Docker itself

Run `docker info`. Three outcomes:

- **Works**: continue.
- **"Cannot connect to the Docker daemon"**: Docker Desktop is installed but not running. Open it (`open -a Docker` on a Mac), wait until `docker info` succeeds, then continue.
- **`docker: command not found`**: Docker is not installed. With cgp-ai: `cgp-ai setup --change` and choose Docker Desktop, or `cgp-ai setup --profile builder --with docker-desktop`. Otherwise Docker Desktop from docker.com. You can still write the files, but say clearly that nothing was tested.

## 2. Look at the project before you write anything

Find out yourself; never ask the person what the files can tell you:

- Language and package manager, from the lock file: `package-lock.json` (npm), `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`, `uv.lock`, `poetry.lock`, `requirements.txt`.
- How the app starts (`scripts.start` in `package.json`, `[project.scripts]`, a `main.py`, a `Procfile`) and whether it has a build step.
- The port it listens on and whether it reads it from `PORT`.
- Every environment variable it reads (`process.env.X`, `os.environ`, `os.getenv`, settings classes). These become `.env.example`.
- Services it talks to: Postgres, MySQL, Redis, MongoDB, other APIs. Look at dependencies and connection strings.
- Existing Docker files. Improve them; do not throw away choices someone made on purpose.
- Whether `.env` is ignored by git. If a real `.env` with secrets is tracked, say so first: it is the most urgent problem.

## 3. Decide what to build

Most requests are one of these:

| The person wants | Build |
|---|---|
| Run their app anywhere, or share it | Dockerfile + .dockerignore + compose.yaml with the app and its services |
| Just a database or Redis for development | compose.yaml with that service only; the app keeps running normally |
| Put it on a server | The above, plus [references/deploy.md](references/deploy.md) |
| Fix an error or an existing setup | Read [references/troubleshooting.md](references/troubleshooting.md), fix the cause, then run the check in step 5 |

Ask only when the answer changes what you build and the project cannot tell you, at most three questions in one message, each with your recommended answer so "yes" is enough. Typical: "Should the database live in Docker too? ➡️ Yes, then one command starts everything." Everything else: pick a sensible default and name it as an assumption in your summary.

## 4. Write the files from the templates

Start from the templates in [assets/](assets/) and adapt them to what you found; [references/stacks.md](references/stacks.md) covers Next.js, Vite and other static sites, FastAPI, Django, bots and scripts without a port, and other languages. [references/compose.md](references/compose.md) covers databases, volumes and health checks.

The templates already follow the rules below. When you adapt them, keep them, because each one prevents a problem beginners hit later and cannot diagnose:

- **Pinned base images** (`node:24-slim`, `python:3.14-slim`, `postgres:18-alpine`), never `latest`. `latest` changes under you and breaks a build that worked yesterday. Use the current LTS or stable major; if unsure, check the official image page.
- **Install from the lock file** (`npm ci`, `uv sync --locked`), so the container gets exactly the versions that work on the person's machine.
- **Dependencies before code** in the Dockerfile, so a code change does not reinstall everything.
- **Multi-stage when there is a build step**: build tools stay in the first stage, the final image carries only what runs. Smaller, faster, less to attack.
- **Run as a normal user, not root.** If someone breaks into the app, they do not own the container.
- **Secrets never in the image.** No `.env` copied in, no keys in `ENV` or `ARG`. Secrets come from `.env` at runtime through compose. `.dockerignore` keeps `.env`, `.git` and `node_modules` / `.venv` out of the build.
- **`.env.example` with every variable**, empty or with harmless sample values and a comment each; `.env` in `.gitignore`. This is how the next person knows what to fill in.
- **No default values for secrets** in compose.yaml (`${ADMIN_API_KEY:-dev-key}`). Use `${VAR:?set VAR in .env}` so a missing secret stops the start with a clear message instead of running with a key anyone can read. When you create the person's `.env`, fill passwords with random values (`openssl rand -hex 16`), never `change-me`.
- **Leave existing credentials alone.** Postgres sets user and password only when its volume is first created; a new password in `.env` locks the app out of an existing database. Change credentials only for a database that has no data yet, and say so.
- **Data in named volumes.** A database without a volume loses everything on `docker compose down`.
- **Health checks and `depends_on: condition: service_healthy`**, so the app starts only when the database accepts connections.
- **Inside compose, services find each other by service name** (`postgres:5432`), not `localhost`. `localhost` inside a container is the container itself.
- **Database ports not published** when the app runs in compose too: the app reaches the database inside Docker, and a Postgres the person already has on port 5432 keeps working. Publish a database port only when the person's own tools or an app outside Docker need it, and then on `127.0.0.1` so it is not reachable from the internet.

## 5. Prove it works

Do not hand over files you have not run. With Docker available:

1. `python3 <this skill>/scripts/check_docker.py <project>`: static check for the rules above. Fix every error; fix warnings unless you have a reason, and name the reason.
2. `docker compose build` (or `docker build`), then `docker compose up -d`. If a port is already taken on this computer, test with a second compose file outside the project that publishes other ports (`docker compose -f compose.yaml -f /tmp/test-ports.yaml up -d`) and deliver the files with the normal ports.
3. Wait for health, then hit the app (`curl -fsS localhost:<port>/<health or root>`) and look at `docker compose logs` for errors.
4. Confirm it does not run as root: `docker compose exec <app> id -u` is not `0`.
5. Note the image size (`docker images`). For a typical Node or Python app, a few hundred MB is normal; above about 1 GB, look for a missed `.dockerignore` entry or build tools left in the final stage.
6. `docker compose down` (without `-v`) when the person did not ask to keep it running.

When something fails, read the error, look it up in [references/troubleshooting.md](references/troubleshooting.md), fix the cause and run again. Tell the person what failed and what you changed in one line; the fix matters more than the story.

Commands that delete data need the person's yes first, every time: `docker compose down -v`, `docker volume rm`, `docker system prune`, `docker image prune -a`. Volumes hold their database. Explain what would be lost before asking. This includes cleaning up after your own tests in their project: stop the containers with `docker compose down` and leave the volume, or ask.

## 6. Hand over

Write in the language the person wrote to you: your answer, `DOCKER.md` and the comments in the files they will open (`.env.example`, `compose.yaml`). Use the language's real characters (ä, ö, ü, ß in German), not ASCII stand-ins.

Write `DOCKER.md` in the project from [assets/DOCKER.md](assets/DOCKER.md) (or a "Run with Docker" section in an existing README): the three or four commands they need (start, stop, logs, rebuild after changes), what to put in `.env`, where the data lives and how to reset it on purpose.

Then tell the person, short and in plain words:

- What you created, one line per file, saying what it is for, not how it works.
- That it was tested, and how (build, started, answered on port X, runs as a normal user, image size).
- How to start it, as its own clearly marked step with the command in a code block, not inside the test report.
- Assumptions you made and anything they must still do (fill in `.env`, rotate a leaked key).

The person is new to this, so every Docker word in your answer gets a few plain words the first time it appears, including the words you use to explain a fix. Better still, say it without the word. Ready-made explanations:

| Word | Plain words |
|---|---|
| image | the packed app, built from the Dockerfile |
| container | the running app, started from the image |
| volume | a folder Docker keeps for the data, so it survives restarts |
| compose / compose.yaml | the file that starts the app and its database together with one command |
| service | one part in compose.yaml, for example the app or the database; they find each other by this name |
| port `3000:3000` | the app is reachable at localhost:3000 on your computer |
| health check | Docker regularly asks the app whether it works |
| `.env` | the file with your passwords and keys; it stays on your computer |

Leave out what they do not need to act: internal mechanics (sockets, layers, init processes) belong in your work, not in their answer.
