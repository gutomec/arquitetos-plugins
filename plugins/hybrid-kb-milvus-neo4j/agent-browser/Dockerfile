# Agent Browser Container
# Browser automation CLI for AI agents - Jurisprudence Search

FROM node:22-slim

# Install system dependencies for Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libxshmfence1 \
    libglu1-mesa \
    libxkbcommon0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install agent-browser globally
RUN npm install -g agent-browser@latest

# Install Chromium for Playwright
RUN agent-browser install --with-deps || npx playwright install chromium --with-deps

# Copy jurisprudence search scripts
COPY . .

# Install additional dependencies
RUN npm install express body-parser cors

# Expose API port
EXPOSE 3100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3100/health || exit 1

# Run the jurisprudence search API
CMD ["node", "server.js"]
