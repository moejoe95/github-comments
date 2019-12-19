from git import Repo
import argparse
import os

from extractor import CommentExtractor


parser = argparse.ArgumentParser()
parser.add_argument('repo')
parser.add_argument("-l", "--lang", help="language")

args = parser.parse_args()
    
repo_path = args.repo
lang = args.lang

git_url = 'https://github.com/'
repo_dir = str.split(git_url + repo_path, '/')
repo_dir = str.split(repo_dir[len(repo_dir)-1], '.')
repo_dir = repo_dir[0]

if os.path.isdir(repo_dir):
    print('repo', repo_dir, 'already exists')
else:
    print('cloning repo into: ' + repo_dir)
    Repo.clone_from(git_url + repo_path, repo_dir)

print('collecting comments in ', repo_dir, '\n')

# traverse files in repo and collect comments
extr = CommentExtractor(lang)
all_comments = extr.extract_comments(repo_dir)

# write comments to text file
extr.write_to_file(repo_dir, all_comments)

print('lines of comments:', extr.get_loc(repo_dir + '.txt'))
print('number comments:', extr.get_number_of_comments())
print('one liners:', extr.get_one_liners())
print('multi liners:', extr.get_mul_liners())
