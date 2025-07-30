from dataclasses import dataclass
from typing import List, Any
import sys
import os
import argparse
import requests
from fastmcp import FastMCP, Context


def main():
    parser = argparse.ArgumentParser(
        description="Goodreads MCP CLI - Interface for Goodreads integration"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auth command
    auth_parser = subparsers.add_parser("auth", help="Authenticate with Goodreads")
    auth_parser.add_argument("--email", required=True, help="Email address")
    auth_parser.add_argument("--password", required=True, help="Password")
    auth_parser.add_argument("--dax-auth", required=True, help="DAX Auth token")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract books by profile ID")
    extract_parser.add_argument("--profile-id", required=True, help="Profile ID")
    extract_parser.add_argument("--dax-auth", required=True, help="DAX Auth token")

    args = parser.parse_args()

    if args.command == "auth":
        try:
            response = auth(args.email, args.password, args.dax_auth)
            print(f"Authenticated! Profile ID: {response.profile_id}")
            print(f"Found {len(response.bundles)} books")
            for bundle in response.bundles:
                print(f"- {bundle.title} by {bundle.author} (★{bundle.rating})")
        except AuthException as e:
            print(f"Auth failed: {e}")
            sys.exit(1)
            
    elif args.command == "extract":
        try:
            response = extract(args.profile_id, args.dax_auth)
            print(f"Extracted books for profile: {response.profile_id}")
            print(f"Found {len(response.bundles)} books")
            for bundle in response.bundles:
                print(f"- {bundle.title} by {bundle.author} (★{bundle.rating})")
        except AuthException as e:
            print(f"Extract failed: {e}")
            sys.exit(1)
            
    else:
        mcp()




@dataclass()
class Bundle(object):
    cover: str
    title: str
    author: str
    rating: float


@dataclass
class AuthResponse(object):
    profile_id: str
    bundles: List[Bundle]


class AuthException(Exception):
    msg: str


class AuthError(AuthException):
    def __init__(self, msg):
        self.msg = msg


# HOST = "https://api.getgather.studio"
HOST = "https://api.getgather.dev"
# HOST = "http://127.0.0.1:8000"


def auth(email: str, password: str, dax_auth: str) -> AuthResponse:
    payload = {
        "platform": "local-bundle",
        "framework": "patchright",
        "browser": "chromium",
        "brand_name": "goodreads",
        "state": {
            "inputs": {
                "email": email,
                "password": password,
            }
        },
    }

    response = requests.post(f"{HOST}/auth/goodreads", json=payload, headers={
        "Authorization": f"Bearer {dax_auth}"
    })
    response_json = response.json()

    if response.status_code != 200:
        raise AuthError(response.text)

    error_msg = response_json["state"]["error"]
    if error_msg:
        raise AuthError(msg=error_msg)

    profile_id = response_json["profile_id"]
    bundles = get_bundle(response_json["extract_result"]["bundles"])
    return AuthResponse(profile_id=profile_id, bundles=bundles)


def extract(profile_id: str, dax_auth: str) -> AuthResponse:
    payload = {
        "profile_id": profile_id,
        "platform": "local-bundle",
        "framework": "patchright",
        "browser": "chromium",
        "brand_name": "goodreads",
        "state": {},
    }

    response = requests.post(f"{HOST}/extract/goodreads", json=payload, headers={
        "Authorization": f"Bearer {dax_auth}"
    })
    response_json = response.json()

    if response.status_code != 200:
        raise AuthError(response.text)

    error_msg = response_json["state"]["error"]
    if error_msg:
        raise AuthError(msg=error_msg)

    profile_id = response_json["profile_id"]
    bundles = get_bundle(response_json["extract_result"]["bundles"])
    return AuthResponse(profile_id=profile_id, bundles=bundles)


def get_bundle(bundles: List[Any]) -> List[Bundle]:
    bundles_response = []

    for bundle in bundles:
        if not isinstance(bundle["content"], list):
            continue

        for content in bundle["content"]:
            bundles_response.append(
                Bundle(
                    cover=content["cover"],
                    title=content["title"],
                    author=content["author"],
                    rating=float(content["rating"]),
                )
            )

    return bundles_response


def mcp():
    mcp_server = FastMCP("Goodreads MCP")
    
    def get_auth_response():
        """Helper function to get cached auth response or authenticate if needed."""
        email = os.getenv("GOODREADS_EMAIL")
        password = os.getenv("GOODREADS_PASSWORD")
        dax_auth = os.getenv("DAX_AUTH")
        
        if not email or not password:
            raise AuthError("GOODREADS_EMAIL and GOODREADS_PASSWORD environment variables must be set")
        
        if not dax_auth:
            raise AuthError("DAX_AUTH environment variable must be set")
            
        return auth(email, password, dax_auth)
    
    @mcp_server.tool()
    def goodreads_auth() -> dict:
        """
        Authenticate with Goodreads using configured credentials and retrieve user's books.
        Credentials should be set via environment variables GOODREADS_EMAIL, GOODREADS_PASSWORD, and DAX_AUTH.
        
        Returns:
            Dictionary containing profile_id and list of books
        """
        try:
            response = get_auth_response()
            return {
                "profile_id": response.profile_id,
                "books": [
                    {
                        "title": bundle.title,
                        "author": bundle.author,
                        "rating": bundle.rating,
                        "cover": bundle.cover
                    }
                    for bundle in response.bundles
                ]
            }
        except AuthException as e:
            return {"error": str(e.msg)}
    
    @mcp_server.tool()
    def goodreads_extract(profile_id: str) -> dict:
        """
        Extract books from a Goodreads profile by profile ID.
        Requires DAX_AUTH environment variable to be set.
        
        Args:
            profile_id: The Goodreads profile ID
            
        Returns:
            Dictionary containing profile_id and list of books
        """
        dax_auth = os.getenv("DAX_AUTH")
        
        if not dax_auth:
            return {"error": "DAX_AUTH environment variable must be set"}
            
        try:
            response = extract(profile_id, dax_auth)
            return {
                "profile_id": response.profile_id,
                "books": [
                    {
                        "title": bundle.title,
                        "author": bundle.author,
                        "rating": bundle.rating,
                        "cover": bundle.cover
                    }
                    for bundle in response.bundles
                ]
            }
        except AuthException as e:
            return {"error": str(e.msg)}
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
