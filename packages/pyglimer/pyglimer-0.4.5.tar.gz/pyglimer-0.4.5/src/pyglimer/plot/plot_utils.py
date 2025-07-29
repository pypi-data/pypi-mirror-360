'''
Plot utilities not to modify plots or base plots.

:copyright:
   The PyGLImER development team (makus@gfz-potsdam.de).
:license:
    EUROPEAN UNION PUBLIC LICENCE v. 1.2
   (https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
:author:
    Lucas Sawade (lsawade@princeton.edu)
    Peter Makus (makus@gfz-potsdam.de)

Created: Wednesday, 20th October 2021 05:05:08 pm
Last Modified: Tuesday, 8th August 2023 01:32:25 pm
'''

import os
from typing import Tuple
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import cartopy
from cartopy.crs import PlateCarree

from pyglimer.constants import maxz, res


def set_mpl_params(bold=False):
    params = {
        'font.family': "DejaVu Sans",
        'font.size': 14 if bold else 12,
        # 'pdf.fonttype': 3,
        'font.weight': 'bold' if bold else 'normal',
        # 'pdf.fonttype': 42,
        # 'ps.fonttype': 42,
        # 'ps.useafm': True,
        # 'pdf.use14corefonts': True,
        'axes.unicode_minus': False,
        'axes.labelweight': 'bold' if bold else 'normal',
        'axes.labelsize': 'medium' if bold else 'small',
        'axes.titlesize': 'large' if bold else 'medium',
        'axes.linewidth': 1,
        'axes.grid': False,
        'grid.color': "k",
        'grid.linestyle': ":",
        'grid.alpha': 0.7,
        'xtick.labelsize': 'medium' if bold else 'small',
        'xtick.direction': 'out',
        'xtick.top': True,  # draw label on the top
        'xtick.bottom': True,  # draw label on the bottom
        'xtick.minor.visible': True,
        'xtick.major.top': True,  # draw x axis top major ticks
        'xtick.major.bottom': True,  # draw x axis bottom major ticks
        'xtick.major.size': 4,  # draw x axis top major ticks
        'xtick.major.width': 1,  # draw x axis top major ticks
        'xtick.minor.top': True,  # draw x axis top minor ticks
        'xtick.minor.bottom': True,  # draw x axis bottom minor ticks
        'xtick.minor.width': 1,  # draw x axis top major ticks
        'xtick.minor.size': 2,  # draw x axis top major ticks
        'ytick.labelsize': 'medium' if bold else 'small',
        'ytick.direction': 'out',
        'ytick.left': True,  # draw label on the top
        'ytick.right': True,  # draw label on the bottom
        'ytick.minor.visible': True,
        'ytick.major.left': True,  # draw x axis top major ticks
        'ytick.major.right': True,  # draw x axis bottom major ticks
        'ytick.major.size': 4,  # draw x axis top major ticks
        'ytick.major.width': 1,  # draw x axis top major ticks
        'ytick.minor.left': True,  # draw x axis top minor ticks
        'ytick.minor.right': True,  # draw x axis bottom minor ticks
        'ytick.minor.size': 2,  # draw x axis top major ticks
        'ytick.minor.width': 1,  # draw x axis top major ticks
        'legend.fancybox': False,
        'legend.frameon': True,
        'legend.loc': 'best',
        'legend.numpoints': 1,
        'legend.fontsize': 'medium' if bold else 'small',
        'legend.framealpha': 1,
        'legend.scatterpoints': 3,
        'legend.edgecolor': 'inherit',
        'legend.facecolor': 'w',
        'mathtext.fontset': 'custom',
        'mathtext.rm': 'DejaVu Sans',
        'mathtext.it': 'DejaVu Sans:italic',
        'mathtext.bf': 'DejaVu Sans:bold'
    }
    matplotlib.rcParams.update(params)


def remove_all(ax=None, top=False, bottom=False, left=False, right=False,
               xticks='none', yticks='none'):
    """Removes all frames and ticks."""
    # Get current axis if none given.
    if ax is None:
        ax = plt.gca()

    # Hide the right and top spines
    ax.spines['bottom'].set_visible(bottom)
    ax.spines['left'].set_visible(left)
    ax.spines['right'].set_visible(right)
    ax.spines['top'].set_visible(top)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position(yticks)
    ax.xaxis.set_ticks_position(xticks)

    # Turn off tick labels
    ax.set_yticklabels([])
    ax.set_xticklabels([])


