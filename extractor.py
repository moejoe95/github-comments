import re
import os
from re import finditer


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
        self.comments.update({'method': []})
        self.comments.update({'copyright': []})  
        self.comments.update({'todo': []}) 
        self.comments.update({'class': []})

    
    def get_class_line(self, content, start, end, it):
        c = content[end]
        while(c != '\n'):
            c = content[start]
            start += it
        return content[start:end:1], start

    def append_comment(self, comment, content, pos, one):        
        if one:
            if 'TODO' in comment:
                self.comments.get('todo').append(comment)
            else:
                self.comments.get('inline').append(comment)
        else:
            line = None
            if self.lang == 'java':
                line, _ = self.get_class_line(content, 0, pos[1], 1)
            else:
                line, prev = self.get_class_line(content, pos[0], pos[0], -1)   
                line, _ = self.get_class_line(content, prev, prev, -1)

            if 'class' in line:
                self.comments.get('class').append(comment)
            elif 'copyright' in comment.lower():
                self.comments.get('copyright').append(comment)
            else:
                self.comments.get('method').append(comment)


    def match_comments(self, file):
        content = ''
        with open(file) as f:
            for line in f.readlines():
                content += line

        reg_one = self.reg_py_one if self.lang == 'py' else self.reg_java_one
        reg_mul = self.reg_py_mul if self.lang == 'py' else self.reg_java_mul

        for match in finditer(reg_one, content):
            self.append_comment(match.group(), content, match.span(), True)
        for match in finditer(reg_mul, content):
            self.append_comment(match.group(), content, match.span(), False)


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


    def get_comments(self, key):
        return self.comments.get(key)
