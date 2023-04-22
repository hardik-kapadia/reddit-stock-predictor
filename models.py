from datetime import datetime as dt

class Stock:
    def __init__(self, name, symbol, history, keywords=[]):
        self.name = name
        self.symbol = symbol
        self.history = history
        self.words = keywords
        self.words.append(symbol)
        self.words.extend(name.split(' ')[0])

    def __repr__(self) -> str:
        return str(
            {
                "name": self.name,
                "symbol": self.symbol,
                "history": self.history,
                "words": self.words,
            }
        )


class RedditTextPost:
    def __init__(self, title, text, upvotes, comment_count, upvote_ratio, created_at):
        self.title = title
        self.text = text
        self.upvotes = upvotes
        self.comment_count = comment_count
        self.upvote_to_comment_ratio = upvotes / comment_count
        self.upvote_ratio = upvote_ratio
        temp = str((dt.utcfromtimestamp(created_at)).date())
        self.created_at = temp

    def __str__(self):
        return str(self.get_data())

    def get_data(self):
        return {
            "title": self.title,
            "text": self.text,
            "upvotes": self.upvotes,
            "comment_count": self.comment_count,
            "upvote_to_comment_ratio": self.upvote_to_comment_ratio,
            "upvote_ratio": self.upvote_ratio,
            "created_at": self.created_at,
        }
