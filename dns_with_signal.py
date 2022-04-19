
"""
-----------------------------------------------------------
IP / DNS name lookup script. Uses Python sockets to do so 
efficiently. 

Python multi-processing is used to speed up the processing of
a long list of IP's

The results are converted to an IP lookup dict() that another
script might use for efficient cached lookups. 

There may be more 'pythonic' or better ways to do some of this.
My goal here is in part readability for moderate Python skills
like mine.
-----------------------------------------------------------
"""

import socket
import multiprocessing as mp
import re
import json
from time import time

import signal

from random import *

def dns_timeout(a,b):
    raise Exception("DNS timeout")

def process_dns_lookup(line):
    # This function does forward DNS lookup
    #
    # The following print helps show the progress of the multi-processing.
    # Note the order may vary between runs!

    print('DOING DNS lookup of: ', line)

    item=None

    res=re.match('^[0-9\.]+\s*$', line)
    if res:
        # IP address, get name
        ip=line
        lookup='IP'

        try:
            signal.signal(signal.SIGALRM, dns_timeout)
            signal.alarm(3)

            result=socket.gethostbyaddr(ip)
            name=result[0]
            item = [ip, name]
        except Exception as exc:
            print("Exception caught: ", exc)
            sys.exc_clear()
            signal.alarm(0)
            item = None
    else:
        # My original code did IP or Name lookup and some more
        # processing, but that obscured the main point. 
        print("I'm not looking up DNS names today.")    

    return(item)

def random_ip():
    rand_ip=str(randrange(1,126))
    for i in range(0,3):
        rand_ip = rand_ip + '.' + str(randrange(1,255))
    return(rand_ip)

def do_dns_lookups(initial_filename):
    print()

    """
    # For field use...
    # Read info from file, file format: one IP or hostname per line.
    with open(initial_filename,'r') as fh:
        inv_list=fh.readlines()
    
    # Note you could also hard-code a manual list:

    # Sample manual test input to make this self-contained for test-drives:
    #inv_list=['208.67.222.222','104.92.231.139']
    """

    # Random test input for more fun with this:
    inv_list=list()
    for i in range(0,50):
        inv_list.append(random_ip())

    ### MULTIPROCESS THE LOOKUPS ###
    # The key point is that with a bigger list, any items that are 
    # slow to obtain a reply do not hold up other processing. 
    # (Try it with say 100 random inputs, for instance. Or do
    # one lookup at a time by setting the pool size to 1.)
    pool = mp.Pool(mp.cpu_count())
    
    # Do one lookup at a time by uncommenting the next line.
    #pool = mp.Pool(1)

    results=pool.map(process_dns_lookup, inv_list)
    
    # Take the results and make a dict of them.
    print()
    lookup_dict=dict()
    for item in results:
        print('RESULT ITEM: ', item)
        if (item != None):
            # Return value of None means the lookup failed.
            # We could return a list with item[1] set to "FAILED"
            # or such, if we wanted to retain knowledge of failed
            # lookups for future retries (skip them, or hope they resolve
            # in the future?)
            ip = item[0]
            name = item[1]
            lookup_dict[ip]=name

    return(lookup_dict)

def main():
    start_time=time()

    lookup_dict = do_dns_lookups('initial-inventory.txt')

    # Show the ip lookup dict(). This could also be embedded in another
    # Python program, or written to a file such a program imports. 

    print()
    print('IP LOOKUP DICT: ')
    print(json.dumps(lookup_dict, indent=4, sort_keys=True))
    print()
    print()

    elapsed=time()-start_time
    print('Elapsed time: ' + f"{elapsed:.2f}" + ' seconds.')
    print('\n\n')
    return

# ------------------------------------------------------------------------------

# Main program to allow testing this script. 
#
# The above functions can (of course) be imported for use in other scripting. 
if __name__ == "__main__":  
    main()

