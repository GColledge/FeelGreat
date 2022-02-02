""" This file is designated as a place to keep functions that are for
 math calculations, data analysis, plot creation and streaming of the plot images"""
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def get_graph():
    """
    code here is taken almost directly from the following video
    https://www.youtube.com/watch?v=jrT6NiM46jk

    As is, this function will take the active figure and stuff it into a buffer for display.
    it is to be called after the figure is all set up. This will be called in a place
    similar to plt.show()"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, y, size=(6, 3), plot_title='Plot', x_label='Date', y_label='Value'):
    plt.switch_backend('AGG')
    plt.figure(figsize=size)
    plt.plot(x, y)
    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()
    graph = get_graph()
    return graph

def convert_to_percent(raw_values):
    """ this function takes a list of numbers and returns
    each value as a percent of the first value in the list."""
    first_value = raw_values[0]
    percentages = [(100 * v/first_value) for v in raw_values]
    return percentages

def get_differentials(raw_values):
    """This function takes a list of numbers and returns the
    difference of the numbers in order."""
    diffs = [0]
    for i in range(len(raw_values) - 1):
        dif = raw_values[i + 1] - raw_values[i]
        diffs.append(dif)
    return diffs