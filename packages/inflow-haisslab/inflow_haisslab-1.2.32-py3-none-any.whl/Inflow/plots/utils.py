# -*- coding: utf-8 -*-

from matplotlib import gridspec, pyplot as plt, rc_context
from matplotlib.ticker import MaxNLocator
from matplotlib.offsetbox import AnchoredOffsetbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
import numpy as np
import os


# Adapted from mpl_toolkits.axes_grid1
class AnchoredScaleBar(AnchoredOffsetbox):
    def __init__(
        self,
        transform,
        sizex=0,
        sizey=0,
        labelx=None,
        labely=None,
        loc=4,
        pad=0.1,
        borderpad=0.1,
        sep=2,
        prop=None,
        barcolor="black",
        barwidth=None,
        **kwargs,
    ):
        """
        Draw a horizontal and/or vertical  bar with the size in data coordinate
        of the give axes. A label will be drawn underneath (center-aligned).

        - transform : the coordinate frame (typically axes.transData)
        - sizex,sizey : width of x,y bar, in data units. 0 to omit
        - labelx,labely : labels for x,y bars; None to omit
        - loc : position in containing axes
        - pad, borderpad : padding, in fraction of the legend font size (or prop)
        - sep : separation between labels and bars in points.
        - **kwargs : additional arguments passed to base class constructor
        """
        from matplotlib.patches import Rectangle
        from matplotlib.offsetbox import (
            AuxTransformBox,
            VPacker,
            HPacker,
            TextArea,
            DrawingArea,
        )

        bars = AuxTransformBox(transform)
        if sizex:
            bars.add_artist(Rectangle((0, 0), sizex, 0, ec=barcolor, lw=barwidth, fc="none"))
        if sizey:
            bars.add_artist(Rectangle((0, 0), 0, sizey, ec=barcolor, lw=barwidth, fc="none"))

        if sizex and labelx:
            self.xlabel = TextArea(labelx, textprops={"color": barcolor})
            bars = VPacker(children=[bars, self.xlabel], align="center", pad=0, sep=sep)
        if sizey and labely:
            self.ylabel = TextArea(labely, textprops={"color": barcolor})
            bars = HPacker(children=[self.ylabel, bars], align="center", pad=0, sep=sep)

        AnchoredOffsetbox.__init__(
            self,
            loc,
            pad=pad,
            borderpad=borderpad,
            child=bars,
            prop=prop,
            frameon=False,
            **kwargs,
        )


def get_nice_number(value, allow_lower=True):
    if value == 0:
        return 0
    nice_numbers = np.array([1, 2, 5, 10])
    exponent_value = np.floor(np.log10(value))
    fraction_value = value / 10**exponent_value
    if allow_lower:
        idx = (np.abs(nice_numbers - fraction_value)).argmin()
    else:
        idx = np.searchsorted(nice_numbers, fraction_value)
    nice_fraction = nice_numbers[idx]
    nice_number = nice_fraction * 10**exponent_value
    return nice_number


def axis_to_data_unit(data_value, data_per_unit):
    unit_value = data_value / data_per_unit
    return unit_value


def data_to_axis_unit(unit_value, data_per_unit):
    data_value = unit_value * data_per_unit
    return data_value


def nice_scalebar_size(ax, data_per_unit, axis="x", bar_occupancy_ratio=0.2):
    if axis == "x":
        axis_size = np.diff(ax.get_xlim())[0]
    elif axis == "y":
        axis_size = np.diff(ax.get_ylim())[0]
    else:
        raise ValueError("axis must be 'x' or 'y'")
    bar_occupancy_ratio = 0.2
    scalebar_length_in_axis_units = axis_size * bar_occupancy_ratio
    scalebar_length_in_data_units = axis_to_data_unit(scalebar_length_in_axis_units, data_per_unit)
    scalebar_length_in_data_units = get_nice_number(scalebar_length_in_data_units)
    scalebar_length_in_axis_units = data_to_axis_unit(scalebar_length_in_data_units, data_per_unit)
    return scalebar_length_in_axis_units, scalebar_length_in_data_units


