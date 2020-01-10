from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
'''
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. 
Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
'''


def add_up(sentiments, key):
    return sum([sen[key] for sen in sentiments])


def clean_comment(comment):
    comment = comment.replace('\n', ' ')
    comment = comment.replace('/**', '')
    comment = comment.replace('/*', '')
    comment = comment.replace('*/', '')
    comment = comment.replace('*', '')
    comment = comment.replace('//', '')
    comment = comment.replace("'''", '')
    comment = comment.replace('#', '')
    comment = comment.strip()
    return comment

class SentimentAnalysis:

    sent_analyzer = SentimentIntensityAnalyzer()
    categories = ['neg', 'neu', 'pos', 'compound']

    def __init__(self, ex):
        self.extractor = ex


    def getAvgSentiment(self):
        comments = self.extractor.get_all_comments()
        sentiments = []
        pos_max = -1
        pos_max_pos = -1
        for i, com in enumerate(comments):
            com = clean_comment(com)
            sent_score = self.sent_analyzer.polarity_scores(com)
            sentiments.append(sent_score)
            if sent_score['pos'] > pos_max:
                pos_max = sent_score['pos']
                pos_max_pos = i
        res = dict()        
        for cat in self.categories:
            res.update({cat: add_up(sentiments, cat) / len(sentiments)})
        return res
