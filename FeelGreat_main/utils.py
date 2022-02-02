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

def get_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(8, 6))
    plt.plot(x, y)
    plt.title('Generic Plot')
    plt.xticks(rotation=45)
    graph = get_graph()
    return graph