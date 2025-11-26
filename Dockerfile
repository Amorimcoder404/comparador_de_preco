# Usa uma imagem base Python que é compatível com Playwright/Chromium
# A imagem 'slim' é menor, mas garantimos as dependências com os comandos RUN
FROM python:3.10-slim

# Instala as dependências necessárias para o Playwright (Chromium)
# O Playwright precisa de algumas libs do sistema que o 'slim' não tem por padrão.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libdbus-glib-1-2 \
    libatk1.0-0 \
    libgdk-pixbuf2.0-0 \
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
    libnss3-dev \
    libxtst6 \
    ca-certificates \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configura o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de dependência e os instala
# Você precisa de um arquivo requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala os browsers do Playwright (Chromium é o que você está usando)
# O comando '--with-deps' instala as dependências do sistema automaticamente.
RUN playwright install chromium --with-deps

# Copia o restante do código da aplicação
# 'templates' é onde deve estar seu index.html
COPY . .

# Define a variável de ambiente para o host/porta do Flask
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# O container irá rodar na porta 5000 (padrão do Flask)
EXPOSE 5000

# Comando para rodar a aplicação usando Gunicorn, que é o servidor de produção
# Configuramos 1 worker e 4 threads para lidar melhor com o scraping assíncrono (Playwright).
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:5000", "conexao:app"]