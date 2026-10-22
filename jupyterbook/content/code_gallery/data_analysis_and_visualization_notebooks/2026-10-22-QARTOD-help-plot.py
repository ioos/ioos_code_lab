"""
Plotting helpers for the 2026-10-22-QARTOD-gliders notebook.
"""

from functools import cache

import cmocean
import gsw
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from ioos_qc.qartod import QartodFlags

#   Tying each flag to a label and a color
flag_style = {
    QartodFlags.GOOD:    ("GOOD", "#77AC30"),
    QartodFlags.UNKNOWN: ("UNKNOWN", "#4DBEEE"),
    QartodFlags.SUSPECT: ("SUSPECT", "#EDB120"),
    QartodFlags.FAIL:    ("FAIL", "#A2142F"),
    QartodFlags.MISSING: ("MISSING", "#7F7F7F"),
}

#   Drawing order, so the worst flags end up on top
order = [QartodFlags.UNKNOWN, QartodFlags.GOOD, QartodFlags.MISSING, QartodFlags.SUSPECT, QartodFlags.FAIL]


def plot_flags(ax, x, y, flags, s=4, thin=1, legend=True, **kwargs):
    x, y, flags = np.asarray(x), np.asarray(y), np.ma.getdata(flags)
    for zorder, f in enumerate(order):
        idx = np.flatnonzero(flags == f)
        if idx.size == 0:   #   No flags of this type, skip rather than break
            continue
        label, color = flag_style[f]
        size = s
        if f == QartodFlags.GOOD:
            idx = idx[::thin]
        else:
            size = 4 * s
        ax.scatter(
            x[idx],
            y[idx],
            s=size,
            color=color,
            linewidths=0,
            label=f"{label} ({np.count_nonzero(flags == f):,})",
            zorder=2 + zorder,
            rasterized=True,
            **kwargs,
        )
    if legend:
        ax.legend(loc="best", markerscale=2, fontsize=8)


#   A way to quickly format date axes
def date_axis(ax, fmt="%d %b"):
    ax.xaxis.set_major_formatter(mdates.DateFormatter(fmt))


@cache
def _landmask():
    #   Imported here so the module loads even without roaring_landmask, and built once
    from roaring_landmask import RoaringLandmask
    return RoaringLandmask.new()


def land_background(ax, extent, res=0.01):
    lon_g = np.arange(extent[0], extent[1] + res, res)
    lat_g = np.arange(extent[2], extent[3] + res, res)
    lon_m, lat_m = np.meshgrid(lon_g, lat_g)
    land = _landmask().contains_many(lon_m.ravel(), lat_m.ravel()).reshape(lon_m.shape)
    ax.contourf(lon_m, lat_m, land, levels=[0.5, 1.5], zorder=0)
    ax.contour(lon_m, lat_m, land, levels=[0.5], linewidths=0.5, zorder=1)
    ax.set_xlim(extent[:2])
    ax.set_ylim(extent[2:])
    #   Keep distances roughly true by correcting for the convergence of meridians
    ax.set_aspect(1 / np.cos(np.deg2rad(np.mean(extent[2:]))))
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")


def _range_spans(lo, hi, fail_span, suspect_span):
    #   (start, end, flag) for the fail and suspect bands outside the good range
    return [
        (lo, fail_span[0], QartodFlags.FAIL), (fail_span[1], hi, QartodFlags.FAIL),
        (fail_span[0], suspect_span[0], QartodFlags.SUSPECT), (suspect_span[1], fail_span[1], QartodFlags.SUSPECT),
    ]


#   Preliminary data check section
def overview_figure(lon, lat, time, pres, temp, psal, extent, map_step=50, section_step=10):
    fig = plt.figure(figsize=(12, 7.5), layout="constrained")
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.6])
    ax_map = fig.add_subplot(gs[:, 0])
    ax_t = fig.add_subplot(gs[0, 1])
    ax_s = fig.add_subplot(gs[1, 1], sharex=ax_t, sharey=ax_t)

    land_background(ax_map, extent=extent)
    sc = ax_map.scatter(
        np.asarray(lon)[::map_step], np.asarray(lat)[::map_step], c=mdates.date2num(time[::map_step]),
        s=2, cmap=cmocean.cm.tempo, rasterized=True,
    )
    cb = fig.colorbar(sc, ax=ax_map, orientation="horizontal", pad=0.02)
    cb.ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    cb.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax_map.text(9.95, 57.55, "DENMARK", ha="center", fontsize=8)
    ax_map.text(9.3, 59.05, "NORWAY", ha="center", fontsize=8)
    ax_map.text(11.4, 58.6, "SWEDEN", ha="center", fontsize=8, rotation=90)
    ax_map.set_title("SEA044 mission 109")

    for ax, var, cmap, label in [
        (ax_t, temp, cmocean.cm.thermal, "Temperature (°C)"),
        (ax_s, psal, cmocean.cm.haline, "Practical salinity"),
    ]:
        sc = ax.scatter(time[::section_step], pres[::section_step], c=var[::section_step], s=1, cmap=cmap,
                        rasterized=True)
        if var is psal:
            sc.set_clim(np.nanpercentile(psal, [1, 99.9]))
        fig.colorbar(sc, ax=ax, label=label)
        ax.set_ylabel("Pressure (dbar)")
    ax_t.invert_yaxis()
    ax_t.set_title("Temperature")
    ax_s.set_title("Salinity")
    date_axis(ax_s)
    plt.setp(ax_t.get_xticklabels(), visible=False)
    return fig, (ax_map, ax_t, ax_s)


#   Timing/gap tests
def impossible_date_figure(time_bad, flags_date, flags_date_window, window, injected, labels, step=500):
    """``injected`` are the indices of the altered timestamps, ``labels`` maps some of them to annotations."""
    idx = np.unique(np.r_[np.arange(0, time_bad.size, step), list(injected)])
    nat = np.isnat(time_bad[idx])
    ylims = [
        (np.datetime64("1965-01-01"), np.datetime64("2035-01-01")),
        (np.datetime64("2025-08-08"), np.datetime64("2025-10-10")),
    ]

    fig, axs = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True, layout="constrained")
    for col, (flags, title) in enumerate([
        (flags_date, "impossible_date_test(TIME)"),
        (flags_date_window, "impossible_date_test(TIME, fail_span=window)"),
    ]):
        for row, ylim in enumerate(ylims):
            ax = axs[row, col]
            plot_flags(ax, idx[~nat], time_bad[idx][~nat], np.ma.getdata(flags)[idx][~nat], s=6, legend=False)
            ax.scatter(idx[nat], np.full(nat.sum(), ylim[0]), marker="x", color=flag_style[QartodFlags.MISSING][1],
                       s=50, clip_on=False, zorder=10)
            ax.set_ylim(ylim)
            if col == 1:
                ax.axhspan(*window, color=flag_style[QartodFlags.GOOD][1], alpha=0.2, lw=0)
            for i, text in labels.items():
                #   Ring each injected timestamp, and label it where it stands apart from the mission
                off_mission = row == 1 or not (window[0] - np.timedelta64(60, "D") < time_bad[i] < window[1])
                if ylim[0] < time_bad[i] < ylim[1] and off_mission:
                    ax.scatter(i, time_bad[i], s=90, facecolors="none", edgecolors="k", linewidths=0.6, zorder=10)
                    ax.annotate(text, xy=(i, time_bad[i]), xytext=(9, 6), textcoords="offset points", fontsize=8)
        axs[0, col].set_title(title, fontfamily="monospace", fontsize=10)
        axs[0, col].axhline(np.datetime64("now"), color="k", ls="--", lw=0.8)
        axs[0, col].text(time_bad.size, np.datetime64("now"), "now ", ha="right", va="bottom", fontsize=8)
        axs[1, col].set_xlabel("Measurement index")
        axs[1, col].yaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        axs[1, col].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v / 1e6:.1f}M"))
    axs[0, 0].set_ylabel("TIME (full range)")
    axs[1, 0].set_ylabel("TIME (zoomed to the mission-ish)")
    axs[0, 0].legend(handles=[
        plt.Line2D([], [], marker="o", ls="", color=flag_style[f][1], label=flag_style[f][0])
        for f in (QartodFlags.GOOD, QartodFlags.FAIL)
    ] + [plt.Line2D([], [], marker="x", ls="", color=flag_style[QartodFlags.MISSING][1], label="MISSING (NaT)")],
        loc="lower right", fontsize=8)
    axs[1, 1].text(5e4, window[1], "deployment window", va="bottom", fontsize=8)
    return fig, axs


