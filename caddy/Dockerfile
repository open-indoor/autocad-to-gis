FROM caddy:2.4.3-builder-alpine AS builder

RUN xcaddy build \
    --with github.com/RussellLuo/caddy-ext/ratelimit

RUN xcaddy build \
    --with https://github.com/echocat/caddy-filter

FROM caddy:2.4.3-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy