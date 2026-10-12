# Services in compose.yaml

The template has the app and Postgres. Use the blocks below for other services; each keeps its data in a named volume, has a health check and stays off the network unless the person needs to reach it from their computer.

## Only a database for development

When the person wants just a database and keeps running the app outside Docker, compose.yaml holds the database alone, its port is published on `127.0.0.1` (if 5432 is taken by a Postgres already installed, use `127.0.0.1:5433:5432` and port 5433 in the URL), and the app connects to `localhost:5432` (outside Docker, `localhost` is right). Give them the connection string for their `.env`:

```
DATABASE_URL=postgres://app:change-me@localhost:5432/app
```

## Databases and caches

| Service | Image | Data path for the volume | Health check |
|---|---|---|---|
| Postgres 18 | `postgres:18-alpine` | `/var/lib/postgresql` | `pg_isready -h 127.0.0.1 -U $${POSTGRES_USER} -d $${POSTGRES_DB}` (the `-h` matters, see below) |
| Postgres 17 or older | `postgres:17-alpine` | `/var/lib/postgresql/data` | same |
| MySQL | `mysql:8.4` | `/var/lib/mysql` | `mysqladmin ping -h 127.0.0.1 -u root -p$${MYSQL_ROOT_PASSWORD}` |
| MariaDB | `mariadb:11.8` | `/var/lib/mysql` | `healthcheck.sh --connect --innodb_initialized` |
| MongoDB | `mongo:8` | `/data/db` | `mongosh --quiet --eval "db.adminCommand('ping')"` |
| Redis | `redis:8-alpine` | `/data` (with `--appendonly yes`) | `redis-cli ping` |

`pg_isready` without `-h 127.0.0.1` asks over a local socket, which answers during Postgres's first-start setup before the database accepts network connections. The app then connects too early and crashes once. MySQL has the same trap; its check above already uses `-h 127.0.0.1`.

Use the same major version the project used before. Credentials come from `.env` through `${VAR}`; the `$$` in health checks makes compose leave the variable for the container's shell.

Postgres creates the user and database from `POSTGRES_*` only on the very first start with an empty volume. Changing them later in `.env` does nothing; the person would either change them inside the database or reset the volume (which deletes the data, so ask first).

## Startup order

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

Without `condition: service_healthy` the app starts as soon as the database container exists, before it accepts connections, and crashes on the first query.

A one-off job (migrations, seeding) that must finish first:

```yaml
  migrate:
    build: .
    command: ["npm", "run", "migrate"]
    env_file: [{ path: .env, required: false }]
    depends_on:
      postgres:
        condition: service_healthy
  app:
    depends_on:
      migrate:
        condition: service_completed_successfully
```

## Environment variables

- `.env` next to compose.yaml is read automatically for `${VAR}` substitution in the file.
- `env_file:` passes variables into a container. Give each container only what it needs.
- `${VAR:?message}` stops with a clear message when the variable is missing, instead of starting with an empty password. Never give a secret a default (`${ADMIN_API_KEY:-dev-key}`): the setup then runs with a key everyone can read in the repository.
- Values with `$` must be written as `$$` in compose.yaml, not in `.env`.

## Ports

- `"3000:3000"` = port on your computer : port in the container.
- `"127.0.0.1:5432:5432"` publishes only to this computer. Use it for a database the person reaches from their own tools. When the app runs in compose too, the database needs no published port at all.
- A port already in use on the computer: change the left number (`"3001:3000"`), not the right one.
- Services talk to each other on the internal network by service name and container port; they do not need `ports:` at all.

## Development with live reload

For development, mount the code and run the dev server in a separate file `compose.dev.yaml`:

```yaml
services:
  app:
    build:
      target: build
    command: ["npm", "run", "dev"]
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      NODE_ENV: development
```

Start with `docker compose -f compose.yaml -f compose.dev.yaml up`. The anonymous `/app/node_modules` volume keeps the container's own `node_modules` from being hidden by the mounted folder. For many beginners, running the app outside Docker with only the database in Docker is simpler; suggest that first.