def data_reception_figure(time, pres, flags_rx, check_time, max_age_hours):
    fig, axs = plt.subplots(2, 1, figsize=(12, 6), sharex=True, layout="constrained")
    #   Data considered "stale"
    plot_flags(axs[0], time, pres, flags_rx, s=1, thin=10)
    axs[0].invert_yaxis()
    axs[0].set_ylabel("Pressure (dbar)")
    axs[0].set_title(f"data_reception_test(TIME, fail_span={max_age_hours}, from_time=check_time)",
                     fontfamily="monospace", fontsize=10)

    #   Age of the data in hours - relative to our check time
    age_hours = (check_time - time) / np.timedelta64(1, "h")
    plot_flags(axs[1], time, age_hours, flags_rx, s=1, thin=100, legend=False)
    axs[1].axhline(max_age_hours, color="k", ls="--", lw=0.8)
    axs[1].text(time[-1], max_age_hours, f"fail_span = {max_age_hours} h ", ha="right", va="bottom", fontsize=8)
    axs[1].axhline(0, color="k", lw=0.5)
    axs[1].set_ylabel("Age at check time (h)")
    for ax in axs:
        ax.axvline(check_time, lw=1.2)
    axs[1].text(check_time, axs[1].get_ylim()[1], " check time", va="top", fontsize=8)
    date_axis(axs[1])
    return fig, axs


def time_gap_figure(dt_seconds, time_gappy, pres_gappy, flags_gap, gap_start, gap_end):
    #   A binned hist, with a vis of the timeseries with a hole in it
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained", width_ratios=[1, 1.5])
    fail_color = flag_style[QartodFlags.FAIL][1]
    bins = np.logspace(0, 4, 41)
    axs[0].hist(np.clip(dt_seconds, 1, None), bins=bins, edgecolor="#262626", linewidth=0.4)
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    for span, label in [(60, "1 min"), (7200, "2 h")]:
        axs[0].axvline(span, color=fail_color, ls="--", lw=1)
        axs[0].text(span, axs[0].get_ylim()[1] * 0.3, f" {label}", color=fail_color, fontsize=8)
    axs[0].set_xlabel("Time between consecutive measurements (s)")
    axs[0].set_ylabel("Count")
    axs[0].set_title("Sampling interval, real data")

    flags_gap = np.ma.getdata(flags_gap)
    near = (time_gappy > gap_start - np.timedelta64(8, "h")) & (time_gappy < gap_end + np.timedelta64(8, "h"))
    axs[1].plot(time_gappy[near], pres_gappy[near], lw=0.6, zorder=1)
    plot_flags(axs[1], time_gappy[near], pres_gappy[near], flags_gap[near], s=2, thin=5, legend=False)
    axs[1].legend(loc="center", markerscale=2, fontsize=8)
    axs[1].axvspan(gap_start, gap_end, color=fail_color, alpha=0.1, lw=0)
    hours = (gap_end - gap_start) / np.timedelta64(1, "h")
    axs[1].text(gap_start + (gap_end - gap_start) / 2, 20, f"{hours:g} h of\ndeleted data", ha="center", va="top",
                fontsize=8)
    axs[1].annotate("first point after the gap", xy=(gap_end, pres_gappy[flags_gap == QartodFlags.FAIL][0]),
                    xytext=(30, 30), textcoords="offset points", fontsize=8, arrowprops={"arrowstyle": "->", "lw": 0.6})
    axs[1].invert_yaxis()
    axs[1].set_ylabel("Pressure (dbar)")
    axs[1].set_title("time_gap_test(TIME, fail_span=2), simulated dropout", fontfamily="monospace", fontsize=10)
    date_axis(axs[1], "%d %b\n%H:%M")
    return fig, axs


