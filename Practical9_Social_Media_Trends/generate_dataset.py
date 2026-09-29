import csv
from datetime import date, timedelta

hashtags = [
    "#AI", "#Technology", "#MachineLearning", "#DataScience",
    "#CloudComputing", "#Cricket", "#Football", "#Olympics",
    "#Sports", "#Movies", "#Music", "#Bollywood",
    "#Gaming", "#Business", "#Startups", "#Marketing",
    "#Innovation", "#Entertainment"
]

regions = ["India", "USA", "UK", "Canada", "Australia"]

categories = {
    "#AI": "Technology",
    "#Technology": "Technology",
    "#MachineLearning": "Technology",
    "#DataScience": "Technology",
    "#CloudComputing": "Technology",
    "#Cricket": "Sports",
    "#Football": "Sports",
    "#Olympics": "Sports",
    "#Sports": "Sports",
    "#Movies": "Entertainment",
    "#Music": "Entertainment",
    "#Bollywood": "Entertainment",
    "#Gaming": "Entertainment",
    "#Business": "Business",
    "#Startups": "Business",
    "#Marketing": "Business",
    "#Innovation": "Technology",
    "#Entertainment": "Entertainment"
}

# 650 records with #AI as the most frequent hashtag
counts = {
    "#AI": 75,
    "#Technology": 55,
    "#MachineLearning": 45,
    "#DataScience": 40,
    "#CloudComputing": 35,
    "#Cricket": 50,
    "#Football": 40,
    "#Olympics": 25,
    "#Sports": 30,
    "#Movies": 35,
    "#Music": 30,
    "#Bollywood": 25,
    "#Gaming": 20,
    "#Business": 25,
    "#Startups": 20,
    "#Marketing": 62,
    "#Innovation": 23,
    "#Entertainment": 15
}

rows = []
start_date = date(2026, 1, 1)

for hashtag in hashtags:
    for i in range(counts[hashtag]):
        day = start_date + timedelta(days=i % 10)
        region = regions[i % len(regions)]

        rows.append([
            day.isoformat(),
            hashtag,
            region,
            categories[hashtag]
        ])

with open("social_media_data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Hashtag", "Region", "Category"])
    writer.writerows(rows)

print("Dataset generated successfully.")
print("Total records:", len(rows))
print("Distinct hashtags:", len(hashtags))