def remove_topright(ax=None):
    """Removes top and right border and ticks from input axes."""

    # Get current axis if none given.
    if ax is None:
        ax = plt.gca()

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')


def plot_catalog(catalog):
    """ Takes in event catalog and plots events as a function of location and
    moment magnitude."""

    plt.figure(figsize=(20, 7.5))
    ax = plt.subplot(111, projection=PlateCarree())

    size = 1
    mags = []
    lats = []
    lons = []

    for event in catalog:
        # Get mag
        mags.append(event.preferred_magnitude().mag)

        # Get location
        origin = event.preferred_origin()
        lats.append(origin.latitude)
        lons.append(origin.longitude)

    # Add coastline
    ax.add_feature(cartopy.feature.LAND, zorder=-2, edgecolor='black',
                   linewidth=0.5, facecolor=(0.9, 0.9, 0.9))

    # Plot events
    c = ax.scatter(
        np.array(lons), np.array(lats),  c=np.array(mags),
        s=size*np.array(mags)**3, marker="o", cmap="magma", vmin=3, vmax=7.5,
        edgecolor="k", linewidth=0.75, zorder=201)
    cbar = plt.colorbar(c, pad=0.005, shrink=1)
    cbar.ax.set_ylabel(r"       $M_w$", rotation=0)


