FROM python:3.13-slim

# Instala dependências do sistema e limpa cache
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 \
  libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
  libxkbcommon0 libasound2 fonts-liberation libappindicator3-1 \
  lsb-release wget curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Atualiza pip e instala playwright
RUN pip install --upgrade pip && pip install playwright==1.43.0

# Baixa browsers do Playwright
RUN playwright install --with-deps

# Define diretório de trabalho
WORKDIR /app

# Copia só os requirements antes (melhor cache)
COPY requirements.txt .

# Instala dependências Python
RUN pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe porta usada pelo FastAPI
EXPOSE 8000

# Inicia aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
