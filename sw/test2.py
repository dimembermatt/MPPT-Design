# test2.py
import matplotlib.pyplot as plt
import numpy as np

n = 100
lim = 22.2

fig = plt.figure()

def get_r_ja(a_fcu, a_bcu, N):
    a = 0.081 / a_fcu
    b = 0.081 / a_bcu
    c = 83.3 / N

    # print(a, b, c)

    num = a * b * c + 10 * a * b + 10 * a * c
    denom = 10 * a + 10 * b + 10 * c + a * c + b * c

    # print(num, denom)
    r_ja = 2.8 + num / denom
    return r_ja

x = []
y = []
z = []
for i in np.linspace(1E-5, 0.005, 100):
    for j in np.linspace(1E-5, 0.005, 100):
        r_ja = get_r_ja(i, j, n)

        if r_ja <= lim * 1.5:
            x.append(i)
            y.append(j)
            z.append(r_ja)

ax = fig.add_subplot(projection='3d')
ax.scatter(np.multiply(x, 1000000), np.multiply(y, 1000000), z, c=z)
ax.set_title("R_JA as a function of TCU area and BCU area")
ax.set_xlabel("FCU (mm^2)")
ax.set_ylabel("BCU (mm^2)")
ax.set_zlabel("R_JA (*C/W)")
ax.set_zlim(0, lim)

plt.show()


r_ja = get_r_ja(2000 * 1E-6, 2000 * 1E-6, 200)
print(r_ja)