#!/usr/bin/env bash
set -uo pipefail

TARGET="${TARGET:-http://localhost:8000/ping}"
DURATION="${DURATION:-10s}"
LEVELS=(1 5 10 20 50 100 200)
OUT="results.csv"
RAW_DIR="raw"

mkdir -p "$RAW_DIR"

if ! command -v hey >/dev/null 2>&1; then
  echo "ERROR: 'hey' not found. brew install hey" >&2
  exit 1
fi

echo "Sanity check: $TARGET"
if ! curl -fsS --max-time 3 "$TARGET" >/dev/null; then
  echo "ERROR: target $TARGET is not reachable. Is docker compose up?" >&2
  exit 1
fi

echo "Warming up..."
hey -z 3s -c 10 "$TARGET" >/dev/null 2>&1 || true

extract() {
  # extract <egrep-pattern> <field-idx> <multiplier> <file>
  local pattern="$1" idx="$2" mult="$3" raw="$4"
  local val
  val=$(grep -E "$pattern" "$raw" 2>/dev/null | head -n1 \
        | awk -v i="$idx" -v m="$mult" '{printf "%.3f", $i * m}')
  if [[ -z "$val" ]]; then
    echo "0"
  else
    echo "$val"
  fi
}

echo "concurrency,rps,p50_ms,p95_ms,p99_ms" > "$OUT"

for c in "${LEVELS[@]}"; do
  echo "==> concurrency=$c duration=$DURATION"
  raw="$RAW_DIR/hey_c${c}.txt"
  if ! hey -z "$DURATION" -c "$c" "$TARGET" > "$raw" 2>&1; then
    echo "    hey exited non-zero (see $raw)"
  fi

  rps=$(extract "Requests/sec:" 2 1 "$raw")
  p50=$(extract "^[[:space:]]*50%+ in" 3 1000 "$raw")
  p95=$(extract "^[[:space:]]*95%+ in" 3 1000 "$raw")
  p99=$(extract "^[[:space:]]*99%+ in" 3 1000 "$raw")

  echo "$c,$rps,$p50,$p95,$p99" >> "$OUT"
  echo "    rps=$rps p50=${p50}ms p95=${p95}ms p99=${p99}ms"

  if [[ "$rps" == "0" ]]; then
    echo "    WARN: zero RPS — peek $raw for errors"
    tail -n 20 "$raw" | sed 's/^/      /'
  fi

  sleep 2
done

echo
echo "Done. $OUT:"
cat "$OUT"