def add_scalebar(
    ax,
    sizex: str | int = "auto",
    sizey: str | int = "auto",
    hide_x_spine=True,
    hide_y_spine=True,
    labelx="",
    labely="",
    data_per_unitx=None,
    data_per_unity=None,
    bar_occupancy_ratio=0.2,
    **kwargs,
):
    """
    Adds a set of scale bars to the axes, matching the size to the ticks of the plot,
    and optionally hiding the x and y axes.

    Args:
        ax (matplotlib axis object): The axis to attach ticks to.
        sizex (str or int or None, optional): Size of the x-axis scale bar.
            If "auto", set size of scale bars to spacing between ticks.
            If None, do not show the scale bar for the x-axis.
            If a number, use this value for the x-axis scale bar. Defaults to "auto".
        sizey (str or int or None, optional): Size of the y-axis scale bar.
            Similar to sizex for y-axis. Defaults to "auto".
        hide_x_spine (bool, optional): If True, hides the x-axis of the parent plot. Defaults to True.
        hide_y_spine (bool, optional): If True, hides the y-axis of the parent plot. Defaults to True.
        labelx (str, optional): Label for the x-axis scale bar. Defaults to "".
        labely (str, optional): Label for the y-axis scale bar. Defaults to "".
        data_per_unitx (? , optional): The scale of how many data point per unit you have on the x axis.
            If used, sizex will not do anything. Defaults to None.
        data_per_unity (? , optional): The scale of how many data point per unit you have on the y axis.
            If used, sizey will not do anything. Defaults to None.
        bar_occupancy_ratio (float, optional): ?. Defaults to 0.2.
        **kwargs: additional arguments passed to AnchoredScaleBars

    Returns:
        AnchoredScaleBars object: the added scale bar.
    """

    def f(axis) -> int:
        locs = axis.get_majorticklocs()
        return len(locs) > 1 and (locs[1] - locs[0])

    sizes = {"x": sizex, "y": sizey}
    labels = {"x": labelx, "y": labely}
    data_per_units = {"x": data_per_unitx, "y": data_per_unity}
    for axis in ["x", "y"]:
        if data_per_units[axis] is not None:
            sizes[axis], label_value = nice_scalebar_size(
                ax, data_per_units[axis], axis=axis, bar_occupancy_ratio=bar_occupancy_ratio
            )
            labels[axis] = str(label_value) + "\n" + labels[axis]
        else:
            if sizes[axis] == "auto":
                sizes[axis] = f(ax.xaxis)

            if sizes[axis] is None:
                sizes[axis] = 0
            else:
                labels[axis] = str(sizes[axis]) + "\n" + labels[axis]

    sb = AnchoredScaleBar(
        ax.transData, sizex=int(sizes["x"]), sizey=int(sizes["y"]), labelx=labels["x"], labely=labels["y"], **kwargs
    )
    ax.add_artist(sb)

    if hide_x_spine:
        ax.xaxis.set_visible(False)
    if hide_y_spine:
        ax.yaxis.set_visible(False)
    if hide_x_spine and hide_y_spine:
        ax.set_frame_on(False)

    return sb


def add_ticklabel_to_axis(ax, tick, label, spine="x"):  # this is pure shit, delete asap

    ticks_getter = "get_xticks" if spine == "x" else "get_yticks"
    tickslabel_getter = "get_xticklabels" if spine == "x" else "get_yticklabels"
    ticks_setter = "set_xticks" if spine == "x" else "set_yticks"
    tickslabel_setter = "set_xticklabels" if spine == "x" else "set_yticklabels"

    original_ticks = eval(f"ax.{ticks_getter}")().copy()
    original_labels = eval(f"ax.{tickslabel_getter}")().copy()

    print("Original", label, original_ticks, original_labels)

    if tick in original_ticks:
        index = int(np.argwhere(original_ticks == tick)[0])
        original_ticks = np.delete(original_ticks, index)
        original_labels.pop(index)

    eval(f"ax.{ticks_setter}")((tick,))
    eval(f"ax.{tickslabel_setter}")((label,))

    new_ticks = np.append(original_ticks, eval(f"ax.{ticks_getter}")().copy())
    original_labels.extend(eval(f"ax.{tickslabel_getter}")().copy())
    new_labels = original_labels

    new_labels = [x for _, x in sorted(zip(new_ticks, new_labels), key=lambda pair: pair[0])]
    new_ticks = np.array(sorted(new_ticks))

    print("New", new_ticks, new_labels, "\n")

    eval(f"ax.{ticks_setter}")(new_ticks)
    eval(f"ax.{tickslabel_setter}")(new_labels)


