import pandas as pd
from sentiment_analysis import SentimentAnalysis
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


class Analyzer:

    datafile = 'dataframe.csv'
    df = None

    def __init__(self):
        self.df = pd.read_csv(self.datafile, index_col=False)


    def add_to_dataframe(self, ex):
        if self.df['project'].isin([ex.repo_name]).any():
            print(ex.repo_name, 'already in dataframe...\n')
            return

        sa = SentimentAnalysis(ex)
        sen = sa.getAvgSentiment()

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
            'copyright-lines': ex.get_comment_line_count('copyright'),
            'neg': sen['neg'],
            'neu': sen['neu'],
            'pos': sen['pos'],
            'com': sen['compound']
        }
        self.df = self.df.append(new_row, ignore_index=True)
        self.df.to_csv(self.datafile, index=False)


    def print_dataframe(self):
        self.df.sort_values(by=['lang'], inplace=True)
        print(self.df)

def main():
    analyzer = Analyzer()
    df = analyzer.df
    print(df)

    sum_java = df[df.lang == 'java']['lines'].sum()
    print('sum lines java:', sum_java)

    sum_py = df[df.lang == 'py']['lines'].sum()
    print('sum lines pyhton:', sum_py, '\n')

    cpc = pd.DataFrame({'cpc': (df['lo-comment'] / df['lo-code']).tolist()}, index=df['project'])
    cpc = cpc.sort_values(by='cpc', ascending=False)
    pl = cpc.plot.bar(rot=0, title='lines of comment / lines of code')
    pl.set_ylabel('lo-comment / lo-code')
    pl.set_xlabel('projects')
    plt.show()

    sen = df.sort_values(by='com', ascending=False)
    pl = sen.plot.bar(y='com',x='project', rot=0, title='Sentiment Analysis')
    pl.set_ylabel('sentiment compound')
    pl.set_xlabel('projects')
    plt.show()

    print('projects with positive sentiment:')
    print(df[df.com >= 0.05]['project'], '\n')

    print('projects with negative sentiment:')
    print(df[df.com <= -0.05]['project'], '\n')

    print('project with neutral sentiment:')
    print(df[(df.com < 0.05) & (df.com > -0.05)]['project'], '\n')

if __name__ == "__main__":
    main()