#   Syntax test
def syntax_figure(records, flags_char, flags_field, good_len, good_field, damage):
    """``damage`` maps record index to (description, ...), as built in the notebook."""
    n_chars = np.char.str_len(records)
    n_fields = np.array([len(r.split(";")) for r in records])
    rec = np.arange(records.size)

    fig, axs = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True, layout="constrained")
    for ax, values, expected, flags, title in [
        (axs[0], n_chars, good_len, flags_char, f'syntax_test(records, nchar={good_len}, lentype="char")'),
        (axs[1], n_fields, good_field, flags_field, f'syntax_test(records, nchar={good_field}, delimiter=";")'),
    ]:
        colors = [flag_style[f][1] for f in np.ma.getdata(flags)]
        ax.barh(rec, values, color=colors, edgecolor="#262626", linewidth=0.3, height=0.8)
        ax.axvline(expected, color="k", ls="--", lw=0.8)
        ax.set_title(title, fontfamily="monospace", fontsize=9)
        ax.set_xlim(0, values.max() * 1.25)
        for i, (what, _) in damage.items():
            ax.text(values[i] + values.max() * 0.02, i, what, va="center", fontsize=8)
    axs[0].set_xlabel("Characters per record")
    axs[1].set_xlabel("Fields per record")
    axs[0].set_ylabel("Record number")
    axs[0].invert_yaxis()
    axs[1].legend(handles=[
        plt.Rectangle((0, 0), 1, 1, color=flag_style[f][1], label=flag_style[f][0])
        for f in (QartodFlags.GOOD, QartodFlags.FAIL)
    ], loc="lower right")
    return fig, axs


#   Location tests
def location_distance_figure(time, lon_bad, lat_bad, flags_loc, range_max, i_swap, i_typo, i_half, i_none):
    time = np.asarray(time)
    d_bad = np.r_[0, gsw.distance(np.asarray(lon_bad), np.asarray(lat_bad))]

    fig, ax = plt.subplots(figsize=(12, 4), layout="constrained")
    plot_flags(ax, time, np.clip(d_bad, 0.01, None), flags_loc, s=3, thin=5)
    ax.set_yscale("log")
    ax.axhline(range_max, color="k", ls="--", lw=0.8)
    ax.text(time[-1], range_max, f"range_max = {range_max / 1000} km ", ha="right", va="bottom", fontsize=8)

    for i, what in [(i_swap, "lat/lon swapped"), (i_typo, "lat = lat+100 N")]:
        ax.annotate(what, xy=(time[i], d_bad[i]), xytext=(15, -5), textcoords="offset points", fontsize=8,
                    arrowprops={"arrowstyle": "->"})
    ax.annotate("jump back to track", xy=(time[i_swap + 1], d_bad[i_swap + 1]), xytext=(15, -20),
                textcoords="offset points", fontsize=8, arrowprops={"arrowstyle": "->"})

    ax.axvline(time[i_half], color=flag_style[QartodFlags.FAIL][1], lw=0.8, zorder=1, ls="--")
    ax.axvline(time[i_none], color=flag_style[QartodFlags.MISSING][1], lw=0.5, zorder=1, ls="--")

    ax.set_ylabel("Distance from previous fix (m)")
    ax.set_title(f'location_test(lon, lat, range_max={range_max}, range_method="wgs84")', fontfamily="monospace",
                 fontsize=10)
    date_axis(ax)
    return fig, ax


def land_zoom_figure(lon, lat, flags, extent, res=0.0005, title="location_on_land_test(lon, lat)"):
    fig, ax = plt.subplots(figsize=(8, 7), layout="constrained")
    land_background(ax, extent=extent, res=res)
    plot_flags(ax, lon, lat, flags, s=3)
    ax.set_title(title, fontfamily="monospace", fontsize=10)
    return fig, ax


