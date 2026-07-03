FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml README.md ./
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir .

COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "black_scholes_engine.app:app"]
