from re import S

import praw
from praw.reddit import Submission, Subreddit, Redditor

from pathvalidate import sanitize_filepath

import os

from models import RedditTextPost


class reddit_api:
    __reddit = None

    def __init__(self, reddit):
        self.__reddit = reddit

    @classmethod
    def get_instance(cls, client_id, client_secret, user_agent, username, password):
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password,
        )
        return cls(reddit)

    def get_text_posts(self, subreddit_name, query, limit):
        subreddit = self.__reddit.subreddit(subreddit_name)

        posts = subreddit.search(query)

        post_count = 0

        final_posts = []

        for post in posts:
            if post.is_self:
                title = post.title
                score = post.score
                comment_count = post.num_comments
                upvote_ratio = post.upvote_ratio
                text = post.selftext
                created_at = post.created_utc

                temp = RedditTextPost(title, text, score, comment_count, upvote_ratio,created_at)

                final_posts.append(temp)

                post_count += 1

                if post_count >= limit:
                    break
        return final_posts

    def get_posts(self, subreddit, words, limit):
        fsubr = self.__reddit.subreddit(subreddit)

        if not os.path.exists(subreddit):
            os.makedirs(subreddit)

        c_count = 0

        submissions = []
        try:
            for submission in fsubr.hot(limit=limit):
                title = submission.title
                print("Title:", title)

                if self.__contains_keys(words, title):
                    if submission.is_self:
                        reddit_api.createText(submission, subreddit)

                else:
                    submission.comments.replace_more(limit=5)
                    for comment in submission.comments:
                        if reddit_api.__contains_keys(words, comment.body):
                            c_count += 1

                            if submission.is_self:
                                reddit_api.createText(submission, subreddit)
                                submissions.append(submission)

                            break

            return submissions, c_count
        except:
            return submissions, 0, 0

    def verify_auth(self):
        print(self.__reddit.user.me())

    @staticmethod
    def __contains_keys(words, str):
        for word in words:
            word_c = len(word.split(" "))

            if len(str.split(" ")) <= word_c:
                if str.lower() == word.lower():
                    return True
                else:
                    continue
            split_ = str.split(" ")
            for i in range(len(split_) - word_c + 1):
                stemp = ""

                for j in range(word_c):
                    stemp += split_[i + j] + " "

                stemp = stemp[0:-1]

                if stemp.lower().strip() == word.lower().strip():
                    return True
        return False

    @staticmethod
    def createText(submission, subreddit):
        title = submission.title
        filename = subreddit + "/" + title + ".txt"
        filename = sanitize_filepath(filename)
        f = open(filename, "w")
        text = submission.selftext
        f.write(text)
        f.close()
