import os
import requests
import argparse
from dotenv import load_dotenv
from tabulate import tabulate
import pandas as pd

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

def output_as_table(data, dependabot_only=False, show_url=False):
    rows = []
    for author, prs in data.items():
        if dependabot_only and author != "dependabot[bot]":
            continue
        for pr in prs:
            row = [
                author,
                pr["title"],
                pr["url"].split("/")[-1],  # repo name from URL
                pr["updated_at"]
            ]
            if show_url:
                row.append(pr["url"])
            rows.append(row)

    # Sort by repo name (index 2), then by author (index 0)
    rows.sort(key=lambda x: (x[2], x[0]))
    
    # Add row numbers with enumerate (starting at 1)
    numbered_rows = [[i+1] + row for i, row in enumerate(rows)]
    df = pd.DataFrame(numbered_rows)
    columns = ["#", "Author", "Title", "Repo", "Updated At"]
    if show_url:
        columns.append("URL")
    df.columns = columns
    markdown_table = df.to_markdown(index=False)
    print(markdown_table)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', help='Show only dependabot PRs')
    parser.add_argument('-o', required=True, help='Organization name')
    parser.add_argument('-url', action='store_true', help='Show URL column')
    args = parser.parse_args()
    
    load_dotenv()
    global TOKEN
    TOKEN = os.getenv('TOKEN')
    pr_list = list_prs(args.o)
    output_as_table(pr_list, args.d, args.url)


if __name__ == "__main__":
    main()

