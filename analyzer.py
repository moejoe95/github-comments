import pandas as pd
from sentiment_analysis import SentimentAnalysis
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import extractor as const


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
            'header': ex.get_number_comment('header'),
            'header-lines': ex.get_comment_line_count('header'),
            'other': ex.get_number_comment('other'),
            'other-lines': ex.get_comment_line_count('other'),
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

    def plotCommentCodeBarChart(self, comments, title):
        cpc = pd.DataFrame({'cpc': (comments / self.df['lo-code']).tolist()}, index=self.df['project'])
        cpc = cpc.sort_values(by='cpc', ascending=False)
        pl = cpc.plot.bar(rot=0, title=title)
        pl.set_xlabel('projects')
        plt.show()

    def plotSentimentBarChart(self):
        sen = self.df.sort_values(by='com', ascending=False)
        pl = sen.plot.bar(y='com',x='project', rot=0, title='Sentiment Analysis')
        pl.set_ylabel('sentiment compound')
        pl.set_xlabel('projects')
        plt.show()

    def plotCommentDistribution(self, lang):
        comment_df = self.df[self.df.lang == lang][const.categories].sum()
        pl = comment_df.plot.pie()
        plt.show()

    def plotOverviewBarChart(self):
        comment_java = self.df[self.df.lang == 'java']['lo-comment'].sum()
        comment_py = self.df[self.df.lang == 'py']['lo-comment'].sum()
        objects = ('Java', 'Python')
        y_pos = np.arange(len(objects))

        plt.bar(y_pos, [comment_java, comment_py], align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel('lines')
        plt.title('Total lines of comments')

        plt.show()

    def plotOverviewStackedBarChart(self):

        test5 = self.df.groupby(['lang'])[const.categories].sum()

        test5.plot(kind='bar', stacked=True)
        plt.show()

def main():
    analyzer = Analyzer()
    df = analyzer.df
    print(df)

    sum_java = df[df.lang == 'java']['lines'].sum()
    print('sum lines java:', sum_java)

    sum_py = df[df.lang == 'py']['lines'].sum()
    print('sum lines pyhton:', sum_py, '\n')

    analyzer.plotCommentCodeBarChart(df['lo-comment'], 'lo-comments / lo-code')
    analyzer.plotCommentCodeBarChart(df['lo-comment']-df['header-lines'], 'lo-comments / lo-code without header comments')
    analyzer.plotSentimentBarChart()

    analyzer.plotCommentDistribution('java')
    analyzer.plotCommentDistribution('py')

    analyzer.plotOverviewBarChart()
    analyzer.plotOverviewStackedBarChart()

    print('projects with positive sentiment:')
    print(df[df.com >= 0.05]['project'], '\n')

    print('projects with negative sentiment:')
    print(df[df.com <= -0.05]['project'], '\n')

    print('project with neutral sentiment:')
    print(df[(df.com < 0.05) & (df.com > -0.05)]['project'], '\n')

if __name__ == "__main__":
    main()
