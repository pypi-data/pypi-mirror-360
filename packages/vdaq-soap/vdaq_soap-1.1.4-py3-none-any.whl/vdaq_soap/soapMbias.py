#!/usr/bin/env python3
"""Do a Hold delay scan."""
import sys
from argparse import ArgumentParser

import daqpp.soap
import matplotlib.pyplot as plt

from vdaq_soap.soapCheckAliVATA import restore_default_state
from vdaq_soap.soapCheckAliVATA import set_default_parameters
from vdaq_soap.soapCheckAliVATA import test_mbias_scan


def main():
    """Main entry."""
    parser = ArgumentParser()
    parser.add_argument("--host", dest="host", default="localhost",
                        type=str, help="The soap server")
    parser.add_argument("--port", dest="port", default=50000,
                        type=int, help="The soap port")
    parser.add_argument("--mid", dest="mid", default="11",
                        type=str, help="The slot ID")
    parser.add_argument("--channel", dest="channel", default=32,
                        type=int, help="The test channel")
    parser.add_argument("--hold_delay", dest="hold_delay", default=175,
                        type=int, help="Chip Hold Delay")
    parser.add_argument("--mbias", dest="mbias", default=600,
                        type=int, help="Chip Main bias")
    parser.add_argument("--polarity", dest="polarity", default=0,
                        type=int, help="Signal polarity")
    parser.add_argument("--nsec", dest="nsec", default=10,
                        type=int, help="Chip Main bias")
    parser.add_argument("--step", type=int, help="Scan step", default=64)
    parser.add_argument("--min_val", type=int, help="Minimum value of scan", default=64)
    parser.add_argument("--max_val", type=int, help="Minimum value of scan", default=4096)
    parser.add_argument("--emin", default=0.0, type=float,
                        help="Min E to show in histogram")
    parser.add_argument("--threshold", default=50, type=int, help="GPx threshold")

    parser.add_argument("--debug", dest="debug", action="store_true",
                        help="Debug server I/O",
                        default=False)
    options = parser.parse_args()

    # This is where we connect with the server
    try:
        server = daqpp.soap.DAQppClient(options.host, options.port, debug=options.debug)
    except Exception as E:
        print(("Could not connect to the server\n{}".format(E)))
        sys.exit()

    # Stop the run if running
    print("Check if the RUnManager is active and running")
    run_manager = daqpp.soap.RunManager("main", server)
    S = run_manager.getStatus()
    if S.status == "Running":
        print("Stopping run")
        run_manager.stopRun()

    # Get the module
    the_module = None
    modules = server.getAllModules()
    for md in modules:
        print("Module {}".format(md.name))
        if md.name == options.mid:
            md.setLocal(False, "main")
            the_module = md
        else:
            md.setLocal(True, "")

    if the_module is None:
        the_module = modules[0]

    if the_module is None:
        print("### soapMbias Error: module {} not present")
        sys.exit()

    npts = int((4096-64)/float(options.step))

    plt.ion()
    set_default_parameters(run_manager, polarity=options.polarity, hold_delay=options.hold_delay, threshold=options.threshold)
    test_mbias_scan(server, the_module,
                    1, options.channel, options.channel,
                    npts, options.min_val, options.max_val,
                    nsec=options.nsec, emin=options.emin)

    # Set all settings in the default state
    restore_default_state(server, options)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