def plot_single_rf(
    rf, tlim: list or tuple or None = None, ylim: list or tuple or None = None,
    depth: np.ndarray or None = None, ax: plt.Axes = None,
    outputdir: str = None, pre_fix: str = None,
    post_fix: str = None, format: str = 'pdf', clean: bool = False,
    std: np.ndarray = None, flipxy: bool = False, color: str = 'seismic',
        show: bool = True, bold: bool = False):
    """Creates plot of a single receiver function

    Parameters
    ----------
    rf : :class:`pyglimer.RFTrace`
        single receiver function trace
    tlim: list or tuple or None
        x axis time limits in seconds if type=='time' or depth in km if
        type==depth (len(list)==2).
        If `None` full trace is plotted.
        Default None.
    ylim: list or tuple or None
        y axis amplitude limits in. If `None` ± 1.05 absmax. Default None.
    depth: :class:`numpy.ndarray`
        1D array of depths
    ax : `matplotlib.pyplot.Axes`, optional
        Can define an axes to plot the RF into. Defaults to None.
        If None, new figure is created.
    outputdir : str, optional
        If set, saves a pdf of the plot to the directory.
        If None, plot will be shown instantly. Defaults to None.
    pre_fix : str, optional
        prepend filename
    post_fix : str, optional
        append to filename
    clean: bool, optional
        If True, clears out all axes and plots RF only.
        Defaults to False.
    std: np.ndarray, optional
        **Only if self.type == stastack**. Plots the upper and lower
        limit of the standard deviation in the plot. Provide the std
        as a numpy array (can be easily computed from the output of
        :meth:`~pyglimer.rf.create.RFStream.bootstrap`)
    flipxy: bool, optional
        Plot Depth/Time on the Y-Axis and amplitude on the x-axis. Defaults
        to False.
    color: str, optional
        Color-scale to use. Options are 'seismic', 'pyglimer', or 'mono'.
        Defaults to 'seismic'.
    show: bool, optional
        Execute plt.show()? Defaults to True

     Returns
    -------
    ax : `matplotlib.pyplot.Axes`
    """
    set_mpl_params(bold)

    if color == 'seismic':
        colorp = (0.9, 0.2, 0.2)
        colorn = (0.2, 0.2, 0.7)
    elif color == 'pyglimer':
        colorp = "#f7931e"
        colorn = "#008edd"
    elif color == 'mono':
        colorp = 'k'
        colorn = 'grey'
    else:
        raise ValueError(f'Unknown argument for color: {color}.')

    # Get figure/axes dimensions
    if ax is None:
        if flipxy:
            height, width = 8, 3
        else:
            width, height = 10, 2.5
        fig = plt.figure(figsize=(width, height))
        ax = plt.axes(zorder=9999999)
        axtmp = None
    else:
        fig = plt.gcf()
        bbox = ax.get_window_extent().transformed(
            fig.dpi_scale_trans.inverted())
        width, height = bbox.width, bbox.height
        axtmp = ax

    # The ratio ensures that the text
    # is perfectly distanced from top left/right corner
    ratio = width/height

    # Use times depending on phase and moveout correction
    ydata = rf.data
    if rf.stats.type == 'time':
        # Get times
        times = rf.times() - (rf.stats.onset - rf.stats.starttime)
        if rf.stats.phase[-1] == 'S':
            times = np.flip(times)
            ydata = np.flip(-rf.data)
    else:
        z = np.hstack(
            ((np.arange(-10, 0, .1)), np.arange(0, maxz+res, res)))
        times = z

    # Plot stuff into axes
    if flipxy:
        if std is not None:
            ax.plot(ydata-std, times, 'k--', lw=0.75)
            ax.plot(ydata+std, times, 'k--', lw=0.75)
            ax.fill_betweenx(
                times, 0, ydata, where=ydata > 0,
                interpolate=True, color=colorp, alpha=.8)
            ax.fill_betweenx(
                times, 0, ydata, where=ydata < 0,
                interpolate=True, color=colorn, alpha=.8)
        else:
            ax.fill_betweenx(
                times, 0, ydata, where=ydata > 0,
                interpolate=True, color=colorp, alpha=.8)
            ax.fill_betweenx(
                times, 0, ydata, where=ydata < 0,
                interpolate=True, color=colorn, alpha=.8)
        ax.plot(ydata, times, 'k', lw=0.75)

        # Set limits
        if tlim is None:
            # don't really wanna see the stuff before
            ax.set_ylim(0, times[-1])
        else:
            ax.set_ylim(tlim)

        if ylim is None:
            absmax = 1.1 * np.max(np.abs(ydata))
            ax.set_xlim([-absmax, absmax])
        else:
            ax.set_xlim(ylim)
        ax.invert_yaxis()
    else:
        if std is not None:
            ax.plot(times, ydata-std, 'k--', lw=0.75)
            ax.plot(times, ydata+std, 'k--', lw=0.75)
            ax.fill_between(times, 0, ydata, where=ydata > 0,
                            interpolate=True, color=colorp, alpha=.8)
            ax.fill_between(times, 0, ydata, where=ydata < 0,
                            interpolate=True, color=colorn, alpha=.8)
        else:
            ax.fill_between(times, 0, ydata, where=ydata > 0,
                            interpolate=True, color=colorp, alpha=.8)
            ax.fill_between(times, 0, ydata, where=ydata < 0,
                            interpolate=True, color=colorn, alpha=.8)
        ax.plot(times, ydata, 'k', lw=0.75)

        # Set limits
        if tlim is None:
            ax.set_xlim(0, times[-1])
            # don't really wanna see the stuff before
        else:
            ax.set_xlim(tlim)

        if ylim is None:
            absmax = 1.1 * np.max(np.abs(ydata))
            ax.set_ylim([-absmax, absmax])
        else:
            ax.set_ylim(ylim)

    # Removes top/right axes spines. If you want the whole thing, comment
    # or remove
    remove_topright()

    # Plot RF only
    if clean:
        remove_all()
    else:
        if rf.stats.type == 'time':
            if flipxy:
                ax.set_ylabel("Conversion Time [s]", rotation=90)
            else:
                ax.set_xlabel("Conversion Time [s]")
        else:
            if flipxy:
                ax.set_ylabel("Conversion Depth [km]", rotation=90)
            else:
                ax.set_xlabel("Conversion Depth [km]")
        if flipxy:
            ax.set_xlabel("A    ", rotation=0)
        else:
            ax.set_ylabel("A    ", rotation=0)

        # Start time in station stack does not make sense
        if rf.stats.type == 'stastack':
            text = rf.get_id()
        else:
            text = rf.stats.starttime.isoformat(sep=" ") + "\n" + rf.get_id()
        ax.text(0.995, 1.0-0.005*ratio, text, transform=ax.transAxes,
                horizontalalignment="right", verticalalignment="top")

    # Only use tight layout if not part of plot.
    if axtmp is None:
        plt.tight_layout()

    # Outout the receiver function as pdf using
    # its station name and starttime

    if outputdir is not None:
        # Set pre and post fix
        if pre_fix is not None:
            pre_fix = pre_fix + "_"
        else:
            pre_fix = ""
        if post_fix is not None:
            post_fix = "_" + post_fix
        else:
            post_fix = ""

        # Get filename
        filename = os.path.join(
            outputdir,
            pre_fix
            + rf.get_id() + "_"
            + rf.stats.starttime.strftime('%Y%m%dT%H%M%S')
            + post_fix
            + f".{format}")
        plt.savefig(filename, format=format, transparent=True)
    elif show:
        plt.show()
    return ax


