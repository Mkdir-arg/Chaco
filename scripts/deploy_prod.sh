#!/usr/bin/env bash
set -Eeuo pipefail

# Deploy script for production (AWS host)
# - Optional git pull
# - Backup of key files + resolved compose
# - Recreate/build services
# - Health check with retries
# - Basic rollback to previous git commit on failure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"
HEALTH_URL="${HEALTH_URL:-http://localhost/health/}"
HEALTH_RETRIES="${HEALTH_RETRIES:-30}"
HEALTH_DELAY_SECONDS="${HEALTH_DELAY_SECONDS:-5}"
ROLLBACK_ON_FAIL="${ROLLBACK_ON_FAIL:-1}"
PULL_BEFORE_DEPLOY="${PULL_BEFORE_DEPLOY:-0}"

cd "$APP_DIR"

log() { printf '[deploy] %s\n' "$*"; }
err() { printf '[deploy][error] %s\n' "$*" >&2; }

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Missing required command: $1"
    exit 1
  fi
}

require_cmd docker
require_cmd git
require_cmd curl

if ! docker compose version >/dev/null 2>&1; then
  err "Docker Compose plugin is required (docker compose ...)"
  exit 1
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  err "Compose file not found: $COMPOSE_FILE"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  err "Env file not found: $ENV_FILE"
  exit 1
fi

if [ "$PULL_BEFORE_DEPLOY" = "1" ]; then
  log "Pulling latest changes from git..."
  git pull --ff-only
fi

if [ -n "$(git status --porcelain)" ]; then
  err "Working tree is not clean. Commit/stash changes before deploy."
  exit 1
fi

PREV_COMMIT="$(git rev-parse HEAD)"
log "Current commit: $PREV_COMMIT"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$APP_DIR/deploy_backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

log "Saving deployment backup to $BACKUP_DIR"
cp "$COMPOSE_FILE" "$BACKUP_DIR/"
cp "$ENV_FILE" "$BACKUP_DIR/"
[ -f "nginx.conf" ] && cp "nginx.conf" "$BACKUP_DIR/"
[ -f "config/settings.py" ] && cp "config/settings.py" "$BACKUP_DIR/settings.py"
[ -f "config/settings_production.py" ] && cp "config/settings_production.py" "$BACKUP_DIR/settings_production.py"
docker compose -f "$COMPOSE_FILE" config > "$BACKUP_DIR/compose.resolved.yml"
printf '%s\n' "$PREV_COMMIT" > "$BACKUP_DIR/previous_commit.txt"

health_check() {
  local i=1
  while [ "$i" -le "$HEALTH_RETRIES" ]; do
    if curl -fsS "$HEALTH_URL" >/dev/null; then
      log "Health check OK: $HEALTH_URL"
      return 0
    fi
    log "Health check failed ($i/$HEALTH_RETRIES), retrying in ${HEALTH_DELAY_SECONDS}s..."
    sleep "$HEALTH_DELAY_SECONDS"
    i=$((i + 1))
  done
  return 1
}

rollback() {
  if [ "$ROLLBACK_ON_FAIL" != "1" ]; then
    err "Rollback disabled (ROLLBACK_ON_FAIL=$ROLLBACK_ON_FAIL)."
    return 1
  fi

  err "Starting rollback to commit $PREV_COMMIT ..."
  git checkout --force "$PREV_COMMIT"
  docker compose -f "$COMPOSE_FILE" up -d --build --force-recreate

  if health_check; then
    log "Rollback completed successfully."
    return 0
  fi

  err "Rollback failed. Manual intervention required."
  return 1
}

log "Validating compose config..."
docker compose -f "$COMPOSE_FILE" config >/dev/null

log "Deploying services..."
docker compose -f "$COMPOSE_FILE" up -d --build --force-recreate

log "Waiting for service health..."
if health_check; then
  log "Deploy completed successfully."
  exit 0
fi

err "Deploy failed health checks."
docker compose -f "$COMPOSE_FILE" ps || true
docker compose -f "$COMPOSE_FILE" logs --tail=200 web websocket nginx || true

rollback
