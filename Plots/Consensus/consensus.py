import matplotlib.pyplot as plt
import os
import glob


csv_files = glob.glob(os.path.join('../data/', "*.csv"))
# Check
if not csv_files:
    print("Aucun fichier CSV trouvé dans le dossier.")
    exit()

plt.figure(figsize=(10, 6))

for file_path in csv_files:
    file_name = "RPi " + os.path.basename(file_path).split(".")[0]

    time = []
    values = []

    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                elem = line.split(",")
                time.append(float(elem[0]))
                values.append(float(elem[1]))


    plt.plot(time[:30], values[:30], label=file_name)
    #plt.plot(values[:30], label=file_name)

plt.xlabel("Time [s]")
plt.ylabel("Value")
plt.title("Consensus state (30 iterations)")
#plt.ylim(min(values)-1, max(values)+1)
plt.legend()
plt.grid(True)
plt.savefig("linear/linear_time.png")
plt.show()
"""
plt.xlabel("Iteration")
plt.ylabel("Value")
plt.title("Consensus state (30 iterations)")
#plt.ylim(min(values)-1, max(values)+1)
plt.legend()
plt.grid(True)
plt.savefig("linear/linear_it.png")
plt.show()"""
