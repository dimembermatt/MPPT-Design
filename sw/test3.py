
L = 527 * 10**-6 # H
I_max = 6.59 # A
rho = 1.77 * 10**-8 # ohm meters
B_max = 530 * 10**-3 # T
R_max = 70 * 10**-3 # ohm
k_u = 0.35

kg = ((L ** 2 )* (I_max ** 2) * rho) / ((B_max * 0.75) ** 2 * R_max * k_u)
print(kg)