def plot_section(
    rfst, channel="PRF",
    timelimits: list or tuple or None = None,
    epilimits: list or tuple or None = None,
    scalingfactor: float = 2.0, ax: plt.Axes = None,
    line: bool = True, linewidth: float = 0.25, outputfile: str or None = None,
    title: str or None = None, show: bool = True, format: str = None,
        color: str = 'seismic', bold: bool = False):
    """Creates plot of a receiver function section as a function
    of epicentral distance.

    Parameters
    ----------
    rfst : :class:`pyglimer.RFStream`
        Stream of receiver functions
    timelimits : list or tuple or None
        y axis time limits in seconds (len(list)==2).
        If `None` full traces is plotted.
        Default None.
    epilimits : list or tuple or None = None,
        y axis time limits in seconds (len(list)==2).
        If `None` from 30 to 90 degrees plotted.
        Default None.
    scalingfactor : float
        sets the scale for the traces. Could be automated in
        future functions(Something like mean distance between
        traces)
        Defaults to 2.0
    line : bool
        plots black line of the actual RF
        Defaults to True
    linewidth: float
        sets linewidth of individual traces
    ax : `matplotlib.pyplot.Axes`, optional
        Can define an axes to plot the RF into. Defaults to None.
        If None, new figure is created.
    outputdir : str, optional
        If set, saves a pdf of the plot to the directory.
        If None, plot will be shown instantly. Defaults to None.
    clean: bool
        If True, clears out all axes and plots RF only.
        Defaults to False.
    color: str, optional
        Color-scale to use. Options are 'seismic', 'pyglimer', or 'mono'.
        Defaults to 'seismic'.

     Returns
    -------
    ax : `matplotlib.pyplot.Axes`

    """
    set_mpl_params(bold)

    if color == 'seismic':
        colorp = (0.9, 0.2, 0.2)
        colorn = (0.2, 0.2, 0.7)
    elif color == 'pyglimer':
        colorp = "#f7931e"
        colorn = "#008edd"
    elif color == 'mono':
        colorp = 'k'
        colorn = 'grey'
    else:
        raise ValueError(f'Unknown argument for color: {color}.')

    # Create figure if no axes is specified
    if ax is None:
        plt.figure(figsize=(8, 6))
        ax = plt.axes(zorder=9999999)

    # Grab one component only
    # That doesn't work anymore. Was there an update in the obspy function?
    # rfst_chan = rfst.sort(channel=channel).sort(keys=['distance'])
    rfst_chan = rfst.sort(keys=['distance'])

    if not len(rfst_chan):
        raise ValueError(
            'There are no receiver functions of channel %s in the RFStream.' %
            channel)

    # Plot traces
    for _i, rf in enumerate(rfst_chan):
        if rf.stats.type == 'time':
            times = rf.times() - (rf.stats.onset - rf.stats.starttime)
            if rf.stats.phase[-1] == 'S':
                times = np.flip(times)
        else:
            z = rf.stats.pp_depth
            times = z

        rftmp = rf.data * scalingfactor \
            + rf.stats.distance
        ax.fill_betweenx(times, rf.stats.distance, rftmp,
                         where=rftmp < rf.stats.distance,
                         interpolate=True, color=colorn,
                         zorder=-_i, alpha=.8)
        ax.fill_betweenx(times, rf.stats.distance, rftmp,
                         where=rftmp > rf.stats.distance,
                         interpolate=True, color=colorp,
                         zorder=-_i - 0.1, alpha=.8)
        if line:
            ax.plot(rftmp, times, 'k', lw=linewidth, zorder=-_i + 0.1)

    # Set limits
    if epilimits is None:
        plt.xlim(epilimits)
    else:
        plt.xlim(epilimits)

    if timelimits is None:
        if rfst[0].stats.type == 'time':
            ylim0 = 0
        else:
            ylim0 = times[0]
        ylim1 = times[-1] + ylim0
        plt.ylim(ylim0, ylim1)
    else:
        plt.ylim(timelimits)
    ax.invert_yaxis()

    # Set labels
    plt.xlabel(r"$\Delta$ [$^{\circ}$]")
    if rfst[0].stats.type == 'time':
        plt.ylabel(r"Time [s]")
    else:
        plt.ylabel(r"Depth [km]")

    # Set title
    if title is not None:
        plt.title(title)
    else:
        plt.title("%s component" % channel)

    # Set output directory
    if outputfile:
        plt.savefig(outputfile, dpi=300, transparent=True, format=format)
    elif show:
        plt.show()
    return ax