def land_and_bounds_figure(lon, lat, flags_land, flags_bounds, extent, operating_area, exclusion_zone):
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.5), sharex=True, sharey=True, layout="constrained")
    for ax, flags, title in [
        (axs[0], flags_land, "location_on_land_test(lon, lat)"),
        (axs[1], flags_bounds, "location_bounds_test(...), outside + inside"),
    ]:
        land_background(ax, extent=extent)
        plot_flags(ax, lon, lat, flags, s=3, thin=10)
        ax.set_title(title, fontfamily="monospace", fontsize=10)

    axs[1].plot(*operating_area.exterior.xy, color="blue", lw=1.5, label="Operating area")
    axs[1].fill(*exclusion_zone.exterior.xy, facecolor="none", edgecolor="red", hatch="///", lw=1,
                label="Exclusion zone")
    axs[1].legend(loc="lower right", fontsize=8, markerscale=2)
    for ax in axs:
        ax.annotate("shifted 0.9° north", xy=(10.3, 59.0), xytext=(10.55, 58.7), fontsize=8,
                    arrowprops={"arrowstyle": "->", "lw": 0.6})
    return fig, axs


#   Gross range and percentile range tests
def gross_range_figure_pres(time, pres, values, flags, fail_span, suspect_span, label, title, bins):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5), width_ratios=[1, 1.6], layout="constrained")
    ax = axs[0]
    ax.hist(values[~np.isnan(values)], bins=bins, linewidth=0.3)
    ax.set_yscale("log")
    lo, hi = bins[0], bins[-1]
    for a, b, f in _range_spans(lo, hi, fail_span, suspect_span):
        if b > a:
            ax.axvspan(max(a, lo), min(b, hi), color=flag_style[f][1], alpha=0.25, lw=0)
    ax.set_xlim(lo, hi)
    ax.set_xlabel(label)
    ax.set_ylabel("Count")
    ax.set_title("Distribution with flag ranges")

    #   Really hard to see suspect on anything other than gray
    ax = axs[1]
    ax.scatter(time[::20], pres[::20], s=0.5, color="gray", rasterized=True, zorder=1)
    bad = np.ma.getdata(flags) != QartodFlags.GOOD
    plot_flags(ax, time[bad], pres[bad], np.ma.getdata(flags)[bad], s=2)
    ax.invert_yaxis()
    ax.set_ylabel("Pressure (dbar)")
    ax.set_title(title, fontfamily="monospace", fontsize=9)
    date_axis(ax)
    return fig, axs


def gross_range_figure_val(time, values, flags, fail_span, suspect_span, bins):
    """Improvement - stack hist sideways and keep the ranges on throughout"""
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5), width_ratios=[1, 3], sharey=True, layout="constrained")
    lo, hi = bins[0], bins[-1]
    for ax in axs:
        for a, b, f in _range_spans(lo, hi, fail_span, suspect_span):
            if b > a:
                ax.axhspan(max(a, lo), min(b, hi), color=flag_style[f][1], alpha=0.25, lw=0, zorder=0)

    ax = axs[0]
    ax.hist(values[~np.isnan(values)], bins=bins, orientation="horizontal", linewidth=0.3)
    ax.set_xscale("log")
    ax = axs[1]
    plot_flags(ax, time, values, flags, s=2, thin=20)
    return fig, axs


