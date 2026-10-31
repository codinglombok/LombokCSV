# LombokCSV container image. The entrypoint is a self-verifying smoke test:
# it imports the built library and checks outputs pinned from the shared
# vectors, so "docker run" exiting 0 proves the shipped artefact works.
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY src ./src
COPY tsconfig.json ./
RUN npx tsup src/index.ts --format esm,cjs --dts --clean

FROM node:24-alpine
WORKDIR /app
ARG VERSION=dev
ENV LOMBOKCSV_VERSION=$VERSION
COPY --from=build /app/dist ./dist
COPY docker/smoke.mjs ./smoke.mjs
USER node
ENTRYPOINT ["node", "smoke.mjs"]
