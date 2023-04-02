#!/usr/bin/env python3
from argparse import ArgumentParser, Namespace
from github_rest_api import Repository


def parse_args(args=None, namespace=None) -> Namespace:
    """Parse command-line arguments.
    :param args: The arguments to parse.
        If None, the arguments from command-line are parsed.
    :param namespace: An inital Namespace object.
    :return: A namespace object containing parsed options.
    """
    parser = ArgumentParser(
        description="Run benchmark for the Rust project and save results to gh-pages."
    )
    parser.add_argument(
        "--token",
        dest="token",
        required=True,
        help="The personal access token for authentication.",
    )
    return parser.parse_args(args=args, namespace=namespace)


def main():
    args = parse_args()
    repo = Repository(args.token, "legendu-net", "docker-rust-cicd")
    repo.create_pull_request(
        {
            "base": "main",
            "head": "dev",
            "title": "Merge dev into main",
        },
    )


if __name__ == "__main__":
    main()
