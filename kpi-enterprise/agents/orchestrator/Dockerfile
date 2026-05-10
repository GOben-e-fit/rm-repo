FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install \
      "fastapi>=0.115" \
      "uvicorn[standard]>=0.30" \
      "pydantic>=2.7" \
      "pydantic-settings>=2.4" \
      "python-jose[cryptography]>=3.3" \
      "httpx>=0.27" \
      "pyyaml>=6.0"

COPY app ./app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import httpx; r = httpx.get('http://127.0.0.1:8000/health', timeout=4); raise SystemExit(0 if r.status_code == 200 else 1)"

ENV KPI_AUTH_MODE=demo \
    KPI_DEFAULT_TENANT=tnt_demo

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
