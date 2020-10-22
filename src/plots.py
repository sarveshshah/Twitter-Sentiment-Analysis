import pandas as pd
import matplotlib.pyplot as plt

def get_plots(tweets):

    """
        Function returns set of predefined plots to output directory
    """
    sample = tweets.groupby(['hour_of_day','sentiment'])[['sentiment']].count()
    sample['sentiment_perc'] = sample.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))

    fig1 = plt.figure(figsize=(10*2, 5))
    ax = fig1.add_subplot(121)

    palette = plt.get_cmap('Oranges')

    ind = np.arange(len(sample.index.levels[0]))  # the x locations for the groups
    width = 0.2   # the width of the bars

    rects1 = ax.bar(ind, sample['sentiment_perc'].loc[:,'negative'], width, color=palette(175))
    rects2 = ax.bar(ind+width, sample['sentiment_perc'].loc[:,'neutral'], width, color=palette(120))
    rects3 = ax.bar(ind+width*2, sample['sentiment_perc'].loc[:,'positive'], width, color=palette(100))

    ax.set_title('Sentiment Score for Tweets by Hour of Day'.format())
    ax.set_ylabel('Sentiment Score')
    ax.set_xlabel('Hour of Day')
    ax.set_xticks(ind + width)
    ax.set_xticklabels([x.capitalize() for x in sample.index.levels[0]])

    ax.legend((rects1[0], rects2[0], rects3[0]), 
              (['Negative','Neutral','Positive']))

    # ------------------------------
    
    sample = tweets.groupby(['sentiment','hour_of_day'])[['sentiment_score']].mean()
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(7,7))

    ax1.plot(sample.loc['negative'], label='Negative')
    ax1.legend()
    ax2.plot(sample.loc['positive'], label='Positive')
    ax2.legend()
    
    return fig1, fig2