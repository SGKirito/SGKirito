import os
import re
from datetime import datetime
import requests

# CONFIGURATION: Change these to your details!
USER = os.environ.get("GITHUB_USER", "YOUR_GITHUB_USERNAME")
JOIN_DATE = "2022-01-15"  # Your GitHub join date (YYYY-MM-DD)
TOKEN = os.environ.get("ACCESS_TOKEN")

headers = {"Authorization": f"bearer {TOKEN}"} if TOKEN else {}

def get_uptime():
    start = datetime.strptime(JOIN_DATE, "%Y-%m-%d")
    now = datetime.now()
    diff = now - start
    years = diff.days // 365
    days = diff.days % 365
    return f"{years} years, {days} days"

def get_stats():
    query = """
    query($user: String!) {
      user(login: $user) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazerCount
          }
        }
        contributionsCollection {
          totalCommitContributions
        }
      }
    }
    """
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"user": USER}},
            headers=headers
        ).json()
        
        user_data = response["data"]["user"]
        repos = user_data["repositories"]["totalCount"]
        stars = sum(repo["stargazerCount"] for repo in user_data["repositories"]["nodes"])
        commits = user_data["contributionsCollection"]["totalCommitContributions"]
        return repos, stars, commits
    except Exception as e:
        print(f"GraphQL error: {e}")
        return 20, 100, 1000

def update_svg(filename, uptime, repos, stars, commits):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r'id="uptime">[^<]+<', f'id="uptime">{uptime}<', content)
    content = re.sub(r'id="repos">[^<]+<', f'id="repos">{repos}<', content)
    content = re.sub(r'id="stars">[^<]+<', f'id="stars">{stars}<', content)
    content = re.sub(r'id="commits">[^<]+<', f'id="commits">{commits:,}<', content)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    uptime = get_uptime()
    repos, stars, commits = get_stats()
    update_svg("dark_mode.svg", uptime, repos, stars, commits)
    update_svg("light_mode.svg", uptime, repos, stars, commits)
