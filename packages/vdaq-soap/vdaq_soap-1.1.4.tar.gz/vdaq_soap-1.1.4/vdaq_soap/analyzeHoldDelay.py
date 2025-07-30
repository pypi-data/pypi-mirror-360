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


def read_hold_delay_data(fname, mod_id, emin=-1, document=None):
    """Read the scan data."""
    print(":> Opening {} for hold_delay analysis".format(fname))
    vdaq = open_data_file(fname)
    if vdaq is None:
        return

    # get the iterator of the Scan data
    scan_iter = vdaq.scan_iter()
    scan_point = next(scan_iter)
    point_values = [scan_point.values[11]]
    point_mean = []
    point_data = []

    prg = ShowProgress(vdaq.nevts, width=24)
    prg.start()
    for evt in vdaq:
        # Get the module id
        mid = evt.mod_id

        if evt.evt_time > scan_point.end:
            # Next point
            try:
                scan_point = next(scan_iter)
                point_values.append(scan_point.values[11])

                if len(point_data):
                    point_mean.append(np.mean(point_data))
                else:
                    point_mean.append(0.0)

                point_data = []

            except StopIteration:
                print("Stop iteration")
                print(evt.evt_time, scan_point.end)
                break

        if mid != mod_id:
            continue

        md = vdaq.modules[mid]
        data = md.process_event(evt)
        if data is not None:
            for C in data:
                if C.E > emin:
                    point_data.append(C.E)

        prg.increase(show=True)

    print("")
    point_mean.append(np.mean(point_data))

    imax = np.argmax(point_mean)
    vmax = point_mean[imax]
    hd_max = point_values[imax]
    print("\nMaximum is {:.1f} at HD={}".format(vmax, hd_max))

    fig, ax = plt.subplots(1, 1)
    ax.plot(point_values, point_mean, 'o-')
    ax.set_title("Hold delay scan")
    ax.set_xlabel("Hold Delay (dac)")
    pdf_file = pathlib.Path.cwd().joinpath("hold_delay_{}.png".format(mod_id))
    fig.savefig(pdf_file, dpi=300)
    if document:
        document.add_heading('Hold Delay Scan', level=2)
        p = document.add_paragraph("Maximum is {:.1f} at HD={}".format(point_mean[imax], point_values[imax]))
        document.add_picture(str(pdf_file))
        os.remove(pdf_file)

    plt.draw()
    plt.pause(0.001)
    return int(hd_max)


def analyzeHoldDelay(files, options):
    """main entry."""
    ifile = Path(files[0]).expanduser().resolve()
    if not ifile.exists():
        return

    read_hold_delay_data(ifile, options.mid, options.emin, None)
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

    analyzeHoldDelay(options.files, options)


if __name__ == "__main__":
    main()