def percentile_range_figure(time, pres, temp, pct_runs, pct_flags, bins):
    """One row per run: histogram with bounds, flagged section, and the section colored to the bounds."""
    fig, axs = plt.subplots(len(pct_runs), 3, figsize=(17, 4 * len(pct_runs)), width_ratios=[1, 1.6, 1.6],
                            sharex="col", layout="constrained", squeeze=False)
    for row, (name, kw) in zip(axs, pct_runs.items(), strict=True):
        low, hi = np.nanpercentile(temp, [kw.get("low_percentile", 5), kw.get("hi_percentile", 95)])
        pad = kw.get("pad", 0)
        flags = pct_flags[name]

        ax = row[0] #   Histogram
        ax.hist(temp[~np.isnan(temp)], bins=bins, linewidth=0.3)
        ax.set_yscale("log")
        for a, b in [(bins[0], low - pad), (hi + pad, bins[-1])]:
            ax.axvspan(a, b, color=flag_style[QartodFlags.SUSPECT][1], alpha=0.25, lw=0)
        ax.axvline(low, color="k", ls="--", lw=0.8)
        ax.axvline(hi, color="k", ls="--", lw=0.8)
        ax.set_xlim(bins[0], bins[-1])
        ax.set_ylabel("Count")
        ax.set_title(name)

        ax = row[1]
        ax.scatter(time[::20], pres[::20], s=0.5, rasterized=True, zorder=1)
        bad = np.ma.getdata(flags) != QartodFlags.GOOD
        plot_flags(ax, time[bad], pres[bad], np.ma.getdata(flags)[bad], s=2, thin=5)
        ax.invert_yaxis()
        ax.set_ylabel("Pressure (dbar)")
        args = "".join(f", {k}={v}" for k, v in kw.items())
        ax.set_title(f"percentile_range_test(TEMP{args})", fontfamily="monospace", fontsize=9)
        date_axis(ax)

        ax = row[2]
        vmin = low - pad
        vmax = hi + pad
        sc = ax.scatter(time[::20], pres[::20], c=temp[::20], s=0.5, cmap=cmocean.cm.thermal,
                        vmin=vmin, vmax=vmax, rasterized=True)
        fig.colorbar(sc, ax=ax, label="Temperature (°C)")
        ax.sharey(row[1])
        ax.set_title(f"TEMP: {vmin:.2f} to {vmax:.2f}", fontfamily="monospace", fontsize=9)
        date_axis(ax)

    axs[-1, 0].set_xlabel("Temperature (°C)")
    return fig, axs


#   Climatology test
def _climatology_axes(temp, depth, flags, title):
    fig, ax = plt.subplots(figsize=(7, 6), layout="constrained")
    plot_flags(ax, temp, depth, flags, s=2, thin=20)
    ax.set_ylim(np.nanmax(depth) + 5, -2)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Depth (m)")
    ax.set_title(title, fontfamily="monospace", fontsize=9)
    return fig, ax


def climatology_figure(temp, depth, flags, boxes, title="climatology_test(config, TEMP, TIME, depth)"):
    """``boxes`` is a list of ((z0, z1), (v0, v1)) drawn as dashed rectangles."""
    fig, ax = _climatology_axes(temp, depth, flags, title)
    for (z0, z1), (v0, v1) in boxes:
        ax.add_patch(plt.Rectangle((v0, z0), v1 - v0, z1 - z0, fill=False, edgecolor="black", ls="--", lw=1))
    return fig, ax


def climatology_windows_figure(temp, depth, flags, clim_windows,
                               title="climatology_test(clim_windows, TEMP, TIME, depth)"):
    """Draws the vspan (suspect) and fspan (fail) boxes of each window in a ``ClimatologyConfig``."""
    fig, ax = _climatology_axes(temp, depth, flags, title)
    for w in clim_windows:
        z0, z1 = w["zspan"]
        for span, f, ls in [(w["vspan"], QartodFlags.SUSPECT, "--"), (w["fspan"], QartodFlags.FAIL, "-")]:
            if span is not None:
                ax.add_patch(plt.Rectangle((span.minv, z0), span.maxv - span.minv, z1 - z0, fill=False,
                                           edgecolor=flag_style[f][1], ls=ls, lw=1.2))

    handles, _ = ax.get_legend_handles_labels()
    handles += [
        plt.Line2D([], [], color=flag_style[QartodFlags.SUSPECT][1], ls="--", label="vspan"),
        plt.Line2D([], [], color=flag_style[QartodFlags.FAIL][1], label="fspan"),
    ]
    ax.legend(handles=handles, loc="lower right", markerscale=2, fontsize=8)
    return fig, ax


