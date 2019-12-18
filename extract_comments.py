from git import Repo
import re
import os
import argparse


class CommentExtractor:
    reg_py_one = re.compile('(?:#[^\n]*)', re.DOTALL)
    reg_py_mul = re.compile('("""(?:(?!""").)*""")', re.DOTALL)
    # from https://stackoverflow.com/questions/25822749/python-regex-for-matching-single-line-and-multi-line-comments
    reg_java_one = re.compile('(?:\/\/[^\n]*)', re.DOTALL)
    reg_java_mul = re.compile('(\/\*(?:(?!\*\/).)*\*\/)', re.DOTALL)

    count_one_liners = 0
    count_multi_liners = 0


    def get_comments(self, filename):
        content = ''
        with open(filename) as f:
            for line in f.readlines():
                content += line

        one = mul = None
        if lang == 'py':
            one = self.reg_py_one.findall(content)
            mul = self.reg_py_mul.findall(content)
        elif lang == 'java':
            one = self.reg_java_one.findall(content)
            mul = self.reg_java_mul.findall(content)
        self.count_one_liners += len(one)
        self.count_multi_liners += len(mul)
        return one + mul


    def is_empty(self, comment_list):
        if isinstance(comment_list, list):
            return all(map(self.is_empty, comment_list))
        return False


    def traverse_files(self, directory):
        all_comments = []
        if os.path.isfile(directory):
            if directory.endswith('.' + lang):
                all_comments.append(self.get_comments(directory))
            else:
                return []
        else:
            dir_list = None
            try:
                dir_list = os.listdir(directory)
            except:
                return []
            for dire in dir_list:
                dir_comments = self.traverse_files(directory + '/' + dire)
                if not self.is_empty(dir_comments):
                    all_comments.append(dir_comments)
        return all_comments


    def write_to_file(self, repo_dir, comment_list):
        if isinstance(comment_list, list):
            for sublist in comment_list:
                self.write_to_file(repo_dir, sublist)
        else:
            with open(repo_dir + '.txt', 'a') as f:
                f.write(comment_list)


    def get_loc(self, file):
        return sum(1 for line in open(file))

    def get_one_liners(self):
        return self.count_one_liners
    
    def get_mul_liners(self):
        return self.count_multi_liners
    
    def get_number_of_comments(self):
        return self.count_multi_liners + self.count_one_liners


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
extr = CommentExtractor()
all_comments = extr.traverse_files(repo_dir)

# write comments to text file
extr.write_to_file(repo_dir, all_comments)

print('lines of comments:', extr.get_loc(lang + '.txt'))
print('number comments:', extr.get_number_of_comments())
print('one liners:', extr.get_one_liners())
print('multi liners:', extr.get_mul_liners())
