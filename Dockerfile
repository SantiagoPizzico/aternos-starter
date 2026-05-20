FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpangocairo-1.0-0 \
    libgtk-3-0 libx11-xcb1 libxss1 \
    fonts-liberation fonts-unifont \
    libasound2t64 libdbus-1-3 libdrm2 \
    libxext6 libxfont2 libxrender1 \
    libxtst6 xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright
RUN playwright install chromium

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
