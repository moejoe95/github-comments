from git import Repo
import re
import os
import sys

regex = re.compile('(?:#[^\n]*|"""(?:(?!""").)*""")', re.DOTALL)


def get_comments(filename):
    content = ''
    with open(filename) as f:
        for line in f.readlines():
            content += line

    return regex.findall(content)


def is_empty(comment_list):
    if isinstance(comment_list, list):
        return all(map(is_empty, comment_list))
    return False


def collect_files(directory):
    all_comments = []
    if os.path.isfile(directory):
        if directory.endswith('.py'):
            all_comments.append(get_comments(directory))
        else:
            return []
    else:
        for dire in os.listdir(directory):
            dir_comments = collect_files(directory + '/' + dire)
            if not is_empty(dir_comments):
                all_comments.append(dir_comments)
    return all_comments

#def remove_empty(all_comments):


repo_path = None
if len(sys.argv) < 2:
    print('invalid number of arguments given')
    sys.exit(-1)
else:
    repo_path = sys.argv[1]

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

all_comments = collect_files(repo_dir)
for comments in all_comments:
    print(comments)
