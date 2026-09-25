FROM node:20

ENV NPM_TOKEN=npm_9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f
ENV NODE_ENV=production

WORKDIR /app

COPY . .

RUN apt-get update
RUN apt-get install -y curl vim netcat-openbsd
RUN npm install
RUN npm run build

EXPOSE 3000

CMD ["node", "dist/main.js"]
