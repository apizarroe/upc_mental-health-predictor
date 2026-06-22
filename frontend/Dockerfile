# ── Etapa 1: build ──────────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Instalar dependencias primero (aprovecha caché de capas)
COPY package.json package-lock.json* ./
RUN npm ci

# Copiar el resto del código y construir
COPY . .
RUN npm run build

# Eliminar devDependencies para reducir tamaño
RUN npm prune --production

# ── Etapa 2: runtime ─────────────────────────────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

# Copiar solo lo necesario para ejecutar
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Puerto que usa adapter-node por defecto
ENV PORT=3000
ENV NODE_ENV=production

EXPOSE 3000

CMD ["node", "build/index.js"]
