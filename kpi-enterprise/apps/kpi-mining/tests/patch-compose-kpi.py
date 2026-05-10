#!/usr/bin/env python3
from pathlib import Path


COMPOSE_PATH = Path("/opt/rm-ki-appliance/repo/overrides/dev/docker-compose.dev-stack.yml")

OLD_BLOCK = """  # === KPI Mining Enterprise: Medialine-styled landing ===
  kpi-mining:
    image: nginx:alpine
    container_name: kpi-mining
    restart: unless-stopped
    volumes:
      - ./kpi-mining/index.html:/usr/share/nginx/html/index.html:ro
    networks: [rmki-edge]
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost/ -o /dev/null || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3
"""

NEW_BLOCK = """  # === KPI Enterprise Mining: C-Level Performance OS ===
  kpi-mining:
    build:
      context: ./kpi-mining
    image: rmki-local/kpi-mining:dev
    container_name: kpi-mining
    restart: unless-stopped
    volumes:
      - ./kpi-mining:/usr/share/nginx/html:ro
      - ./kpi-mining/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    networks: [rmki-edge]
    labels:
      - "rm.ki.role=kpi-enterprise-mining"
      - "rm.ki.tenant=shared-demo"
      - "rm.ki.api=static-plus-agent-proxy"
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost/api/health -o /dev/null || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3
"""


def main() -> None:
    text = COMPOSE_PATH.read_text(encoding="utf-8")
    if NEW_BLOCK in text:
        print("compose already updated")
        return
    if OLD_BLOCK not in text:
        raise SystemExit("compose kpi block did not match expected old/new shape")
    COMPOSE_PATH.write_text(text.replace(OLD_BLOCK, NEW_BLOCK), encoding="utf-8")
    print("compose kpi block updated")


if __name__ == "__main__":
    main()
