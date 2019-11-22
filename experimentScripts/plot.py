from matplotlib import pyplot as plt

"""
    Experiment results
    These are 95% confidence intervals for each experiment
"""
end_to_end_delays = [
    (0.05028352316353978, 0.05091768685843288),  # experiment 1
    (0.0894014673505196, 0.0900367994036308),  # experiment 2
    (0.10753256633108318, 0.1081764237659627)  # experiment 3
]
"""
    Emulated delays
    We do not know exact delay. What we know what it may, possibly, close to.
    We will use those values to plot figure.
"""
emulated_delays = [
    20,
    40,
    50
]

"""
    Calculate means.
"""
e2edelays = [
    1000 * (x1 + x2) / 2 for x1, x2 in end_to_end_delays
]
"""
    Calculate error sizes.
"""
errors = [
    1000 * abs(x1 - x2) / 2 for x1, x2 in end_to_end_delays
]

"""
    Plot the figure and save it to 'figure.png'
"""
fig = plt.figure()
plt.errorbar(x=emulated_delays, y=e2edelays, yerr=errors)
plt.xlabel(xlabel='emulated delays')
plt.ylabel(ylabel='end to end delays')
plt.show()
fig.savefig('figure.png', dpi=fig.dpi * 4)
