#!/usr/bin/env python3
"""Do a Hold delay scan."""
import sys
from argparse import ArgumentParser
import numpy as np
import daqpp.soap
import matplotlib.pyplot as plt

from vdaq_soap.soapCheckAliVATA import set_module_param
from vdaq_soap.soapCheckAliVATA import wait_for_end_of_run, get_monitor_data

def remove_outliers(data, cut=2.0, outliers=False, debug=False):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        outliers: if True, return the outliers rhater than remove them
        debug: be verbose if True.

    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    if outliers:
        indx = np.where(s > cut)[0]
    else:
        indx = np.where(s < cut)[0]

    return indx

def maskNoisyChannels(server, cut=7.5, do_run=False):
    """Main Entry."""

    if do_run:
        # Stop the run if running
        print("Check if the RUnManager is active and running")
        run_manager = daqpp.soap.RunManager("main", server)
        S = run_manager.getStatus()
        if S.status == "Running":
            print("Stopping run")
            run_manager.stopRun()

        # Create a new pedestal run
        server.createRunManager("pedestal", "main")
        run_manager = daqpp.soap.RunManager("main", server)
        set_module_param(run_manager, "ro_mode", 1)

        # Reset all monitor data
        for the_module in server.getAllModules():
        	the_module.resetMonitorData()


        run_manager.setMaxEvents(5000)
        run_manager.startRun()
        wait_for_end_of_run(run_manager, 5.0)
        server.createRunManager("data", "main")
        run_manager = daqpp.soap.RunManager("main", server)
        run_manager.GetReady()
        

    # Get the module
    the_module = None
    modules = server.getAllModules()
    for the_module in modules:
        print("Module {}".format(the_module.name))



        # Get the data
        data = get_monitor_data(the_module)
        noise =  data['histograms']['noise']
        channels = remove_outliers(noise['data'], cut, outliers=True)

        chanlist = ""
        for chan in channels:
            chanlist += "{},".format(chan)

        try:
            if chanlist[-1]==',':
                chanlist = chanlist[:-1]

            the_module.getParameter("command").set_value("setMask|{}=1".format(chanlist))

        except IndexError:
            pass



            print(channels)

def main():
    """Entry Point."""
    parser = ArgumentParser()
    parser.add_argument("--host", dest="host", default="localhost",
                        type=str, help="The soap server")
    parser.add_argument("--port", dest="port", default=50000,
                        type=int, help="The soap port")
    parser.add_argument("--cut", dest="cut", default=7.5,
                        type=float, help="The cut to remove outliers")
    parser.add_argument("--run", action="store_true", default=False, help="Add to make a pedestal run.")

    options = parser.parse_args()

    # This is where we connect with the server
    try:
        server = daqpp.soap.DAQppClient(options.host, options.port)

    except Exception as E:
        print(("Could not connect to the server\n{}".format(E)))
        sys.exit()


    maskNoisyChannels(server, cut=options.cut, do_run=options.run)

if __name__ == "__main__":
    main()
