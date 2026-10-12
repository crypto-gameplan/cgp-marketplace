# Run with Docker

You need Docker Desktop running. Everything else comes from the files in this folder.

## First start

```bash
cp .env.example .env
```

Open `.env` and fill in the values. Then:

```bash
docker compose up -d --build
```

The app runs at http://localhost:<PORT>.

## Every day

| What | Command |
|---|---|
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| See what it prints | `docker compose logs -f app` |
| After you changed code or dependencies | `docker compose up -d --build` |
| Is everything running? | `docker compose ps` |

## Your data

<Which service keeps data, in which volume, and that `docker compose down` keeps it.>

To delete all data and start fresh (cannot be undone): `docker compose down -v`

## When something goes wrong

Run `docker compose logs app` and read the last lines; the error is usually there. <Add the problems this project is known for.>
