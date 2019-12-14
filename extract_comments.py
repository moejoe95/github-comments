from git import Repo
import re
import os
import argparse

reg_py = re.compile('(?:#[^\n]*|"""(?:(?!""").)*""")', re.DOTALL)
# from https://stackoverflow.com/questions/25822749/python-regex-for-matching-single-line-and-multi-line-comments
reg_java = re.compile('(?:\/\/[^\n]*|\/\*(?:(?!\*\/).)*\*\/)', re.DOTALL)


def get_comments(filename):
    content = ''
    with open(filename) as f:
        for line in f.readlines():
            content += line

    if lang == 'py':
        return reg_py.findall(content)
    elif lang == 'java':
        return reg_java.findall(content)


def is_empty(comment_list):
    if isinstance(comment_list, list):
        return all(map(is_empty, comment_list))
    return False


def traverse_files(directory):
    all_comments = []
    if os.path.isfile(directory):
        if directory.endswith('.' + lang):
            all_comments.append(get_comments(directory))
        else:
            return []
    else:
        dir_list = None
        try:
            dir_list = os.listdir(directory)
        except:
            return []
        for dire in dir_list:
            dir_comments = traverse_files(directory + '/' + dire)
            if not is_empty(dir_comments):
                all_comments.append(dir_comments)
    return all_comments


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

all_comments = traverse_files(repo_dir)
for comments in all_comments:
    print(comments)
