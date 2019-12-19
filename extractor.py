import re
import os

class CommentExtractor:
    # from https://stackoverflow.com/questions/25822749/python-regex-for-matching-single-line-and-multi-line-comments
    reg_py_one = re.compile('(?:#[^\n]*)', re.DOTALL)
    reg_py_mul = re.compile('("""(?:(?!""").)*""")', re.DOTALL)
    reg_java_one = re.compile('(?:\/\/[^\n]*)', re.DOTALL)
    reg_java_mul = re.compile('(\/\*(?:(?!\*\/).)*\*\/)', re.DOTALL)

    count_one_liners = 0
    count_multi_liners = 0

    lang = 'py'

    def __init__(self, language):
        self.lang = language        


    def get_comments(self, filename):
        content = ''
        with open(filename) as f:
            for line in f.readlines():
                content += line

        one = mul = None
        if self.lang == 'py':
            one = self.reg_py_one.findall(content)
            mul = self.reg_py_mul.findall(content)
        elif self.lang == 'java':
            one = self.reg_java_one.findall(content)
            mul = self.reg_java_mul.findall(content)
        self.count_one_liners += len(one)
        self.count_multi_liners += len(mul)
        return one + mul


    def is_empty(self, comment_list):
        if isinstance(comment_list, list):
            return all(map(self.is_empty, comment_list))
        return False


    def extract_comments(self, directory):
        all_comments = []
        if os.path.isfile(directory):
            if directory.endswith('.' + self.lang):
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
                dir_comments = self.extract_comments(directory + '/' + dire)
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
                f.write('\n\n')


    def get_loc(self, file):
        return sum(1 for line in open(file)) - self.get_number_of_comments() # subtract newlines

    def get_one_liners(self):
        return self.count_one_liners
    
    def get_mul_liners(self):
        return self.count_multi_liners
    
    def get_number_of_comments(self):
        return self.count_multi_liners + self.count_one_liners
