# Gateway saturation bench (1 vCPU)

Минимальный стенд для замера колена насыщения async FastAPI gateway на 1 vCPU.

## Топология

```
hey -> gateway (cpu 2) -> mock-auth (cpu 0)
                       -> mock-downstream (cpu 1)
```

Каждый upstream спит `asyncio.sleep(0.003)` (имитация I/O). Gateway делает два последовательных
async http-вызова через **один** общий `httpx.AsyncClient`.

## Зависимости

- Docker / Docker Compose
- `hey` — `go install github.com/rakyll/hey@latest`
- Python 3.12 + `matplotlib` для графика

```bash
pip install matplotlib
```

## Запуск

```bash
docker compose up -d --build
bash bench.sh
python plot.py
```

Результаты:
- `results.csv` — сырые метрики (concurrency, rps, p50_ms, p95_ms, p99_ms)
- `raw/hey_c*.txt` — полный вывод `hey` для каждого уровня
- `results.png` — два графика (RPS vs concurrency, latency vs concurrency)

## Замечания

- `cpuset` в docker-compose работает на Linux. На macOS / Docker Desktop пиннинг к
  конкретным физическим ядрам не гарантируется — VM сама решает планирование. Для
  чистого результата запускайте на Linux-хосте.
- Между уровнями нагрузки 2 секунды паузы, плюс отдельный warm-up.
