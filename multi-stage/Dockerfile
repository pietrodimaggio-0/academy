FROM node:alpine as builder
WORKDIR /app
COPY package*.json ./
COPY tsconfig*.json ./
COPY src src
RUN  npm ci && npm run build

FROM node:alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY --from=builder /app/dist/ dist/
ENTRYPOINT ["npm", "run", "start:prod"]
