
import math as m

Rv = 160
f = 46000
C = 18E-6 * 0.8
DF = .12
vrms = Rv / (2 * m.sqrt(2))

z = (1 / (2 * m.pi * f * C) * m.sqrt(1 + DF ** 2))
irms_lf = vrms / z

p_max = 0.08
ESR = DF / (2 * m.pi * f * C)
irms_hf = m.sqrt(p_max / 100)

print(f"Rv: {Rv} V")
print(f"Vrms: {vrms} V")
print(f"Z imp: {z} Ohm")
print(f"Irms lf: {irms_lf} A")
print(f"ESR: {ESR} Ohm")
print(f"Irms hf: {irms_hf} A")

# Choose the switching frequency.
# f_s (kHz): 46
# Minimum C_IN: 4.131 uF
# Minimum C_OUT: 43.426 uF
# Minimum L: 601.292 uH
# Input capacitor should be rated for:
#     V_DC: 90.539 V.
#     I_RMS: 0.008 A.
# Output capacitor should be rated for:
#     V_DC: 164.062 V.
#     I_RMS: 0.013 A.
# Inductor should be rated for 8.838 A.
# Press any key to end.

D = 0.10367
# D = 0.86744
T = 1 / f
L = 601.292 * 10 ** -6
I_O = 400 / 80
# ii_rms = 6.15 / (1 - D) * m.sqrt(D * (1 - D))
# print(ii_rms)

io_rms = m.sqrt((D / (1 - D) * I_O ** 2) + (1 / 12 * D ** 2 * (1 - D) ** 3 * (80 * T / L) ** 2))
print(io_rms)

    vpkpk = r_ci_v
    ipkpk1 = ci_min * vpkpk * f_sw / min_duty
    ipkpk2 = ci_min * vpkpk * f_sw / (1 - min_duty)
    irms =  m.sqrt((ipkpk1 ** 2 * min_duty / f_sw) + (ipkpk1 ** 2 * (1 - min_duty) / f_sw))
    a = ci_min ** 2 * vpkpk ** 2 * f_sw / min_duty
    b = ci_min ** 2 * vpkpk ** 2 * f_sw / (1 - min_duty)
    irms = m.sqrt(a + b)
    ci_rms_min = irms * sf