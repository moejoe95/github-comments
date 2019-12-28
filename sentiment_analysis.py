from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
'''
Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. 
Eighth International Conference on Weblogs and Social Media (ICWSM-14). Ann Arbor, MI, June 2014.
'''
class SentimentAnalysis:

    sent_analyzer = SentimentIntensityAnalyzer()
    categories = ['neg', 'neu', 'pos', 'compound']

    def __init__(self, ex):
        self.extractor = ex

    def add_up(self, sentiments, key):
        return sum([sen[key] for sen in sentiments])

    def getAvgSentiment(self):
        comments = self.extractor.get_all_comments()
        sentiments = []
        for com in comments:
            sent_score = self.sent_analyzer.polarity_scores(com)
            sentiments.append(sent_score)

        res = dict()        
        for cat in self.categories:
            res.update({cat: self.add_up(sentiments, cat) / len(sentiments)})

        return res
