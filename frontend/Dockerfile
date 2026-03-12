<<<<<<< HEAD
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev"]
=======
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy static dashboard assets
COPY index.html ./index.html
COPY mockData.js ./mockData.js

# Nginx default command serves files on port 80
>>>>>>> dhruvBranch

