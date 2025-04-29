# Usa imagem oficial leve do Python
FROM python:3.13-slim

# Instala dependências de sistema necessárias pro Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
  libnss3 \
  libnspr4 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libatspi2.0-0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libxkbcommon0 \
  libasound2 \
  fonts-liberation \
  libappindicator3-1 \
  lsb-release \
  wget \
  curl \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Atualiza pip
RUN pip install --upgrade pip

# Instala o Playwright separadamente (antes para baixar os browsers depois)
RUN pip install playwright

# Faz download dos browsers necessários (Chromium, Firefox, Webkit) + deps
RUN playwright install --with-deps

# Define o diretório de trabalho
WORKDIR /app

# Copia o seu projeto para dentro do container
COPY . .

# Instala as dependências do seu projeto
RUN pip install -r requirements.txt

# Expõe a porta padrão do FastAPI
EXPOSE 8000

# Comando para iniciar o app (Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
