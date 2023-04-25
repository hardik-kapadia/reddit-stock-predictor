from flair.data import Sentence
from flair.models import TextClassifier
import flair
import numpy as np
import pandas as pd
import re
import nltk

from reddit import reddit_api
from models import RedditTextPost, Stock
from get_stocks import get_current_stock_price, get_stock, get_stock_from_symbol

import factor as fact
import datetime as DT

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

from reddit import reddit_api
import yaml

with open("auth.yaml", "r") as yamlfile:
    temp_reddit_auth_data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    reddit_auth_creds = temp_reddit_auth_data["REDDIT"]

reddit = reddit_api.get_instance(
    reddit_auth_creds["CLIENT_ID"],
    reddit_auth_creds["CLIENT_SECRET"],
    "<Epic:App:1.0>",
    reddit_auth_creds["USERNAME"],
    reddit_auth_creds["PASSWORD"],
)

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("punkt")
nltk.download("omw-1.4")


def get_data(post):
    _data = post.get_data()
    return _data


class process:
    def __init__(self, df):
        
        # print(df.head())
        self.df = df

    def noise_removal(self, sentence):
        for i in range(len(sentence)):
            sentence[i] = sentence[i].lower()
            sentence[i] = re.sub(r"\W", " ", sentence[i])
            sentence[i] = re.sub(r"\d", " ", sentence[i])  # removes digits
            sentence[i] = re.sub(r"\s+", " ", sentence[i])  # removes spaces
            words = nltk.word_tokenize(sentence[i])
            new = []
            for word in words:
                if word not in stopwords.words("english"):
                    new.append(word)
            sentence[i] = " ".join(new)
        return sentence[0]

    def lemmetization(self, tweet):
        df = self.df
        lem = WordNetLemmatizer()

        for i in range(len(df["text"])):
            words = nltk.word_tokenize(df["text"][i])
            words = [lem.lemmatize(word, pos="v") for word in words]
            df["text"][i] = " ".join(words)

    def predictionsentiment(self, post):
        classifier = TextClassifier.load("en-sentiment")
        sentence = Sentence(post)
        # print(tweet)
        classifier.predict(sentence)
        x = str(sentence.labels[0])
        y = x.split(" ")
        z = float(y[-1][1:-1])
        if str(y[-2]) == "POSITIVE":
            return z
        else:
            return z * -1


def get_initial_df(posts):
    df = pd.DataFrame()

    for i in posts:
        post = get_data(i)
        df = df._append(post, ignore_index=True)

    return df


def get_formatted_df(df):
    processor = process(df)
    df["text"] = df["text"].apply(lambda x: processor.noise_removal([x]))
    df["text"].apply(lambda x: processor.lemmetization(x))
    df["Probability"] = df["text"].apply(lambda x: processor.predictionsentiment(x))

    return df


# def get_daily_scores(df, stock__):
#     print(df)
#     print("\n\n")
#     print(stock__.history)

subreddit_name='wallstreetbets+IndianStockMarket'

def get_score(_stock_):
    
    # print(_stock_.words)
    posts = reddit.get_text_posts(subreddit_name=subreddit_name,query=_stock_.words,limit=100)
    
    print(len(posts))
    
    df = get_initial_df(posts)
    df = get_formatted_df(df)

    df["score"] = df["Probability"] * (
        (df["upvotes"] * fact.UPVOTE_COEF)
        + (df["comment_count"] * fact.COMMENT_COEF)
        + (df["upvote_to_comment_ratio"] * fact.UPVOTE_TO_COMMENT_RATIO_COEF)
        + (df["upvote_ratio"] * fact.UPVOTE_RATIO)
    )

    df2 = df.groupby(["created_at"])["score"].sum()
    
    print('\n\n-----------------------------------')
    
    print(df2)

    df3 = df2.to_dict()

    print('\n\n\n-----------------------------------------------\n\n\n')
    print(df3)
    print('\n\n\n-----------------------------------------------\n\n\n')

    hist = _stock_.history
    hist["gain"] = hist["Close"] - hist["Open"]

    print(hist)

    prediction = False

    latest_avg = 0
    try:
        latest_avg = float(df3[str(DT.date.today())]) + float(
            df3[str(DT.date.today() - DT.timedelta(days=1))]
        )
    except KeyError:
        print("Got the error")
        latest_avg = float(df3[str(DT.date.today() - DT.timedelta(days=2))]) * 2

    print("\n\n Latest avg: ", latest_avg, "\n\n")
    prediction = latest_avg > 0
    count = 0

    avg = 0

    # mult = 1

    in_favour = 0
    against = 0

    for i, row in hist.iterrows():
        dt = str(i)[:10]
        gain = float(row["gain"])
        try:
            social_media_score = float(df3[dt])
        except KeyError:
            continue

        x = gain / social_media_score

        if x > 0:
            print("adding to favor")
            in_favour += 1
        else:
            print("adding t against")
            against += 1

        avg += abs(x)
        count += 1

        print(dt, gain, social_media_score, x)

    print("count is: ", count)
    print("and herrreeee's Johny: ", in_favour, against)

    if in_favour > against:
        mult = in_favour / count
    else:
        print("\n\nway down we go\n\n")
        mult = against / count
        mult *= -1

    avg = avg / count

    print("mult is", mult)

    result = latest_avg * avg * mult

    print("\n\n\n------------------\navg is", avg)

    print("Predicted gain:", result)

    closing_price = 0
    current_price = get_current_stock_price(_stock_.symbol)
    if current_price == 0:
        m = hist["Close"]
        closing_price = m[-1]
        current_price = closing_price

    print("Latest Price:", current_price)

    future_price = current_price + result
    print("Predicted Price: %.2f" % future_price)

    return result, future_price, current_price


stock = get_stock_from_symbol("TSLA", "Tesla", ["car"])
get_score(stock)