def centered_ticks(image, tick_spacing=50):
    """Get locations and labels of ticks in relation to the center of an image, spaced by the value tick_spacing

    Args:
        image (_type_): _description_
        tick_spacing (int, optional): _description_. Defaults to 50.

    Returns:
        _type_: _description_
    """
    shape_y, shape_x = image.shape
    half_x = shape_x // 2
    half_y = shape_y // 2

    x_ticks_labels_right = np.arange(0, half_x, tick_spacing)
    x_ticks_labels_left = np.arange(-tick_spacing, -half_x, -tick_spacing)
    x_ticks_labels = np.concatenate([np.flip(x_ticks_labels_left), x_ticks_labels_right])

    x_ticks_right = np.arange(half_x, shape_x, tick_spacing)
    x_ticks_left = np.arange(half_x - tick_spacing, 0, -tick_spacing)
    x_ticks = np.concatenate([np.flip(x_ticks_left), x_ticks_right])

    y_ticks_labels_top = np.arange(0, half_y, tick_spacing)
    y_ticks_labels_bottom = np.arange(-tick_spacing, -half_y, -tick_spacing)
    y_ticks_labels = np.concatenate([np.flip(y_ticks_labels_bottom), y_ticks_labels_top])

    y_ticks_right = np.arange(half_y, shape_y, tick_spacing)
    y_ticks_left = np.arange(half_y - tick_spacing, 0, -tick_spacing)
    y_ticks = np.concatenate([np.flip(y_ticks_left), y_ticks_right])

    return half_x, x_ticks, x_ticks_labels, half_y, y_ticks, y_ticks_labels


def add_colorbar(im, ax, *, sci_notation=False, cbar_ticks_nb=2, visible_outline=False, **cbar_kwargs):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax, **cbar_kwargs)
    cbar.outline.set_visible(visible_outline)
    cbar.ax.yaxis.set_major_locator(MaxNLocator(nbins=cbar_ticks_nb, integer=True))
    if sci_notation:
        cbar.formatter.set_powerlimits((0, 0))
    return cbar


def legend_unique_items(axes):
    """
    Use like this :

    fig, axes = plt.subplots(2,2)
    fig.legend(*legend_unique_items(axes))

    OR

    axes[0,0].legend(*legend_unique_items(axes))

    OR

    fig.legend(*legend_unique_items(axes),title = "Legend")

    Parameters
    ----------
    axes : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.

    """
    import numpy as np
    from collections import OrderedDict

    def get_unique_handles():
        handles = []
        labels = []
        for ax in axes:
            leg_handles, leg_slabels = ax.get_legend_handles_labels()
            handles.extend(leg_handles)
            labels.extend(leg_slabels)
        legeng_dict = OrderedDict(zip(labels, handles))
        return legeng_dict.values(), legeng_dict.keys()

    if not isinstance(axes, (list, tuple, np.ndarray)):
        axes = [axes]
    if isinstance(axes, np.ndarray):
        axes = axes.flatten()

    handles, labels = get_unique_handles()
    return handles, labels  #


