FROM node:lts-slim

# Install basic development tools
# RUN apt update && apt install -y less git

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . .

# RUN npm run dev