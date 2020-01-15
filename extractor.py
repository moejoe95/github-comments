import re
import os
from re import finditer

# constants
categories = ['method', 'class', 'header','todo', 'other']
METHOD = 'method'
CLASS = 'class'
TODO = 'todo'
HEADER = 'header'
OTHER = 'other'
JAVA = 'java'
PYTHON = 'py'


class CommentExtractor:
    # from https://stackoverflow.com/questions/25822749/python-regex-for-matching-single-line-and-multi-line-comments
    
    reg_py_one = re.compile('(?:#[^\n]*)', re.DOTALL)
    reg_py_mul = re.compile('("""(?:(?!""").)*""")', re.DOTALL)

    reg_java_one = re.compile('(?:\/\/[^\n]*)', re.DOTALL)
    reg_java_mul = re.compile('(\/\*(?:(?!\*\/).)*\*\/)', re.DOTALL)

    reg_java_method = re.compile('^((private|public|protected)\s)?.+\(.*', re.DOTALL)
    reg_py_method = re.compile('.*[^\(-]\)\s*:.*', re.DOTALL)
    reg_java_class = re.compile('^((private|protected|public)\s)?((static|abstract|final)\s)?(class|@?interface|enum)\s.*', re.DOTALL)
    reg_py_class = re.compile('^class\s.*:$', re.DOTALL)

    comments = dict()
    comment_counts = dict()

    lang = None
    repo_name = None

    line_count = 0
    code_count = 0
    number_files = 0

    def __init__(self, language, repo):
        self.lang = language  
        self.repo_name = repo

        for cat in categories:
            self.comments.update({cat: []})
            self.comment_counts.update({cat: 0})
    

    def match_class_or_method(self, line):
        return (not self.reg_java_class.match(line)  \
        and not self.reg_java_method.match(line) \
        ) \
        and line


    def get_prev_or_next_code_line(self, content, start, it, stopchar='\n'):
        end = start
        if end >= len(content):
            end = len(content)-1
        c = content[end]
        while c != stopchar and end >= 0 and end < len(content):
            c = content[end]
            end += it
        if end <= start:
            return content[end+1:start+1], end
        line = content[start:end+1]
        # skip annotations in java code
        line = line.strip()
        if line.startswith('@'):
            while self.match_class_or_method(line):
                line, prev = self.get_prev_or_next_code_line(content, end, it)
                end = prev
        return line, end


    def get_code_line(self, content, pos):
        line = None
        if self.lang == JAVA:
            line, _ = self.get_prev_or_next_code_line(content, pos[1]+1, 1)
        else:
            line, prev = self.get_prev_or_next_code_line(content, pos[0]-1, -1)   
            line, _ = self.get_prev_or_next_code_line(content, prev-1, -1)
        return line.strip()
        

    def append_comment(self, comment, content, pos, one, file):   
        newline_count = comment.count('\n') # count number of lines of comment
        line = self.get_code_line(content, pos)

        # header comment
        if pos[0] <= 1: 
            self.comment_counts.update({HEADER: self.comment_counts[HEADER] + newline_count})
            self.comments.get(HEADER).append(comment)

        # todo comments
        elif TODO.upper() in comment: 
            self.comment_counts.update({TODO: self.comment_counts[TODO]+1})
            self.comments.get(TODO).append(comment)

        # other one line comment
        elif one:
            self.comment_counts.update({OTHER: self.comment_counts[OTHER] + newline_count})
            self.comments.get(OTHER).append(comment)

        # class or interface comments
        elif self.reg_java_class.match(line) or self.reg_py_class.match(line): 
            self.comment_counts.update({CLASS: self.comment_counts[CLASS] + newline_count})
            self.comments.get(CLASS).append(comment)

        # method comment
        elif self.reg_java_method.match(line) or self.reg_py_method.match(line): 
            self.comment_counts.update({METHOD: self.comment_counts[METHOD] + newline_count})
            self.comments.get(METHOD).append(comment)

        # other comments
        else: 
            if line.startswith('#'):
                self.comment_counts.update({HEADER: self.comment_counts[HEADER] + newline_count})
                self.comments.get(HEADER).append(comment)
            else:
                self.comment_counts.update({OTHER: self.comment_counts[OTHER] + newline_count})
                self.comments.get(OTHER).append(comment)


    def match_comments(self, file):
        content = ''
        self.number_files += 1
        with open(file, encoding='utf8') as f:
            for line in f.readlines():
                content += line
                if not line.isspace():
                    self.line_count += 1

        reg_one = self.reg_py_one if self.lang == PYTHON else self.reg_java_one
        reg_mul = self.reg_py_mul if self.lang == PYTHON else self.reg_java_mul

        it = finditer(reg_one, content)
        i = 0
        prev_pos = -1
        com = ''
        comments = []
        for match in it:
            if i == 0:
                prev_pos = match.regs[0][0]-1
            if prev_pos+2 >= match.regs[0][0]:
                com += match.group() + '\n'
            else:
                if com == '':
                    comments.append([content[match.regs[0][0]:match.regs[0][1]], match.regs[0][0], match.regs[0][1]])
                else:
                    comments.append([com, 0, match.regs[0][1]])
                com = ''

            prev_pos = match.regs[0][1]
            i += 1

        for com, start, end in comments:
            self.append_comment(com, content, [start, end], True, file)

        for match in finditer(reg_mul, content):
            self.append_comment(match.group(), content, match.span(), False, file)


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

    def get_avg_comment_len(self):
        total_len = 0
        i = 0
        for com in self.get_all_comments():
            total_len += len(com)
            i += 1
        if i == 0:
            return 0
        return total_len / i

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
