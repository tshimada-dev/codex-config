import argparse
import json

from settings import load_config


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--profile", action="append", required=True)
    args = parser.parse_args(argv)
    result = {profile: load_config(args.config, profile) for profile in args.profile}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

