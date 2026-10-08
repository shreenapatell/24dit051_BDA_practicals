import csv
import random
from datetime import datetime, timedelta

random.seed(42)

customers = range(1, 101)

with open("customer_transactions.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["CustomerID", "Date", "Amount"])

    start_date = datetime(2026, 1, 1)

    for customer in customers:
        purchases = random.randint(5, 30)

        for _ in range(purchases):
            date = start_date + timedelta(days=random.randint(0, 179))
            amount = round(random.uniform(200, 5000), 2)

            writer.writerow([
                customer,
                date.strftime("%Y-%m-%d"),
                amount
            ])

print("Customer transaction dataset generated successfully.")
