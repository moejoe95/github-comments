from git import Repo
import argparse
import os
import requests
import shutil
import pandas as pd
import OAuth

from extractor import CommentExtractor
from analyzer import Analyzer

lang2ending =  {'Python': 'py', 'Java': 'java'}
git_url = 'https://github.com/'


def get_top_repos(lang, n):
    page_num = n // 30 + 2

    repo_pages = []
    for i in range(1, page_num):
        top_repo_req = requests.get('https://api.github.com/search/repositories?q=language:' 
            + lang + '&sort:stars&sort=desc&page=' + str(i), 
            headers={'Authorization': OAuth.TOKEN})
        top_repos_json = top_repo_req.json()
        repo_pages.append(top_repos_json['items'])

    top_repos = dict()
    i = 0
    for repos in repo_pages:
        for repo in repos:
            top_repos.update({repo['full_name']: lang2ending.get(lang)})
            if i+1 == n:
                return top_repos
            i += 1

    return top_repos

parser = argparse.ArgumentParser()
parser.add_argument('repo', nargs='*')
parser.add_argument("-l", "--lang", help="language")
parser.add_argument("-o", "--out", help="outputfile")
parser.add_argument("-t", "--top", help="get top repositories")
parser.add_argument("-rm", action="store_true", help="remove repo after analyzing")

args = parser.parse_args()

repos = dict()

if len(args.repo) == 0:
    n = 1
    if (args.top):
        n = int(args.top)
    repos = get_top_repos('Python', n)
    repos.update(get_top_repos('Java', n))
else:
    for repo in args.repo:
        repos.update({repo: args.lang})

for repo_path, lang in repos.items():
    out = args.out

    df = pd.read_csv('dataframe.csv', index_col=False)
    if df['project'].isin([repo_path]).any():
        print('repo', repo_path, 'is already in dataframe, continue ...')
        continue

    if os.path.isdir(repo_path):
        print('repo', repo_path, 'already exists in current folder')
    else:
        print('cloning repo into: ' + repo_path)
        Repo.clone_from(git_url + repo_path, repo_path)

    print('collecting comments ...')

    # traverse files in repo and collect comments
    extr = CommentExtractor(lang, repo_path)
    all_comments = extr.extract_comments(repo_path)

    # write comments to text file
    if out:
        extr.write_files(out)

    req_repo = requests.get('https://api.github.com/repos/' + repo_path, 
        headers={'Authorization': OAuth.TOKEN})
    meta_data_repo = req_repo.json()

    an = Analyzer()
    an.add_to_dataframe(extr, meta_data_repo)
    #an.print_dataframe()

    if args.rm:
        print('removing repo', repo_path, '...\n')
        shutil.rmtree(repo_path.split('/')[0])
