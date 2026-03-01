"""CLI entrypoint for the full data pipeline."""

from _runner import run


if __name__ == "__main__":
    run("machineinnovatorsinc_solution.data.pipeline:main")
