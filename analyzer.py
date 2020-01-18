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


    def add_to_dataframe(self, ex, meta_data):

        #sa = SentimentAnalysis(ex)
        #sen = sa.getAvgSentiment()

        new_row = {
            'project': ex.repo_name, 
            'lang': ex.lang, 
            'lines': ex.get_line_count(), 
            'lo-code': ex.get_code_lines_count(),
            'lo-comment': ex.get_comment_lines_count(), 
            'number-comments': ex.get_number_comments(),
            'todo': ex.get_number_comment('todo'),
            'todo-lines': ex.get_comment_line_count('todo'),
            'class': ex.get_number_comment('class'),
            'class-lines': ex.get_comment_line_count('class'),
            'method': ex.get_number_comment('method'),
            'method-lines': ex.get_comment_line_count('method'),
            'header': ex.get_number_comment('header'),
            'header-lines': ex.get_comment_line_count('header'),
            'other': ex.get_number_comment('other'),
            'other-lines': ex.get_comment_line_count('other'),
            'avg-len': ex.get_avg_comment_len(),
            'stars': meta_data['stargazers_count'],
            'forks': meta_data['forks_count'],
            'size': meta_data['size'],
            'subscribers': meta_data['subscribers_count']
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


    def plotStarBarChart(self):
        cpc = pd.DataFrame({'stars': (self.df['stars']).tolist(), 'forks': (self.df['forks']).tolist()}, index=self.df['project'])
        cpc = cpc.sort_values(by='stars', ascending=False)
        pl = cpc.plot.bar(rot=0, title='Stars/Forks on GitHub')
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


    def plotOverviewBarChart(self, col, titel, yaxis):
        comment_java = self.df[self.df.lang == 'java'][col].sum() / len(self.df[self.df.lang == 'java'])
        comment_py = self.df[self.df.lang == 'py'][col].sum() / len(self.df[self.df.lang == 'py'])
        objects = ('Java', 'Python')
        y_pos = np.arange(len(objects))
        plt.bar(y_pos, [comment_java, comment_py], align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.ylabel(yaxis)
        plt.title(titel)
        plt.show()


    def plotAvgCommentCode(self):
        comment_java = (self.df[self.df.lang == 'java']['lo-comment'] / self.df['lo-code']).median()
        comment_py = (self.df[self.df.lang == 'py']['lo-comment'] / self.df['lo-code']).median()

        print(comment_java)
        objects = ('Java', 'Python')
        y_pos = np.arange(len(objects))
        plt.bar(y_pos, [comment_java, comment_py], align='center', alpha=0.5)
        plt.xticks(y_pos, objects)
        plt.title('Average comment/code ratio')
        plt.show()


    def plotOverviewStackedBarChart(self):
        t = self.df.groupby(['lang'])[const.categories].sum()
        t.plot(kind='bar', stacked=True)
        plt.show()


    def plotCommentStarScatter(self):
        y = self.df['lo-comment'] / self.df['lo-code']
        x = self.df['stars']
        plt.scatter(x, y)
        plt.show()

    def plotBoxplot(self, df, col, outliers=True):
        df.boxplot(col, showfliers=outliers)
        plt.show()

def main():
    analyzer = Analyzer()
    df = analyzer.df
    
    df_java = df[df.lang == 'java']
    df_python = df[df.lang == 'py']

    sum_java = df[df.lang == 'java']['lines'].sum()
    print('sum lines java:', sum_java)
    print('number java projects', len(df_java), '\n')

    sum_py = df[df.lang == 'py']['lines'].sum()
    print('sum lines pyhton:', sum_py)
    print('number of python projects', len(df_python), '\n')

    ratio_java = pd.DataFrame({'comment/code': df_java['lo-comment'] / df_java['lo-code']})
    analyzer.plotBoxplot(ratio_java, 'comment/code')
    ratio_py = pd.DataFrame({'comment/code': df_python['lo-comment'] / df_python['lo-code']})
    analyzer.plotBoxplot(ratio_py, 'comment/code')

    analyzer.plotBoxplot(df_java, 'avg-len')
    analyzer.plotBoxplot(df_python, 'avg-len')

    analyzer.plotAvgCommentCode()

    analyzer.plotCommentDistribution('java')
    analyzer.plotCommentDistribution('py')
    
    analyzer.plotOverviewStackedBarChart()
    
    analyzer.plotOverviewBarChart('avg-len', 'Average length of comment', 'length')
    
    analyzer.plotCommentStarScatter()

if __name__ == "__main__":
    main()
