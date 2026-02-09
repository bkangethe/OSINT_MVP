import networkx as nx
from datetime import datetime
import numpy as np  
import pandas as pd
import matplotlib.pyplot as plt


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

# iterate tweets
# for tweet in tweets:
#     add_tweet_to_graph(tweet)

def get_rumour_cascade(root_id):
    cascade_nodes = nx.descendants(G.reverse(copy=False), root_id)
    cascade_nodes.add(root_id)
    return G.subgraph(cascade_nodes)

def growth_rate(cascade_subgraph):
    times = sorted([datetime.fromisoformat(G.nodes[n]["date"].replace("Z",""))
                    for n in cascade_subgraph.nodes()
                    if G.nodes[n]["node_type"] == "tweet" and "date" in G.nodes[n]])
    if len(times) < 2:
        return 0
    hours = (times[-1] - times[0]).total_seconds() / 3600
    return len(times) / max(hours, 0.01)


def early_reach(cascade_subgraph, k=10):
    tweets = [n for n in cascade_subgraph.nodes() if G.nodes[n]["node_type"] == "tweet"]
    tweets_sorted = sorted(tweets, key=lambda n: G.nodes[n]["date"])
    early = tweets_sorted[:k]
    return sum(G.nodes[n].get("impressions",0) for n in early)

def structural_virality(cascade_subgraph):
    tweets = [n for n in cascade_subgraph.nodes() if G.nodes[n]["node_type"] == "tweet"]
    if len(tweets) < 2:
        return 0
    lengths = []
    for i in range(len(tweets)):
        for j in range(i+1, len(tweets)):
            try:
                lengths.append(nx.shortest_path_length(cascade_subgraph, tweets[i], tweets[j]))
            except nx.NetworkXNoPath:
                pass
    return np.mean(lengths) if lengths else 0


def sentiment_volatility(cascade_subgraph):
    polarities = [G.nodes[n]["polarity"] for n in cascade_subgraph.nodes()
                  if G.nodes[n]["node_type"] == "tweet" and "polarity" in G.nodes[n]]
    return np.std(polarities) if polarities else 0

def rumour_score(cascade_subgraph):
    return (0.4*growth_rate(cascade_subgraph) +
            0.3*early_reach(cascade_subgraph) +
            0.2*structural_virality(cascade_subgraph) +
            0.1*sentiment_volatility(cascade_subgraph))
def draw_cascade(cascade_subgraph):
    pos = nx.spring_layout(cascade_subgraph, seed=42)
    node_colors = ["skyblue" if cascade_subgraph.nodes[n]["node_type"]=="tweet" else "lightgreen"
                   for n in cascade_subgraph.nodes()]
    nx.draw(cascade_subgraph, pos, node_size=50, node_color=node_colors, arrows=True)
    plt.show()

def plot_timeline(cascade_subgraph):
    times = [datetime.fromisoformat(G.nodes[n]["date"].replace("Z",""))
             for n in cascade_subgraph.nodes() if G.nodes[n]["node_type"]=="tweet"]
    if not times:
        return
    df = pd.DataFrame({"time": times})
    df.groupby(pd.Grouper(key="time", freq="10min")).size().plot(kind="bar")
    plt.ylabel("Number of tweets")
    plt.title("Cascade timeline (tweets per 10min)")
    plt.show()

root_tweet_id = 2014800579378246033
cascade_subgraph = get_rumour_cascade(root_tweet_id)

# Metrics
print("Growth rate (tweets/hour):", growth_rate(cascade_subgraph))
print("Early reach (first 10 tweets impressions):", early_reach(cascade_subgraph))
print("Structural virality:", structural_virality(cascade_subgraph))
print("Sentiment volatility:", sentiment_volatility(cascade_subgraph))
print("Rumour score:", rumour_score(cascade_subgraph))

# Visuals
draw_cascade(cascade_subgraph)
plot_timeline(cascade_subgraph)
