import pandas as pd

class Analyzer:

    datafile = 'dataframe.csv'
    df = None

    def __init__(self):
        self.df = pd.read_csv(self.datafile, index_col=False)


    def add_to_dataframe(self, ex):

        if ex.repo_name in self.df['project'].any():
            print(ex.repo_name, 'already in dataframe')
            return

        new_row = {
            'project': ex.repo_name, 
            'lang': ex.lang, 
            'lines': ex.get_line_count(), 
            'lo-code': ex.get_code_lines_count(),
            'lo-comment': ex.get_comment_lines_count(), 
            'todo': ex.get_comment_count('todo'),
            'inline': ex.get_comment_count('inline'),
            'class': ex.get_comment_count('class'),
            'method': ex.get_comment_count('method'),
            'copyright': ex.get_comment_count('copyright')
        }
        self.df = self.df.append(new_row, ignore_index=True)
        self.df.to_csv(self.datafile, index=False)


    def print_dataframe(self):
        print(self.df)

