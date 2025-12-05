FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libfontconfig1 \
    libatk1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libgtk-3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libasound2 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    libcups2 \
    libxkbcommon0 \
    libdrm2 \
    libgbm1 \
    libexpat1 \
    libglib2.0-0 \
    ca-certificates \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# instala chromium e deps
RUN playwright install chromium

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "conexao:app"]
