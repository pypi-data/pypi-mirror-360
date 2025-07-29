# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap, to_rgb
import matplotlib as mpl
import numpy as np


def cbar(vmin, vmax, ax=None, **kwargs):
    """
    Used to generate a simple, one subplot figure that is a colorbar, with the specifiev vmin vmax and optional kwargs
    to tune the legends / look of it.

    List of kwargs :
        - figsize = (height,width)
        - cmap = str
        - lwratio = float
            the ratio between with and height for the colorbar
        - fontsize = float
        - title = str
            the label of the colorbar (the unit description etc)

    Parameters
    ----------
    vmin : TYPE
        DESCRIPTION.
    vmax : TYPE
        DESCRIPTION.
    ** kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.
    ax : TYPE
        DESCRIPTION.

    """
    if ax is not None:
        fig = ax.figure
    else:
        fig, ax = plt.subplots(1, figsize=kwargs.get("figsize", (10, 1)))
    cmap = mpl.cm.get_cmap(kwargs.get("cmap", "jet"))
    resolution = 100
    colorline = np.linspace(vmin, vmax, resolution)
    colorline = np.repeat(colorline[:, np.newaxis], resolution / kwargs.get("lwratio", 5), axis=1)
    # colorline = cmap(colorline)
    ax.imshow(colorline, cmap=cmap, vmin=vmin, vmax=vmax, origin="lower")
    ax.set_yticks((0, 100))
    ax.set_yticklabels((vmin, vmax), fontsize=kwargs.get("fontsize", None))
    ax.set_xticks(())
    ax.set_ylabel(
        kwargs.get("title", None),
        labelpad=-30,
        fontsize=kwargs.get("fontsize", None),
    )
    return fig, ax


def alter_color(color, amount=0.5):
    """
    Lightens or darkens the given color by multiplying (1-luminosity) by the given amount
    (negative to darken, positive to lighten). Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys

    try:
        c = mc.cnames[color]
    except Exception:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    lightness = 1 - (amount * (1 - c[1])) if amount >= 0 else abs(-amount - 1) * c[1]
    return colorsys.hls_to_rgb(c[0], lightness, c[2])


def norm_color(value, vmin, vmax, cmap="viridis"):
    color_map = plt.get_cmap("viridis")
    normalizer = colors.Normalize(vmin=vmin, vmax=vmax)
    return color_map(normalizer(value))


def linear_cmap(colors=["red", "green"], n_bins=100):

    if isinstance(colors, str):
        colors = colors.split("_")

    colors = [to_rgb(c) if isinstance(c, str) else c for c in colors]

    cmap_name = "_".join(colors)

    # Create the colormap
    cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)
    return cmap
