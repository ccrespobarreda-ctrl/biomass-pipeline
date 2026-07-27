FROM python:3.12-slim
# uv para instalar dependencias rapido y reproducible
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml ./
RUN uv pip install --system --no-cache .
COPY src ./src
COPY configs ./configs
ENV PYTHONPATH=/app/src
# el comando concreto lo pondra Dagster; por ahora, imagen base reproducible
CMD ["python", "-c", "import biomass_pipeline; print('imagen lista')"]