def combined_single_station_plot(
    rfst, stack, ylim: Tuple[float, float] = None,
    epilimits: Tuple[float, float] = None, std: np.ndarray = None,
    scalingfactor: float = 6, outputfile: str = None, fmt: str = None, dpi=300,
    title: str = None, color: str = 'seismic', bold: bool = False,
    width_ratios: Tuple[float, float] = (1, 2),
    plot_lines: bool = False, linewidth: float = 0.25) -> Tuple[
        plt.Axes, plt.Axes]:
    """
    Creates a combined plot of the stack and the individual receiver functions
    (both depth-migrated).

    :param rfst: Stream of receiver functions in depth-domain
    :type rfst: RFStream
    :param stack: trace holding the stack
    :type stack: RFTrace
    :param ylim: ylim, defaults to None
    :type ylim: Tuple[float, float], optional
    :param epilimits: epicentral distance limits, defaults to None
    :type epilimits: Tuple[float, float], optional
    :param std: standard deviation computated via bootstrap
        in RFStream.bootstrap(), defaults to None
    :type std: np.ndarray, optional
    :param scalingfactor: Scalingfactor of the individual receiver functions,
        defaults to 6
    :type scalingfactor: float, optional
    :param outputfile: save figure file to, defaults to None
    :type outputfile: str, optional
    :param fmt: format to save in, defaults to None
    :type fmt: str, optional
    :param dpi: dpis, defaults to 300
    :type dpi: int, optional
    :param title: Title of the figure, defaults to None
    :type title: str, optional
    :param color: colour scaling to use, defaults to 'seismic'
    :type color: str, optional
    :param bold: Print labels bold, defaults to False
    :type bold: bool, optional
    :param width_ratios: Width ratio stack ad individual functions
        subplot, defaults to (1, 2)
    :type width_ratios: Tuple[float, float], optional
    :param plot_lines: Plot lines in the section plot, defaults to False
    :type plot_lines: bool, optional
    :param linewidth: Linewidth of the lines in the section plot,
        defaults to 0.25
    :type linewidth: float, optional
    """
    set_mpl_params(bold)

    fig, (ax0, ax1) = plt.subplots(
        1, 2, gridspec_kw={'width_ratios': width_ratios}, figsize=(10, 10),
        sharey=True)
    if title:
        fig.suptitle(title, fontsize=16, fontweight='bold')

    # no space between panels
    plt.subplots_adjust(wspace=0, hspace=0)

    plot_single_rf(
        stack, flipxy=True, std=std, ax=ax0, color=color, show=False,
        bold=bold, tlim=ylim)
    ax0.set_title('Stack')

    # Full Box
    ax0.spines['right'].set_visible(True)
    ax0.spines['top'].set_visible(True)

    # Only show ticks on the left ticks
    ax0.yaxis.set_ticks_position('left')
    ax0.set_xlabel(None)
    ax0.set_xticklabels([])
    ax0.set_xticks([])
    for txt in ax0.texts:
        txt.remove()

    # Section plot
    ax1 = plot_section(
        rfst, line=plot_lines, scalingfactor=scalingfactor, timelimits=ylim,
        ax=ax1, show=False, title='Individual Receiver Functions', color=color,
        bold=bold, epilimits=epilimits, linewidth=linewidth)
    ax1.spines['right'].set_visible(True)
    ax1.spines['top'].set_visible(True)
    ax1.set_xlabel(r'Epicentral Distance, $\Delta$ [$^{\circ}$]')
    ax1.tick_params(
        axis='both', which='both', right=False, top=False, labelleft=False,
        direction='inout')
    plt.ylabel(None)
    if outputfile is not None:
        plt.savefig(outputfile, transparent=True, format=fmt, dpi=dpi)
    return ax0, ax1


