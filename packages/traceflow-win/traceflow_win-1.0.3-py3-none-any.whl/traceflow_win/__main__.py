import argparse
import asyncio
import sys

from .traceflow_win import TraceflowWin


async def main():
    parser = argparse.ArgumentParser(description="TraceflowWin CLI tool",prog="python -m traceflow_win")
    parser.add_argument("destination", help="Destination IP or hostname to trace")
    parser.add_argument("--path-count", type=int, default=4, help="Number of parallel paths (default: 4)")
    parser.add_argument("--max-hops", type=int, default=30, help="Maximum number of hops (default: 30)")
    parser.add_argument("--timeout", type=int, default=2, help="Timeout per hop in seconds (default: 2)")

    args = parser.parse_args()

    tracer = TraceflowWin(
        destination=args.destination,
        path_count=args.path_count,
        max_hops=args.max_hops,
        timeout=args.timeout
    )

    results = await tracer.run()

    for path_id, hops in results.items():
        print(f"Path {path_id}: {hops}")

if __name__ == "__main__":
    asyncio.run(main())
