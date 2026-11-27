FROM python:3.12-slim

# Liga a imagem publicada no GHCR a este repositório (necessário para o
# GITHUB_TOKEN do workflow ter permissão de escrita no pacote).
LABEL org.opencontainers.image.source="https://github.com/rafaellimarc01/API-Pipeline"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY app ./app

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
