import matplotlib.pyplot as plt

k_values = [2, 3, 4, 5, 6, 7, 8]

wssse_values = [
    250.12345617359023,
    199.66137741099007,
    168.45899823135753,
    142.7695595405575,
    122.57605920061798,
    116.76489004259405,
    94.89414438111207
]

plt.figure(figsize=(8, 5))

plt.plot(
    k_values,
    wssse_values,
    marker="o"
)

plt.title("Elbow Method for Optimal K")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("WSSSE")

plt.xticks(k_values)
plt.grid(True)

plt.tight_layout()

plt.savefig("elbow_plot.png", dpi=300)

print("Elbow plot saved as elbow_plot.png")