#   Pressure test
def pressure_cycle_figure(time, pres, profile, flags_pres, flags_pres_float, down):
    """A down/up pair of profiles, zoomed at the bottom turn and the surfacing. ``down`` should be odd."""
    up = down + 1
    cycle = (profile >= down) & (profile <= up)
    t_c, p_c = time[cycle], pres[cycle]
    fp, ff = np.ma.getdata(flags_pres)[cycle], np.ma.getdata(flags_pres_float)[cycle]

    #   Shading regions: the period at the bottom and the period back at the surface
    i_bottom = np.nanargmax(p_c)
    i_surface = np.flatnonzero(p_c < 2)[-1] #   TODO: Handle plotting blue/downcast transmission sections at the beginning.
    zooms = [
        (t_c[i_bottom] - np.timedelta64(2, "m"), t_c[i_bottom] + np.timedelta64(3, "m")),
        (t_c[np.flatnonzero(p_c[i_bottom:] < 4)[0] + i_bottom] - np.timedelta64(1, "m"),
         t_c[i_surface] + np.timedelta64(1, "m")),
    ]

    fig = plt.figure(figsize=(12, 9), layout="constrained")
    gs = fig.add_gridspec(3, 2, height_ratios=[1.3, 1, 1])
    ax_top = fig.add_subplot(gs[0, :])
    ax_top.plot(t_c, p_c, lw=0.6, zorder=1)
    plot_flags(ax_top, t_c, p_c, fp, s=2)
    ax_top.invert_yaxis()
    ax_top.set_ylabel("Pressure (dbar)")
    ax_top.set_title(
        f"pressure_test(PRES, direction, pad=0.01): profiles {down} (down) and {up} (up)",
        fontfamily="monospace", fontsize=10,
    )
    date_axis(ax_top, "%d %b %H:%M")

    zoom_axs = np.empty((2, 2), dtype=object)
    for col, (t0, t1) in enumerate(zooms):
        ax_top.axvspan(t0, t1, color="k", alpha=0.08, lw=0)
        m = (t_c >= t0) & (t_c <= t1)
        for row, flags, label in [(1, fp, "pad=0.01"), (2, ff, "pad=0.01, assess_floating=True")]:
            ax = zoom_axs[row - 1, col] = fig.add_subplot(gs[row, col])
            ax.plot(t_c[m], p_c[m], lw=0.6, zorder=1)
            plot_flags(ax, t_c[m], p_c[m], flags[m], s=3, legend=False)
            if row == 2:
                added = m & (ff != fp)
                ax.scatter(t_c[added], p_c[added], s=40, facecolors="none", edgecolors="k", linewidths=0.6,
                           zorder=10, label=f"added by assess_floating ({added.sum()})")
            if col == 1:
                ax.legend(loc="lower right", markerscale=2, fontsize=8)
            ax.invert_yaxis()
            ax.set_title(label, fontfamily="monospace", fontsize=9)
            date_axis(ax, "%H:%M:%S")
            if col == 0:
                ax.set_ylabel("Pressure (dbar)")
    return fig, (ax_top, zoom_axs)


def suspect_share_figure(flags, profile_slices, profile, direction,
                         title="Share of each profile flagged by pressure_test (assess_floating=True)"):
    starts = np.array([s.start for s in profile_slices])
    frac_suspect = np.array([np.mean(np.ma.getdata(flags)[s] == QartodFlags.SUSPECT) for s in profile_slices]) * 100
    prof_num = profile[starts]
    is_down = direction[starts] == 1

    fig, ax = plt.subplots(figsize=(12, 3.8), layout="constrained")
    ax.bar(prof_num[is_down], frac_suspect[is_down], width=1, label="Downcast")
    ax.bar(prof_num[~is_down], frac_suspect[~is_down], width=1, label="Upcast")
    ax.set_xlim(prof_num[0] - 1, prof_num[-1] + 1)
    ax.set_xlabel("Profile number")
    ax.set_ylabel("SUSPECT points (%)")
    ax.set_title(title)
    ax.legend()
    return fig, ax


