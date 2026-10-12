# syntax=docker/dockerfile:1
# Node.js app WITHOUT a build step (plain JavaScript, Express, Fastify, a bot).
# Adapt: the lock file and install command (npm, pnpm, yarn), the port, the health path, the start command.

FROM node:24-slim
ENV NODE_ENV=production
WORKDIR /app

# Dependencies first: this layer is reused until package.json or the lock file changes.
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev

# Then the code, owned by the unprivileged "node" user that the image already has.
COPY --chown=node:node . .
USER node

ENV PORT=3000
EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+process.env.PORT+'/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "server.js"]
