import argparse
import json

from planner import plan_jobs


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("jobs")
    args = parser.parse_args(argv)
    with open(args.jobs, encoding="utf-8") as handle:
        jobs = json.load(handle)
    print(json.dumps(plan_jobs(jobs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

