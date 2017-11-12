import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

import squarify


parser = argparse.ArgumentParser(description='Creates tree map.')
parser.add_argument('filename', type=str,
                    help='filename desired to analyse')
arg = parser.parse_args()

# these values define the coordinate system for the returned rectangles
# the values will range from x to x + width and y to y + height
x = 0.
y = 0.
width = 2
height = 2

count_names = pd.read_csv(arg.filename)
values = count_names['total'].get_values()

# values must be sorted descending (and positive, obviously)
values[::-1].sort()

# the sum of the values must equal the total area to be laid out
# i.e., sum(values) == width * height
values = squarify.normalize_sizes(values, width, height)

# returns a list of rectangles
rects = squarify.squarify(values, x, y, width, height)

patches = [mpatches.Rectangle([sq['x'], sq['y']], sq['dx'], sq['dy']) for sq in rects]

fig, ax = plt.subplots()
colors = np.linspace(0, 1, len(patches))
np.random.shuffle(colors)
collection = PatchCollection(patches, cmap=plt.cm.hsv, alpha=0.3)
collection.set_array(np.array(colors))
ax.add_collection(collection)

plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.axis('equal')
plt.axis('off')
plt.savefig('{}.png'.format(arg.filename))
