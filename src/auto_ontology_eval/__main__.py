"""Entry point: python -m auto_ontology_eval --run-dir runs/eval

Runs preflight, S2, S1, S3 and S4 in order through the fail-closed
pipeline, then writes the results document into the run directory
(RESULTS.md, or RESULTS-LIVE.md in the live-internals configuration of
spec Amendment 3). Exits non-zero when any step fails or the
NVIDIA_API_KEY secret is missing.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import config, live, pipeline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="auto_ontology_eval")
    parser.add_argument("--run-dir", default="runs/eval")
    parser.add_argument("--upstream-dir", default="/tmp/auto-ontology")
    parser.add_argument("--configuration", default=config.DEFAULT_CONFIGURATION,
                        choices=config.CONFIGURATIONS)
    args = parser.parse_args(argv)
    run_dir = Path(args.run_dir)
    live.CTX.upstream_dir = Path(args.upstream_dir)
    live.CTX.configuration = args.configuration
    code = pipeline.run_all(dict(os.environ), live.STEPS, run_dir,
                            configuration=args.configuration)
    if (live.CTX.upstream_dir / ".env").exists():
        live.stage_teardown_logs(run_dir, os.environ.get("NVIDIA_API_KEY", "").strip())
    status = "failed, see failure.json" if code else "completed"
    results_name = ("RESULTS-LIVE.md" if args.configuration == config.LIVE_CONFIGURATION
                    else "RESULTS.md")
    print(f"auto-ontology-eval {status}; {results_name} at {run_dir / results_name}")
    return code


if __name__ == "__main__":
    sys.exit(main())
