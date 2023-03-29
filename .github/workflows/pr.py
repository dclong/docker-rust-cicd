#!/usr/bin/env python3
import json
from argparse import ArgumentParser, Namespace
import requests

OWNER = "legendu-net"
REPO = "docker-rust-cicd"


def list_pull_requests(token: str, owner: str, repo: str) -> list[dict]:
    resp = requests.get(
        url=f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
        },
    )
    if not resp.ok:
        resp.raise_for_status()
    return resp.json()


def create_pull_request(token: str, owner: str, repo: str, data: dict[str, str]) -> dict:
    """Create a pull request.
    Notice that the error code 422 (Unprocessable Entity)
    means there's no changes to merge from the head branch to the base branch,
    so it is not really an error.
    :param token: The personal access token for authentication.
    :param owner: Owner of the repository.
    :param repo: Name of the repository.
    :param data: A dict containing information (e.g., base, head, title, body, etc.)
    about the pull request to be created.
    """
    if not ("head" in data and "base" in data):
        raise ValueError("The data dict must contains keys head and base!")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    resp = requests.post(
        url=f"https://api.github.com/repos/{owner}/{repo}/pulls",
        headers=headers,
        data=json.dumps(data),
    )
    if resp.status_code == 422:
        err_msg = resp.json()["errors"][0]["message"]
        if "no commits between" in err_msg.lower():
            return None
        prs = list_pull_requests(token, OWNER, REPO)
        for pr in prs:
            if pr["head"]["ref"] == data["head"] and pr["base"]["ref"] == data["base"]:
                return pr
        raise RuntimeError("The existing PR is closed/merged before identified!")
    return resp.json()


def merge_pull_request(token: str, owner: str, repo: str, pr_number: int):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    resp = requests.put(
        url=f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/merge",
        headers=headers,
    )
    if not resp.ok:
        resp.raise_for_status()


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


def update_branch(token: str, branch: str):
    pr = create_pull_request(
        token,
        OWNER,
        REPO,
        {
            "base": branch,
            "head": "dev",
            "title": "Get Upstream Changes",
        },
    )
    if pr is None:
        return
    print(pr)
    merge_pull_request(token, OWNER, REPO, pr["number"])


def main():
    args = parse_args()
    create_pull_request(
        args.token,
        OWNER,
        REPO,
        {
            "base": "main",
            "head": "dev",
            "title": f"Merge dev into main",
        },
    )


if __name__ == "__main__":
    main()
