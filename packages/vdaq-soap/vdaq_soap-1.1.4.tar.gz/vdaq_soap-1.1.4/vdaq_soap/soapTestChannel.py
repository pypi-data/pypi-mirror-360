#!/usr/bin/env python3
"""Do a Hold delay scan."""
import sys
from argparse import ArgumentParser

import daqpp.soap
import matplotlib.pyplot as plt

from vdaq_soap.soapCheckAliVATA import restore_default_state
from vdaq_soap.soapCheckAliVATA import set_default_parameters
from vdaq_soap.soapCheckAliVATA import test_TDCs


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
    parser.add_argument("--mbias", dest="mbias", default=300,
                        type=int, help="Chip Main bias")
    parser.add_argument("--hold_delay", dest="hold_delay", default=175,
                        type=int, help="Chip hold delay")
    parser.add_argument("--polarity", dest="polarity", default=0,
                        type=int, help="Signal polarity")
    parser.add_argument("--nsec", dest="nsec", default=10,
                        type=int, help="Chip Main bias")
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
        print("### CheckAliVATAq Error: module {} not present")
        sys.exit()

    plt.ion()
    set_default_parameters(run_manager, 
                           polarity=options.polarity, 
                           hold_delay=options.hold_delay,
                           threshold=options.threshold,
                           mbias=options.mbias)
    test_TDCs(server, the_module, channel=options.channel, nsec=options.nsec, emin=options.emin)

    # Set all settings in the default state
    restore_default_state(server, options)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
