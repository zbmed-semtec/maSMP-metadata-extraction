FROM node:18

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Add node_modules/.bin to PATH
ENV PATH /app/node_modules/.bin:$PATH
ARG VUE_APP_API_URL
ENV VUE_APP_API_URL=${VUE_APP_API_URL}

EXPOSE 8080 3000

# Start the application
CMD ["npm", "run", "serve"]