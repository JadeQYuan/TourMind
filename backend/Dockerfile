FROM python:3.10-slim

WORKDIR /app

# 依赖由构建脚本在 python:3.10-slim 容器内预装（确保 Linux 平台兼容）
COPY packages/ /app/packages/
ENV PYTHONPATH=/app/packages

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

RUN mkdir -p /app/uploads

EXPOSE 8000

CMD ["sh", "-c", "python -m alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