def clarify_plot_ax(
    ax,
    remove_spines=["top", "right"],
    tickfontsize=18,
    labelsfontsize=20,
    titlefontsize=20,
    xbins=2,
    ybins=2,
    integerticks=True,
):
    from matplotlib.ticker import MaxNLocator

    for spine in remove_spines:
        ax.spines[spine].set_visible(False)

    if tickfontsize is not None:
        for item in ax.get_xticklabels() + ax.get_yticklabels():
            item.set_fontsize(tickfontsize)

    if labelsfontsize is not None:
        for item in [ax.xaxis.label, ax.yaxis.label]:
            item.set_fontsize(labelsfontsize)

    if titlefontsize is not None:
        for item in [ax.title]:
            item.set_fontsize(titlefontsize)

    if xbins is not None:
        if xbins == 0:
            ax.set_xticks(())
            ax.xaxis.set_visible(False)
        else:
            ax.xaxis.set_major_locator(MaxNLocator(nbins=xbins + 1, integer=integerticks))

    if ybins is not None:
        if ybins == 0:
            ax.set_yticks(())
            ax.yaxis.set_visible(False)
        else:
            ax.yaxis.set_major_locator(MaxNLocator(nbins=ybins, integer=integerticks))


def clarify_image_ax(ax, nospine=True):
    minx, miny, maxx, maxy = 0, 0, 0, 0
    try:
        origin = ax.get_images()[0].origin
    except IndexError:
        return  # returning silently in case there is no image in axis. This is not a delayed drawer
    for img in ax.get_images():
        (
            _minx,
            _maxx,
            _miny,
            _maxy,
        ) = img.get_extent()  # in matplotlib, y axis is reversed by default when plotting images
        if _minx < minx:
            minx = _minx
        if _maxx > maxx:
            maxx = _maxx

        if origin == "upper":
            if _miny > miny:
                miny = _miny
            if _maxy < maxy:
                maxy = _maxy
        else:
            if _miny < miny:
                miny = _miny
            if _maxy > maxy:
                maxy = _maxy

    ax.set_xlim((minx, maxx))
    ax.set_ylim((miny, maxy))
    if nospine:
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)


def fig_pixel_sized(width, height, dpi=80):
    return plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)


def fig_as_array(fig):
    """
    Draw a figure in a numpy array to use it for video creation for example
    More info on : https://stackoverflow.com/questions/35355930/matplotlib-figure-to-image-as-a-numpy-array
    """
    import numpy as np

    fig.canvas.draw()
    image = np.frombuffer(fig.canvas.tostring_rgb(), dtype="uint8")
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)

    return image


def save_session_fig(
    fig,
    alf_identifier,
    extra=None,
    session_details=None,
    extensions=["svg", "png"],
    rcparams={
        "image.composite_image": False,  # https://github.com/matplotlib/matplotlib/issues/7151
        "font.family": ["sans-serif"],
        "font.sans-serif": ["Arial"],
        "text.usetex": False,
        "svg.fonttype": "none",
    },
    **savefig_kwargs,
):
    if extra is None:
        extra = ()
    if not isinstance(extra, (tuple, list)):
        extra = (extra,)
    extra = "." + "".join([f"{ext}." for ext in extra])

    if not isinstance(extensions, (list, tuple)):
        extensions = (extensions,)

    session_path = session_details.path if session_details is not None else ""
    root = os.path.abspath(os.path.join(session_path, "figures"))
    if not os.path.isdir(root):
        os.makedirs(root)
    fullpath = os.path.join(root, f"fig.{alf_identifier}{extra}")

    with rc_context(rcparams):
        for extension in extensions:
            fig.savefig(fullpath + extension, **savefig_kwargs)


def make_space_above(fig: plt.Figure, topmargin=1):
    """increase figure size to make topmargin (in inches) space for
    titles, without changing the axes sizes"""
    s = fig.subplotpars
    w, h = fig.get_size_inches()

    figh = h - (1 - s.top) * h + topmargin
    fig.subplots_adjust(bottom=s.bottom * h / figh, top=1 - topmargin / figh)
    fig.set_figheight(figh)


