FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup
WORKDIR /app
COPY --from=build /app/dist /app/dist
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules /app/node_modules
COPY --from=build /app/vite.config.js ./
COPY --from=build /app/index.html ./
COPY --from=build /app/src /app/src

USER appuser
EXPOSE 5173
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]