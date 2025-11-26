# Usa a imagem base Python que é compatível com Playwright/Chromium
FROM python:3.10-slim

# Configura o diretório de trabalho no container
WORKDIR /app

# Instala as dependências de sistema (Chromium/Playwright)
# REMOVEMOS: libgconf-2-4 e libgdk-pixbuf2.0-0, que causaram erro.
# ADICIONAMOS: libgdk-pixbuf-xlib-2.0-0, sugerido no log para substituir um dos pacotes.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libnss3 \
    libfontconfig1 \
    libdbus-glib-1-2 \
    libatk1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
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
    # Limpa a lista de pacotes para reduzir o tamanho da imagem
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependência e os instala
# Certifique-se de que requirements.txt está no seu projeto.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala o browser Playwright (Chromium)
RUN playwright install chromium --with-deps

# Copia o restante do código da aplicação
# Lembre-se que o index.html deve estar em 'templates/'
COPY . .

# Define a variável de ambiente para o host/porta do Flask
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# O container irá rodar na porta 5000 (padrão do Flask)
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "conexao.py"]
