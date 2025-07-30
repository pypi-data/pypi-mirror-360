# TraceflowWin

Small cross-platform traceroute tool that supports multi-path probing based on the functionality of rucarrol's traceflow.

**Rucarrol's Traceflow**: https://github.com/rucarrol/traceflow

Works on **Linux** without **Npcap**  
Requires **Npcap** on **Windows**: [https://npcap.com/#download](https://npcap.com/#download)
-   Must have support raw traffic and Wincap API comp mode

![Npcap](docs/npcap%20installer%20pic.png)
---

## Python Example

```python
from traceflow_win import TraceflowWin
import asyncio

async def main():
    tracer = TraceflowWin("8.8.8.8")
    results = await tracer.run()
    
    for path_id, hops in results.items():
        print(f"Path {path_id}: {hops}")

asyncio.run(main())
```

---

## CLI Usage

```
python -m traceflow_win <Ip/Hostname>
```

### Example:

```
python -m traceflow_win 1.1.1.1 --path-count 5 --max-hops 40
```

---

## CLI Options

| Argument              | Description                                | Default    |
|-----------------------|--------------------------------------------|------------|
| `<destination>`       | Destination IP or hostname to trace        | _Required_ |
| `--path-count`        | Number of parallel paths                   | `4`        |
| `--max-hops`          | Maximum number of hops                     | `30`       |
| `--timeout`           | Timeout per hop in seconds                 | `2`        |
| `-h, --help`          | Show help message                          |            |

## Notes/Known Problems:
- High path counts (8-10 and above) can result in trace errors as scapy sniff() is not asynchronous.