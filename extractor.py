import re
import os

class CommentExtractor:
    # from https://stackoverflow.com/questions/25822749/python-regex-for-matching-single-line-and-multi-line-comments
    reg_py_one = re.compile('(?:#[^\n]*)', re.DOTALL)
    reg_py_mul = re.compile('("""(?:(?!""").)*""")', re.DOTALL)
    reg_java_one = re.compile('(?:\/\/[^\n]*)', re.DOTALL)
    reg_java_mul = re.compile('(\/\*(?:(?!\*\/).)*\*\/)', re.DOTALL)

    comments = dict()

    lang = None
    repo_name = None

    def __init__(self, language, repo):
        self.lang = language  
        self.repo_name = repo
        self.comments.update({'inline': []})
        self.comments.update({'multiline': []})
        self.comments.update({'copyright': []})  
        self.comments.update({'todo': []}) 


    def append_comment(self, comment_list, one):
        for comment in comment_list:
            if 'Copyright' in comment:
                self.comments.get('copyright').append(comment)
            elif 'TODO' in comment:
                self.comments.get('todo').append(comment)
            else:
                if one:
                    self.comments.get('inline').append(comment)
                else:
                    self.comments.get('multiline').append(comment)

    def match_comments(self, file):
        content = ''
        with open(file) as f:
            for line in f.readlines():
                content += line

        one = mul = None
        if self.lang == 'py':
            one = self.reg_py_one.findall(content)
            mul = self.reg_py_mul.findall(content)
        elif self.lang == 'java':
            one = self.reg_java_one.findall(content)
            mul = self.reg_java_mul.findall(content)

        self.append_comment(one, True)
        self.append_comment(mul, False)


    def is_empty(self, comment_list):
        if isinstance(comment_list, list):
            return all(map(self.is_empty, comment_list))
        return False


    def extract_comments(self, directory):
        if os.path.isfile(directory):
            if directory.endswith('.' + self.lang):
                self.match_comments(directory)
            else:
                return []
        else:
            dir_list = None
            try:
                dir_list = os.listdir(directory)
            except:
                return []
            for dire in dir_list:
                self.extract_comments(directory + '/' + dire)


    def write_files(self):
        for key, value in self.comments.items():
            self.write_comments_file(self.comments.get(key), key)


    def write_comments_file(self, comment_list, key):
        if isinstance(comment_list, list):
            for sublist in comment_list:
                self.write_comments_file(sublist, key)
        else:
            with open(self.repo_name + '_' + key + '.txt', 'a') as f:
                f.write(comment_list)
                f.write('\n\n')


    # TODO filter empty comments
    # TODO filter license link in one liners

    def get_comments(self, key):
        return self.comments.get(key)
