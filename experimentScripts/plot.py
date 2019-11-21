# %%
from matplotlib import pyplot as plt
end_to_end_delays = [
    (0.05028352316353978, 0.05091768685843288),  # experiment 1
    (0.0894014673505196, 0.0900367994036308),  # experiment 2
    (0.10753256633108318, 0.1081764237659627)  # experiment 3
]
emulated_delays = [
    20,
    40,
    50
]

# %%
e2edelays = [
    1000 * (x1 + x2) / 2 for x1, x2 in end_to_end_delays
]
errors = [
    1000 * abs(x1 - x2) / 2 for x1, x2 in end_to_end_delays
]
print(errors)
yerr = [[], []]
for x1, x2 in end_to_end_delays:
    yerr[0].append(x1)
    yerr[1].append(x2)

# %%
plt.errorbar(x=emulated_delays, y=e2edelays, yerr=errors)
plt.show()

# %%


# %%


# %%
