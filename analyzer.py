import pandas as pd

class Analyzer:

    datafile = 'dataframe.csv'
    df = None

    def __init__(self):
        self.df = pd.read_csv(self.datafile, index_col=False)


    def add_to_dataframe(self, ex):
        if self.df['project'].isin([ex.repo_name]).any():
            print(ex.repo_name, 'already in dataframe...\n')
            return

        new_row = {
            'project': ex.repo_name, 
            'lang': ex.lang, 
            'lines': ex.get_line_count(), 
            'lo-code': ex.get_code_lines_count(),
            'lo-comment': ex.get_comment_lines_count(), 
            'number-comments': ex.get_number_comments(),
            'todo': ex.get_number_comment('todo'),
            'todo-lines': ex.get_comment_line_count('todo'),
            'inline': ex.get_number_comment('inline'),
            'inline-lines': ex.get_comment_line_count('inline'),
            'class': ex.get_number_comment('class'),
            'class-lines': ex.get_comment_line_count('class'),
            'method': ex.get_number_comment('method'),
            'method-lines': ex.get_comment_line_count('method'),
            'copyright': ex.get_number_comment('copyright'),
            'copyright-lines': ex.get_comment_line_count('copyright')
        }
        self.df = self.df.append(new_row, ignore_index=True)
        self.df.to_csv(self.datafile, index=False)


    def print_dataframe(self):
        self.df.sort_values(by=['lang'], inplace=True)
        print(self.df)


analyzer = Analyzer()
df = analyzer.df
print(df)

sum_java = df[df.lang == 'java']['lines'].sum()
print('sum lines java:', sum_java)

sum_py = df[df.lang == 'py']['lines'].sum()
print('sum lines pyhton:', sum_py)
