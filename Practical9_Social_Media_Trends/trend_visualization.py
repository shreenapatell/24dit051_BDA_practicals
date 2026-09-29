import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("social_media_data.csv")

hashtag_counts = df["Hashtag"].value_counts().head(10)
hashtag_counts = hashtag_counts.sort_values(ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(hashtag_counts.index, hashtag_counts.values)

plt.title("Top 10 Trending Hashtags")
plt.xlabel("Number of Occurrences")
plt.ylabel("Hashtag")

plt.tight_layout()
plt.savefig("top_10_hashtags.png", dpi=300)

print("Top 10 Trending Hashtags:")
print(hashtag_counts.sort_values(ascending=False))
print("\nVisualization saved as top_10_hashtags.png")