#   Density inversion test
def profile_panels_figure(pres, profile, pnum, panels, flags=None, title=None):
    """Side-by-side profiles sharing the pressure axis.

    ``panels`` is a list of (values, xlabel), e.g. [(sigma0, r"$\\sigma_0$ (kg m$^{-3}$)"), (ds["SA"].values, ...)].
    If ``flags`` is given, SUSPECT and FAIL points are marked on every panel.
    """
    s = profile == pnum
    fig, axs = plt.subplots(1, len(panels), figsize=(4 * len(panels), 6), sharey=True, layout="constrained",
                            squeeze=False)
    axs = axs[0]
    for ax, (values, label) in zip(axs, panels, strict=True):
        ax.plot(values[s], pres[s], lw=0.8)
        if flags is not None:
            for f in (QartodFlags.SUSPECT, QartodFlags.FAIL):
                m = np.ma.getdata(flags)[s] == f
                ax.scatter(values[s][m], pres[s][m], s=25, color=flag_style[f][1], zorder=3,
                           label=f"{flag_style[f][0]} ({m.sum()})")
        ax.set_xlabel(label)
    axs[0].invert_yaxis()
    axs[0].set_ylabel("Pressure (dbar)")
    if flags is not None:
        axs[0].legend()
    fig.suptitle(title or f"Profile {pnum}")
    return fig, axs


def density_inversion_figure(time, pres, sigma0, profile, direction, profile_slices, flags_dens, pnum,
                             di_suspect, di_fail, step=25):
    """One profile's sigma0 and signed density change, next to the flagged section for the whole mission."""
    prof_num = profile[[s.start for s in profile_slices]]
    s = profile_slices[int(np.flatnonzero(prof_num == pnum)[0])]
    flags_dens = np.ma.getdata(flags_dens)
    p_prof, s_prof, f_prof = pres[s], sigma0[s], flags_dens[s]
    d_prof = np.r_[np.nan, np.sign(np.diff(p_prof)) * np.diff(s_prof)]

    fig, axs = plt.subplots(1, 3, figsize=(13, 6), width_ratios=[1, 1, 1.6], layout="constrained")
    ax = axs[0]
    ax.plot(s_prof, p_prof, lw=0.6, zorder=1)
    plot_flags(ax, s_prof, p_prof, f_prof, s=3)
    ax.set_xlim(np.nanpercentile(s_prof, [1, 100]) + [-0.3, 0.3])  # ignore the odd fresh surface sample
    ax.set_xlabel(r"$\sigma_0$ (kg m$^{-3}$)")
    ax.set_ylabel("Pressure (dbar)")
    ax.set_title(f"Profile {pnum} ({'down' if direction[s.start] == 1 else 'up'})")
    ax.invert_yaxis()

    ax = axs[1]
    plot_flags(ax, d_prof, p_prof, f_prof, s=3, legend=False)
    for th, f in [(di_suspect, QartodFlags.SUSPECT), (di_fail, QartodFlags.FAIL)]:
        ax.axvline(th, color=flag_style[f][1], ls="--", lw=1)
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlim(-0.3, 0.3)
    ax.set_xlabel(r"$\delta$ (kg m$^{-3}$ per sample)")
    ax.set_title("Signed density change")
    ax.sharey(axs[0])

    ax = axs[2]
    ax.scatter(time[::step], pres[::step], s=0.5, rasterized=True, zorder=1)
    bad = flags_dens >= QartodFlags.SUSPECT
    plot_flags(ax, time[bad], pres[bad], flags_dens[bad], s=1.5)
    ax.set_ylabel("Pressure (dbar)")
    ax.set_title(f"density_inversion_test(SIGMA0, PRES, {di_suspect}, {di_fail})", fontfamily="monospace",
                 fontsize=9)
    ax.invert_yaxis()
    date_axis(ax)
    return fig, axs
