FROM python:3.13

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ARG USER_ID=1000
ARG GROUP_ID=1000

WORKDIR /app

COPY . .

RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv pip install --no-cache '.[playwright]'

ENV PLAYWRIGHT_BROWSERS_PATH=/playwright-browsers
RUN playwright install --with-deps chromium

RUN groupadd --gid $GROUP_ID user && \
    useradd --uid $USER_ID --gid $GROUP_ID -m -s /bin/bash user

# Create directories and set permissions
RUN mkdir -p /app/data/output /app/pattern_cache && \
    chown -R ${USER_ID}:${GROUP_ID} /app /opt/venv $PLAYWRIGHT_BROWSERS_PATH

USER user

ENTRYPOINT ["html2rss-ai"]

CMD ["--help"]