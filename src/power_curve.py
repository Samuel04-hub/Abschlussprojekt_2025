from load_data import load_data
from sort import bubble_sort
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Load the data from the CSV file
    data = load_data('data/activity.csv')
    power_W = data['PowerOriginal']
    print(power_W)
    sorted_power_W = bubble_sort(power_W)
    print(sorted_power_W[::-1])
    
    fig, ax = plt.subplots()
    a = np.arange(len(sorted_power_W))  
    x = a/60    # Assuming time is the index of the power data
    y = sorted_power_W[::-1] # Use the sorted power data for plotting

    ax.plot(x, y, color='blue')  # Add a line plot for better visualization
    ax.set(xlabel='Time (min)', ylabel='Power (W)',
           title='Power Curve')
    ax.grid()
    plt.show()
    # Save the plot as a PNG file
    fig.savefig("figures/power_curve.png")

