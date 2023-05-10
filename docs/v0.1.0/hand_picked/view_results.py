import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

res = pd.read_csv("performance_results.csv")

fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
fig.suptitle(f"Efficiency Across I/O Map")

ax.plot_trisurf(res["VIN"], res["VOUT"], res["EFF"], alpha=0.7)
ax.scatter(res["VIN"], res["VOUT"], res["EFF"], c=res["EFF"])
ax.set_xlabel("$V_{IN}$ (V)")
ax.set_ylabel("$V_{OUT}$ (V)")
ax.set_zlabel("Efficiency (%)")
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
fig.suptitle(f"Power Loss Across I/O Map")
p_loss = res["PIN"] - res["POUT"]
ax.plot_trisurf(res["VIN"], res["VOUT"], p_loss, alpha=0.7)
ax.scatter(res["VIN"], res["VOUT"], p_loss, c=p_loss)
ax.set_xlabel("$V_{IN}$ (V)")
ax.set_ylabel("$V_{OUT}$ (V)")
ax.set_zlabel("Power Loss (W)")
plt.tight_layout()
plt.show()