def get_centered_ticks(image, tick_spacing=50):
    shape_y, shape_x = image.shape
    half_x = shape_x // 2
    half_y = shape_y // 2

    x_ticks_labels_right = np.arange(0, half_x, tick_spacing)
    x_ticks_labels_left = np.arange(-tick_spacing, -half_x, -tick_spacing)
    x_ticks_labels = np.concatenate([np.flip(x_ticks_labels_left), x_ticks_labels_right])

    x_ticks_right = np.arange(half_x, shape_x, tick_spacing)
    x_ticks_left = np.arange(half_x - tick_spacing, 0, -tick_spacing)
    x_ticks = np.concatenate([np.flip(x_ticks_left), x_ticks_right])

    y_ticks_labels_top = np.arange(0, half_y, tick_spacing)
    y_ticks_labels_bottom = np.arange(-tick_spacing, -half_y, -tick_spacing)
    y_ticks_labels = np.concatenate([np.flip(y_ticks_labels_bottom), y_ticks_labels_top])

    y_ticks_right = np.arange(half_y, shape_y, tick_spacing)
    y_ticks_left = np.arange(half_y - tick_spacing, 0, -tick_spacing)
    y_ticks = np.concatenate([np.flip(y_ticks_left), y_ticks_right])

    return half_x, x_ticks, x_ticks_labels, half_y, y_ticks, y_ticks_labels


def imshow_centered_ticks(image, ax=None, tick_spacing=50):
    if ax is None:
        fig, ax = plt.subplots()

    im = ax.imshow(image, cmap="jet")

    ax.figure.colorbar(im, ax=ax, label="correlation (A.U.)")

    ax.grid(True, color="w", linestyle="-", linewidth=1, alpha=0.5)

    (
        half_x,
        x_ticks,
        x_ticks_labels,
        half_y,
        y_ticks,
        y_ticks_labels,
    ) = get_centered_ticks(image, tick_spacing)
    ax.axhline(half_y, color="w")
    ax.axvline(half_x, color="w")
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_ticks_labels, rotation=45)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks_labels)

    return ax


class SeabornFig2Grid:

    def __init__(self, seaborngrid, fig, subplot_spec):
        self.fig = fig
        self.sg = seaborngrid
        self.subplot = subplot_spec
        if isinstance(self.sg, sns.axisgrid.FacetGrid) or isinstance(self.sg, sns.axisgrid.PairGrid):
            self._movegrid()
        elif isinstance(self.sg, sns.axisgrid.JointGrid):
            self._movejointgrid()
        self._finalize()

    def _movegrid(self):
        """Move PairGrid or Facetgrid"""
        self._resize()
        n = self.sg.axes.shape[0]
        m = self.sg.axes.shape[1]
        self.subgrid = gridspec.GridSpecFromSubplotSpec(n, m, subplot_spec=self.subplot)
        for i in range(n):
            for j in range(m):
                self._moveaxes(self.sg.axes[i, j], self.subgrid[i, j])

    def _movejointgrid(self):
        """Move Jointgrid"""
        h = self.sg.ax_joint.get_position().height
        h2 = self.sg.ax_marg_x.get_position().height
        r = int(np.round(h / h2))
        self._resize()
        self.subgrid = gridspec.GridSpecFromSubplotSpec(r + 1, r + 1, subplot_spec=self.subplot)

        self._moveaxes(self.sg.ax_joint, self.subgrid[1:, :-1])
        self._moveaxes(self.sg.ax_marg_x, self.subgrid[0, :-1])
        self._moveaxes(self.sg.ax_marg_y, self.subgrid[1:, -1])

    def _moveaxes(self, ax, gs):
        # https://stackoverflow.com/a/46906599/4124317
        ax.remove()
        ax.figure = self.fig
        self.fig.axes.append(ax)
        self.fig.add_axes(ax)
        ax._subplotspec = gs
        ax.set_position(gs.get_position(self.fig))
        ax.set_subplotspec(gs)

    def _finalize(self):
        plt.close(self.sg.fig)
        self.fig.canvas.mpl_connect("resize_event", self._resize)
        self.fig.canvas.draw()

    def _resize(self, evt=None):
        self.sg.fig.set_size_inches(self.fig.get_size_inches())
