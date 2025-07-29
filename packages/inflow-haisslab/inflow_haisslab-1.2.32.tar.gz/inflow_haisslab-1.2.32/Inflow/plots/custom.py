# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 15:03:01 2023

@author: tjostmou
"""
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patheffects import withStroke
import numpy as np
import seaborn as sns
import pandas as pd

from .utils import add_scalebar, clarify_image_ax, clarify_plot_ax, add_colorbar, save_session_fig, centered_ticks
from timelined_array import TimelinedArray

from typing import Any, Optional


def sci_imshow(
    image,
    *,
    ax=None,
    vmin=None,
    vmax=None,
    cmap=None,
    cbar_label=None,
    cbar_visible_outline=False,
    cbar_sci_notation=True,
    show_scale=True,
    scale_unit="pixels",
    scale_color="black",
    pixels_per_unit=1,
    ticks_nb=2,
    title=None,
    **cbar_kwargs,
):
    """Displays an image in a scientific-paper-ready way.
    It will appear without x and y ticks, but rather use a scalebar
    and show a colorscale of the values. The behaviour can be tuned with some options below :

    Args:
        image (numpy.ndarray): The image to be displayed.

    Kwargs:
        ax (matplotlib.pyplot.Axes, optional): The matplotlib axes object to draw the image on. Defaults to None.
        vmin (float, optional): The lower saturation threshold for the image intensity. Defaults to None.
        vmax (float, optional): The upper saturation threshold for the image intensity. Defaults to None.
        cmap (str, optional): The colormap identifier. Defaults to None.
        cbar_label (str, optional): Label for the color bar. Defaults to None.
        sci_notation (bool, optional): Whether to show colorbar labels in scientific notation. Defaults to True.
        show_scale (bool, optional): Whether to display the image scale. Defaults to True.
        scale_unit (str, optional): The unit of measurement for the scale. Defaults to "pixels".
        pixels_per_unit (int, optional): The number of pixels equivalent to one unit of the scale. Defaults to 1.
        ticks_nb (int, optional): The number of ticks to display on the color bar. Defaults to 2.
        title (str, optional): The title of the image plot. Defaults to None.

        You can also include all arguments that would be available for the plt.colorbar function.

    Returns:
        matplotlib.pyplot.Axes: The Axes object with the image displayed.
    """
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    from matplotlib.ticker import MaxNLocator

    # left = 0
    # right = left + (image.shape[1] / pixels_per_unit)
    # bottom = (image.shape[0] / pixels_per_unit)
    # top = 0

    if ax is None:
        fig, ax = plt.subplots()
    im = ax.imshow(image, vmin=vmin, vmax=vmax, cmap=cmap)  # , extent = [left, right, bottom, top])
    add_colorbar(
        im,
        ax,
        label=cbar_label,
        sci_notation=cbar_sci_notation,
        cbar_ticks_nb=ticks_nb,
        visible_outline=cbar_visible_outline,
        **cbar_kwargs,
    )

    if show_scale:
        add_scalebar(
            ax,
            sizey=None,
            data_per_unitx=pixels_per_unit,
            labelx=scale_unit,
            borderpad=1,
            barcolor=scale_color,
        )
    else:
        clarify_image_ax(ax)
    ax.set_title(title)
    return ax


def scale_bar(
    ax,
    pixels,
    mm=5,
    pos=(20, 20),
    width=4,
    color="w",
    fontsize=14,
    vertical_offset=35,
    unit="mm",
):
    ax.plot([pos[0], pos[0] + pixels], [pos[1], pos[1]], linewidth=width, color=color)
    ax.text(
        pos[0] + (pixels / 2),
        pos[1] + vertical_offset,
        str(mm) + " " + unit,
        color=color,
        fontsize=fontsize,
        horizontalalignment="center",
    )


def colored_boxplot(
    ax,
    data,
    color="black",
    position=1,
    width=0.8,
    zorder=2,
    fill_alpha=1,
    label=None,
    show_median=False,
    showfliers=True,
    show_distribution=False,
    distribution_marker=".",
    distribution_markersize=8,
    distribution_alpha=0.5,
    distribution_zorder=None,
    **kwargs,
):
    import seaborn as sns
    from .artists import DottedYLine, DelayedYTickAdder
    import numpy as np
    import matplotlib
    from .colors import alter_color

    kwargs.pop("widths", False)
    kwargs.pop("positions", False)
    kwargs.pop("labels", False)

    bp = ax.boxplot(
        data,
        positions=(position,),
        widths=(width,),
        labels=(label,),
        patch_artist=True,
        showfliers=showfliers,
        **kwargs,
    )

    if show_distribution:
        distribution_zorder = zorder - 1 if distribution_zorder is None else distribution_zorder
        sns.swarmplot(
            ax=ax,
            data=data,
            color=color,
            size=distribution_markersize,
            alpha=distribution_alpha,
            marker=distribution_marker,
            zorder=distribution_zorder,
            linewidth=0,
        )

        collecs = ax.get_children()
        found = False
        collec = None
        for collec in collecs:
            if isinstance(collec, matplotlib.collections.PathCollection):
                try:
                    if collec.__COLORPLOT_OFFSETED__:
                        continue
                except Exception:
                    found = True
                    break
        if found:
            x, y = np.array(collec.get_offsets()).T
            offsets = x + float(position)
            offsets = list(zip(offsets, y))
            collec.set_offsets(offsets)
            collec.__COLORPLOT_OFFSETED__ = True

    for element in ["boxes", "whiskers", "fliers", "means", "medians", "caps"]:
        for lines in bp[element]:
            lines.set_color(color)
            lines.set_linewidth(2)

    zorder_fill = zorder - 2 if show_distribution else zorder - 1
    for patch in bp["boxes"]:
        patch.set(facecolor=alter_color(color, 0.5), zorder=zorder_fill, alpha=fill_alpha)

    if show_median:
        med = np.nanmedian(data)
        if show_median == 1 or show_median == 3:
            ax.add_artist(DottedYLine(position, med))
            ax.add_artist(DelayedYTickAdder(med))
        if show_median == 2 or show_median == 3:
            ax.text(
                position,
                med,
                f"{med:g}",
                color=color,
                ha="center",
                va="bottom",
                zorder=zorder + 1,
            )
    return bp


def heatmap_axis_setter(ticks, tick_labels, new_ticks):
    xs = [ticks[0], ticks[-1]]
    ys = [float(tick_labels[0].get_text()), float(tick_labels[-1].get_text())]

    coeffs = np.polyfit(ys, xs, 1)
    poly = np.poly1d(coeffs)
    values = poly(new_ticks)
    return values


def make_traces_heatmap(
    traces_series,
    conditions,
    neuron_values=None,
    values_label="accuracy",
    session_details=None,
    responsive_to="",
    vmin=0.42,
    vmax=0.7,
    chance=0.3,
    close_plot=True,
    acc_vmin=-1,
    acc_vmax=1,
):
    g = sns.JointGrid(height=8, ratio=10)

    left = 1.05  # the left side of the subplots of the figure
    bottom = 0.05  # the bottom of the subplots of the figure
    width = 0.5  # the width of the subplots of the figure
    height = 0.6
    extra_axis = g.fig.add_axes([left, bottom, width, height])

    roi_traces = TimelinedArray(traces_series)
    timeline = roi_traces.timeline
    rois_names = list(traces_series.index)
    heat_dataframe = pd.DataFrame(roi_traces, index=rois_names, columns=timeline)

    sns.heatmap(
        heat_dataframe,
        ax=g.ax_joint,
        cmap="magma",
        cbar_kws={
            "label": "DF/F0 (normalized)",
            "location": "left",
            "pad": 0.005,
            "shrink": 0.75,
            "extend": "both",
        },
        vmin=vmin,
        vmax=vmax,
    )

    coord0 = heatmap_axis_setter(g.ax_joint.get_xticks(), g.ax_joint.get_xticklabels(), 0)
    coord06 = heatmap_axis_setter(g.ax_joint.get_xticks(), g.ax_joint.get_xticklabels(), 0.6)
    coord1 = heatmap_axis_setter(g.ax_joint.get_xticks(), g.ax_joint.get_xticklabels(), 1)

    g.ax_joint.axvline(coord0, ls="-", lw=0.5, zorder=10, color="white")
    g.ax_joint.axvline(coord06, ls=(0, (5, 10)), lw=0.75, zorder=10, color="white")
    g.ax_joint.axvline(coord1, ls=(0, (1, 10)), lw=1, zorder=10, color="white")

    x_ticklabels = [-1, 0, 0.6, 1, 3]
    x_ticks = heatmap_axis_setter(g.ax_joint.get_xticks(), g.ax_joint.get_xticklabels(), x_ticklabels)

    g.ax_joint.set_xticklabels(g.ax_joint.get_xticklabels(), rotation=30)

    g.ax_joint.set_yticklabels(g.ax_joint.get_yticklabels(), rotation=30)

    g.ax_joint.set_xlabel("time (s)")
    g.ax_joint.set_ylabel("roi#")

    g.ax_joint.set_xticks(x_ticks)
    g.ax_joint.set_xticklabels(x_ticklabels)

    neuron_scores = pd.DataFrame(neuron_values.values, index=neuron_values.index, columns=[values_label])
    neuron_scores = neuron_scores.dropna()
    sns.heatmap(
        neuron_scores,
        ax=g.ax_marg_y,
        cmap="coolwarm",
        cbar_kws={
            "label": values_label,
            "shrink": 2,
            "extend": "min",
            "anchor": (0, 1),
        },
        vmin=acc_vmin,
        vmax=acc_vmax,
    )
    g.ax_marg_y.set_yticks([])

    sns.histplot(
        neuron_scores,
        x=values_label,
        ax=extra_axis,
        binwidth=0.05,
        linewidth=0,
        stat="percent",
    )
    extra_axis.set_ylabel("percent of neurons in category")
    extra_axis.set_xlim(acc_vmin, acc_vmax)
    extra_axis.axvline(chance, ls="--", color="k", label=f"chance\n({chance})")

    percent_above_chance = int(len(neuron_scores[neuron_scores["accuracy"] > chance]) / len(neuron_scores) * 100)
    extra_axis.text(
        chance + 0.1,
        extra_axis.get_yticks()[-2],
        f"{percent_above_chance}%\nneurons\nabove\nchance",
        ha="left",
        va="center",
    )

    extra_axis.legend()
    clarify_plot_ax(extra_axis, tickfontsize=None, labelsfontsize=None, titlefontsize=None)
    g.ax_marg_x.set_visible(False)

    cond_items = []
    for key in [
        "is_VGAT",
        "in_target_barrel",
        "frequency_change",
        "nontarget_amplitude",
    ]:
        if key not in conditions.keys():
            continue
        if key == "is_VGAT":
            cond_items.append("inhibitory" if conditions["is_VGAT"] else "excitatory")
        if key == "in_target_barrel":
            cond_items.append("primary" if conditions["in_target_barrel"] else "neigbouring")
        if key == "frequency_change":
            cond_items.append(str(int(conditions["frequency_change"])))
        if key == "nontarget_amplitude":
            cond_items.append("distract_on" if conditions["nontarget_amplitude"] == "10" else "distract_off")
    cond_items = [responsive_to] + cond_items
    condition_summary = ".".join(cond_items)

    g.fig.suptitle(condition_summary)

    if session_details is not None:
        save_session_fig(
            g.fig,
            "responsiveness_heatmap",
            extra=condition_summary,
            session_details=session_details,
            bbox_inches="tight",
        )

    if close_plot:
        plt.close()

    return g


def centered_ticks_imshow(image, ax=None, tick_spacing=50):

    if ax is None:
        fig, ax = plt.subplots()

    im = ax.imshow(image, cmap="jet")

    ax.figure.colorbar(im, ax=ax, label="correlation (A.U.)")

    ax.grid(True, color="w", linestyle="-", linewidth=1, alpha=0.5)

    half_x, x_ticks, x_ticks_labels, half_y, y_ticks, y_ticks_labels = centered_ticks(image, tick_spacing)
    ax.axhline(half_y, color="w")
    ax.axvline(half_x, color="w")
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_ticks_labels, rotation=45)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_ticks_labels)

    return ax


def correlation_center_image(
    *input_data: tuple[np.ndarray, np.ndarray] | tuple[dict[str, Any]],
    title="",
    ax: Optional[Axes] = None,
    tick_spacing=50,
    flat_field=None,
    flat_field_corrected=False,
    gaussian=None,
):
    if isinstance(input_data[0], dict):
        correlation_results: dict[str, Any] = input_data[0]
    else:
        # input_data must be a tuple of np arrays, where first is ref, second is tested image
        from pImage.measurements import correlation_2D

        ref, test = input_data[0], input_data[1]
        correlation_results = correlation_2D(
            ref,
            test,
            flat_field=flat_field,
            flat_field_corrected=flat_field_corrected,
            gaussian=gaussian,
        )

    ax = centered_ticks_imshow(correlation_results["correlation_image"], ax=ax, tick_spacing=tick_spacing)
    ax.plot(
        *correlation_results["maximum_correlation_point"],
        "o",
        color="black",
        markersize=5,
        markerfacecolor="black",
        markeredgewidth=2,
        markeredgecolor="white",
    )
    ax.text(
        *correlation_results["maximum_correlation_point"],
        s="  " + str(correlation_results["shifts"]),
        color="black",
        va="center",
        ha="left",
        path_effects=[withStroke(linewidth=3, foreground="white")],
    )
    ax.set_title(title)
    return correlation_results, ax


def image_histogram(image: np.ndarray, ax=None) -> Axes:
    if ax is None:
        _, ax = plt.subplots(1, figsize=(10, 10))

    try:
        iinfo = np.iinfo(image.dtype)
        xmin, xmax = iinfo.min, iinfo.max
        bins = xmax - xmin
    except ValueError:  # dtatype is not int based
        xmin, xmax = image.min(), image.max()
        bins = 100

    ax.hist(image.flatten(), bins)
    ax.set_xlim(xmin, xmax)
    return ax
