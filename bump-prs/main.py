import os
import requests
import argparse
from dotenv import load_dotenv
from tabulate import tabulate

github_url="https://api.github.com"
orgname="starwit"
author="dependabot[bot]"

def list_prs(org):
    result = {}
    url=github_url + "/search/issues?q=org:" + org + "+type:pr+state:open&per_page=100"
    headers = {}
    headers["Accept"] = "application/vnd.github+json"
    if(TOKEN):
        headers["Authorization"] = "Bearer " + TOKEN
    resp = requests.get(url, headers=headers)
    data = resp.json()
    for pr in data["items"]:
        title = pr["title"]
        author = pr["user"]["login"]
        if author not in result:
            result[author] = []
        result[author].append({
            "title" : title,
            "url" : pr["repository_url"],
            "updated_at" : pr["updated_at"]
        })
    return result

def output_as_table(data, dependabot_only=False):
    rows = []
    for author, prs in data.items():
        if dependabot_only and author != "dependabot[bot]":
            continue
        for pr in prs:
            rows.append([
                author,
                pr["title"],
                pr["url"].split("/")[-1],  # repo name from URL
                pr["updated_at"]
            ])

    # Sort by repo name (index 2), then by author (index 0)
    rows.sort(key=lambda x: (x[2], x[0]))
    
    # Add row numbers with enumerate (starting at 1)
    numbered_rows = [[i+1] + row for i, row in enumerate(rows)]

    table = tabulate(numbered_rows, headers=["#", "Author", "Title", "Repo", "Updated At"], tablefmt="github")
    print(table)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', help='Show only dependabot PRs')
    parser.add_argument('-o', required=True, help='Organization name')
    args = parser.parse_args()
    
    load_dotenv()
    global TOKEN
    TOKEN = os.getenv('TOKEN')
    pr_list = list_prs(args.o)
    output_as_table(pr_list, args.d)


if __name__ == "__main__":
    main()

