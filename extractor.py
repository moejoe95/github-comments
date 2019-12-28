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
    comment_counts = dict()

    categories = ['inline', 'method', 'class', 'todo', 'copyright']

    lang = None
    repo_name = None

    line_count = 0
    code_count = 0
    number_files = 0

    def __init__(self, language, repo):
        self.lang = language  
        self.repo_name = repo

        for cat in self.categories:
            self.comments.update({cat: []})
            self.comment_counts.update({cat: 0})
    

    def get_class_line(self, content, start, it):
        end = start
        c = content[end]
        while c != '\n' and end >= 0 and end < len(content):
            c = content[end]
            end += it
        if end < start:
            return content[end:start:1], end
        return content[start:end:1], end


    def append_comment(self, comment, content, pos, one):   
        if one: # one-line comments
            if 'TODO' in comment:
                self.comment_counts.update({'todo': self.comment_counts['todo']+1})
                self.comments.get('todo').append(comment)
            else:
                self.comment_counts.update({'inline': self.comment_counts['inline']+1})
                self.comments.get('inline').append(comment)
        else: # multi-line comments
            line = None
            if self.lang == 'java':
                line, _ = self.get_class_line(content, pos[1]+1, 1)
            else:
                line, prev = self.get_class_line(content, pos[0]-1, -1)   
                line, _ = self.get_class_line(content, prev, -1)

            newline_count = comment.count('\n') # count number of lines of comment
            if 'class' in line:
                self.comment_counts.update({'class': self.comment_counts['class'] + newline_count})
                self.comments.get('class').append(comment)
            elif 'copyright' in comment.lower():
                self.comment_counts.update({'copyright': self.comment_counts['copyright'] + newline_count})
                self.comments.get('copyright').append(comment)
            else:
                self.comment_counts.update({'method': self.comment_counts['method'] + newline_count})
                self.comments.get('method').append(comment)


    def match_comments(self, file):
        content = ''
        self.number_files += 1
        with open(file) as f:
            for line in f.readlines():
                content += line
                if not line.isspace():
                    self.line_count += 1

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


    def write_files(self, outfile):
        for key, value in self.comments.items():
            self.write_comments_file(self.comments.get(key), key, outfile)


    def write_comments_file(self, comment_list, key, outfile):
        if isinstance(comment_list, list):
            for sublist in comment_list:
                self.write_comments_file(sublist, key, outfile)
        else:
            with open(outfile + '_' + key + '.txt', 'a') as f:
                f.write(comment_list)
                f.write('\n\n')


    def get_comments(self, key):
        return self.comments.get(key)


    def get_all_comments(self):
        return [com for _, com_list in self.comments.items() for com in com_list]


    def get_number_comment(self, key):
        return len(self.comments.get(key))


    def get_number_comments(self):
        return sum([len(v) for _,v in self.comments.items()])


    def get_line_count(self):
        ''' get total lines of files without whitespace lines '''
        return self.line_count


    def get_comment_line_count(self, key):
        return self.comment_counts.get(key)


    def get_comment_lines_count(self):
        ''' get total lines of comments '''
        return sum([v for _,v in self.comment_counts.items()])


    def get_code_lines_count(self):
        ''' get total lines of code '''
        return self.line_count - self.get_comment_lines_count()
