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

reddit.verify_auth()

subreddit = 'wallstreetbets+IndianStockMarket'

words = 'Reliance'

print(reddit.get_text_posts(subreddit,words,limit=10))

