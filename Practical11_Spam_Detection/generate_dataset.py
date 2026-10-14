import csv
import random

random.seed(42)

ham_messages = [
    "Hey are we meeting today",
    "Please call me when you are free",
    "Your assignment is due tomorrow",
    "I will reach home in ten minutes",
    "Can you send me the notes",
    "Thank you for your help",
    "Are you coming to college today",
    "Please bring the book with you",
    "Dinner is ready come home",
    "I will message you later",
    "The meeting starts at nine",
    "Let me know when you arrive",
    "Have a good day",
    "I am waiting near the station",
    "We will discuss this tomorrow"
]

spam_messages = [
    "Congratulations you won a free prize claim now",
    "Win cash now click this link",
    "Urgent claim your free reward today",
    "You have won a lottery prize call now",
    "Get a free phone by clicking this link",
    "Limited offer earn money quickly",
    "Claim your bonus now reply YES",
    "You are selected for a cash reward",
    "Free entry in a weekly prize draw",
    "Congratulations claim your gift now",
    "Earn extra cash from home today",
    "Exclusive offer click here to claim",
    "Your account won a reward verify now",
    "Get cheap loans apply immediately",
    "Winner claim your prize before expiry"
]

with open("sms_spam.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["label", "message_text"])

    # 1,000 original/generated sample records
    for i in range(1000):
        if i % 3 == 0:
            writer.writerow([
                "spam",
                random.choice(spam_messages)
            ])
        else:
            writer.writerow([
                "ham",
                random.choice(ham_messages)
            ])

print("SMS dataset generated successfully.")
print("Records: 1000")
	

