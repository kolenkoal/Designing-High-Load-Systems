import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt

CSV_PATH = Path(__file__).parent / "results.csv"
OUT_PATH = Path(__file__).parent / "results.png"


def load(path: Path):
    conc, rps, p50, p95, p99 = [], [], [], [], []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                conc.append(int(row["concurrency"]))
                rps.append(float(row["rps"]))
                p50.append(float(row["p50_ms"]))
                p95.append(float(row["p95_ms"]))
                p99.append(float(row["p99_ms"]))
            except (ValueError, KeyError):
                continue
    return conc, rps, p50, p95, p99


def safe_xscale(ax, xs):
    if xs and all(x > 0 for x in xs):
        ax.set_xscale("log")


def safe_yscale(ax, *series):
    flat = [v for s in series for v in s]
    if flat and all(v > 0 for v in flat):
        ax.set_yscale("log")


def main():
    if not CSV_PATH.exists():
        raise SystemExit(f"{CSV_PATH} not found. Run bench.sh first.")

    conc, rps, p50, p95, p99 = load(CSV_PATH)

    if not conc:
        print("No data rows in results.csv. Did bench.sh fail?", file=sys.stderr)
        sys.exit(1)

    fig, (ax_rps, ax_lat) = plt.subplots(1, 2, figsize=(13, 5))

    ax_rps.plot(conc, rps, marker="o", color="tab:blue")
    safe_xscale(ax_rps, conc)
    ax_rps.set_title("Gateway throughput (1 vCPU)")
    ax_rps.set_xlabel("Concurrency")
    ax_rps.set_ylabel("Requests / sec")
    ax_rps.grid(True, which="both", linestyle="--", alpha=0.4)
    for x, y in zip(conc, rps):
        ax_rps.annotate(f"{y:.0f}", (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)

    ax_lat.plot(conc, p50, marker="o", label="p50", color="tab:green")
    ax_lat.plot(conc, p95, marker="o", label="p95", color="tab:orange")
    ax_lat.plot(conc, p99, marker="o", label="p99", color="tab:red")
    safe_xscale(ax_lat, conc)
    safe_yscale(ax_lat, p50, p95, p99)
    ax_lat.set_title("Latency vs concurrency")
    ax_lat.set_xlabel("Concurrency")
    ax_lat.set_ylabel("Latency (ms)")
    ax_lat.legend()
    ax_lat.grid(True, which="both", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=140)
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
