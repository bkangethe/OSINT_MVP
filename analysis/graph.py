import networkx as nx

G = nx.Graph()

def add_tweet_to_graph(tweet):
    tweet_id = tweet["id"]
    user = tweet["username"]

    G.add_node(user, node_type="user")
    
    G.add_node(tweet_id,
               node_type="tweet",
               text=tweet["text"],
               sentiment=tweet["text_analysis"]["sentiment"],
               polarity=tweet["text_analysis"]["polarity"],
               risk=tweet["text_analysis"]["risk"],
               lang=tweet["lang"],
               likes=tweet["like_count"],
               replies=tweet["reply_count"],
               retweets=tweet["retweet_count"],
               impressions=tweet["impression_count"],
               date=tweet["date"]
               )

    G.add_edge(user, tweet_id, relation="POSTED")

    for ref in tweet.get("referenced_tweets", []):
        ref_id = ref["id"]
        G.add_node(ref_id, node_type="tweet")
        G.add_edge(tweet_id, ref_id, relation=ref["type"].upper())

    for url in tweet.get("entities", {}).get("urls", []):
        expanded = url["expanded_url"]
        G.add_node(expanded, node_type="url")
        G.add_edge(tweet_id, expanded, relation="LINKS_TO")