def baz_hist(az, nbins, bold=False):
    """
    Takes in backazimuth distribution and number of bins to compute
    the distribution of incoming angles.

    Parameters
    ----------
    az : numpy.ndarray
        azimuthal distribution in 1D array
    nbins : int
        Number of bins

    Returns
    -------å
    None

    """
    set_mpl_params(bold)

    # Get axes (or create one)
    ax = plt.gca()

    # Define bins
    bin_edges = np.linspace(0, 360, nbins+1)
    cts, edges = np.histogram(az, bins=bin_edges)

    # Define bars
    xbaz = edges[:-1] + 0.5 * np.diff(edges)
    wbaz = np.diff(edges)

    # Plot bars
    bars = plt.bar(xbaz/180*np.pi, cts, wbaz/180*np.pi, bottom=0.0)
    for r, bar in zip(cts, bars):
        bar.set_facecolor(plt.cm.magma_r(r / np.max(cts)))

    # Define limits and labels
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.invert_yaxis()
    ax.set_xticks(np.arange(0, 2*np.pi, 2*np.pi/8))
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
    labels = ax.get_xticklabels()
    plt.title('Backazimuth')
    for label in labels:
        pos = label.get_position()
        label.set_position([pos[0], pos[1]-0.02])


def rayp_hist(rayp, nbins, v=5.8, bold=False):
    """
    Takes in rayparameter distribution and number of bins to compute
    the distribution of incoming angles.

    Parameters
    ----------
    rayp: numpy.ndarray
        1D ndarray of rayparameters
    nbins: int
        Number of bins
    v: float
        assummed surface velocity for the computation of the
        incidence angle. Default 5.8 km/s.
    phase: string
        indicates which incidence wave is meant 'S' or 'P'. Default is 'P'
        simple defines boundaries of the plot nothing more nothing less.

    Returns
    -------
    None

    Notes
    -----
    Get Incidence angle p = sin i/v <--> v sin i / p <--> i = asin(vp)
    Default value 5.8 km/s taken from PREM.

    """
    set_mpl_params(bold)

    # Compute the angle
    angle = np.arcsin(rayp*v)

    # Use existing polar axis
    ax = plt.gca()

    # Define bins and bin angles
    bin_edges = np.linspace(0, np.pi/2, nbins+1)
    cts, edges = np.histogram(angle, bins=bin_edges)

    # Compute bars
    xbaz = edges[:-1] + 0.5 * np.diff(edges)
    wbaz = np.diff(edges)

    # Plot colored histogram
    bars = plt.bar(xbaz, cts, wbaz, bottom=0.0)
    bars = plt.bar(xbaz, cts, wbaz, bottom=0.0)
    for r, bar in zip(cts, bars):
        bar.set_facecolor(plt.cm.magma_r(r / np.max(cts)))

    # Change axis limits and labels
    ax.set_rorigin(2*np.max(cts))
    ax.set_rmin(1.05*np.max(cts))
    ax.set_rmax(0)
    ax.set_theta_zero_location('S')
    ax.set_theta_direction(1)
    ax.set_thetamin(7.5)
    ax.set_thetamax(35)
    labels = ax.get_xticklabels()
    plt.title('Incident Angle')
    for label in labels:
        pos = label.get_position()
        label.set_position([pos[0], pos[1]-0.02])
    ax.tick_params(labelleft=True, labelright=False,
                   labeltop=False, labelbottom=True)


def stream_dist(
    rayp: list or np.array, baz: list or np.array, nbins: float = 50,
    v: float = 5.8, phase: str = 'P', outputfile: None or str = None,
    format: str = "pdf", dpi: int = 300, title: str = None,
        bold: bool = False):
    """Uses backazimuth and rayparameter histogram plotting tools to create
    combined overview over the Distribution of incident waves.

    Parameters
    ----------
    rayp: numpy.ndarray
        1D ndarray of rayparameters
    az: numpy.ndarray
        azimuthal distribution in 1D array
    nbins: int
        Number of bins
    v: float
        assummed surface velocity for the computation of the
        incidence angle. Default 5.8 km/s.
    phase: string
        indicates which incidence wave is meant 'S' or 'P'. Default is 'P'
        simple defines boundaries of the rayparemeter plot nothing
        more nothing less.
    outputfile:  str or None
        Path to savefile. If None plot is not saved just shown.
        Defaults to None.
    format: str
        outputfile format
    dpi: int
        only used if file format is none vector.
    bold: bool, optional
        Print titles and labels larger

    """
    fig = plt.figure(figsize=(10, 4.5))
    if title:
        fig.suptitle(title, fontsize=19, fontweight='bold')
    plt.subplots_adjust(wspace=0.05)
    plt.subplot(121, projection="polar")
    baz_hist(baz, nbins, bold=bold)
    plt.subplot(122, projection="polar")
    rayp_hist(rayp, nbins, v=v, bold=bold)

    if outputfile:
        if format in ["pdf", "epsg", "svg", "ps"]:
            dpi = None
        plt.savefig(outputfile, format=format, dpi=dpi)
