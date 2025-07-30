#!/usr/bin/env python3
"""Analyze Mbias"""
import os
import pathlib
import sys
from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from vdaq_ana import ShowProgress

from vdaq_soap.data_utils import open_data_file


def read_mbias_scan(fname, mod_id, emin=-1, document=None):
    """Read the mbias scan data.

    Args:
    ----
        fname: The file name
        mod_id: The modile ID
        document (optional): The word document. Defaults to None.

    """
    print(":> Opening {} for mbias analysis".format(fname))
    vdaq = open_data_file(fname)
    if vdaq is None:
        return

    # get the iterator of the Scan data
    scan_iter = vdaq.scan_iter()
    scan_point = next(scan_iter)
    point_values = [scan_point.values[4]]
    point_mean = []
    point_rms = []
    point_data = []
    point_good = []
    good_chan = 0
    n_evts = 0

    try:
        the_chan = scan_point.values[0]
    except KeyError:
        the_chan = -1

    prg = ShowProgress(vdaq.nevts, width=24)
    prg.start()
    for evt in vdaq:
        # Get the module id
        mid = evt.mod_id

        if evt.evt_time > scan_point.end:
            # Next point
            try:
                scan_point = next(scan_iter)
                point_values.append(scan_point.values[4])
                if n_evts:
                    point_good.append(good_chan/n_evts)
                else:
                    point_good.append(0)

                if len(point_data) > 3:
                    point_mean.append(np.mean(point_data))
                    point_rms.append(np.std(point_data))
                else:
                    point_mean.append(0)
                    point_rms.append(0)

                try:
                    the_chan = scan_point.values[0]
                except KeyError:
                    the_chan = -1

                n_evts = 0
                good_chan = 0
                point_data = []

            except StopIteration:
                print("Stop iteration")
                print(evt.evt_time, scan_point.end)
                break

        if mid != mod_id:
            continue

        n_evts += 1
        md = vdaq.modules[mid]
        data = md.process_event(evt)
        if data is not None:
            ng = 0
            for C in data:
                if C.chan == the_chan:
                    ng += 1

                if C.E > emin:
                    point_data.append(C.E)

            if ng > 0:
                good_chan += 1

        prg.increase(show=True)

    print("")
    point_mean.append(np.mean(point_data))
    point_rms.append(np.std(point_data))
    if n_evts:
        point_good.append(good_chan/n_evts)
    else:
        point_good.append(0)

    imax = np.argmax(point_mean)
    imin = np.argmin(point_rms)
    print("\nMaximum amplitud is {:.1f} at Mbias={:.1f}".format(point_mean[imax], point_values[imax]))
    print("Minimum rms is {:.1f} at Mbias={:.1f}".format(point_rms[imin], point_rms[imin]))

    fig, ax = plt.subplots(3, 1, figsize=(6.4, 7.2), tight_layout=True)

    ax[0].plot(point_values, point_good, 'o-')
    ax[0].set_title("Mbias scan - good channel")
    ax[0].set_xlabel("mbias")

    ax[1].plot(point_values, point_mean, 'o-')
    ax[1].set_title("Mbias scan - Amplitude")
    ax[1].set_xlabel("mbias")
    ax[2].plot(point_values, point_rms, 'o-')
    ax[2].set_title("Mbias scan - noise")
    ax[2].set_xlabel("mbias")

    pdf_file = pathlib.Path.cwd().joinpath("mbias_{}.png".format(mod_id))
    fig.savefig(pdf_file, dpi=300)
    if document:
        document.add_heading('Mbias Scan', level=2)
        p = document.add_paragraph("Maximum amplitud is {:.1f} at Mbias={:.1f}".format(point_mean[imax],
                                                                                       point_values[imax]))
        p = document.add_paragraph("Minimum rms is {:.1f} at Mbias={:.1f}".format(point_rms[imin],
                                                                                  point_rms[imin]))
        document.add_picture(str(pdf_file))
        os.remove(pdf_file)

    plt.draw()
    plt.pause(0.001)


def analyzeMbias(files, options):
    """main entry."""
    ifile = Path(files[0]).expanduser().resolve()
    if not ifile.exists():
        return

    read_mbias_scan(ifile, options.mid, options.emin, None)
    plt.show()


def main():
    """Main entry."""
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--emin", default=0.0, type=float, help="Min E to show in histogram")

    parser.add_argument("--mid", dest="mid", default=11, type=int, help="The slot ID")

    options = parser.parse_args()

    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    analyzeMbias(options.files, options)


if __name__ == "__main__":
    main()