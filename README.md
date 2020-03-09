# MBTA rest api demonstration program

Any questions can be sent to ashirshac@gmail.com

> 1) Retrieves data representing subway routes: 'Light Rail' (type 0) and 'Heavy Rail' (type 1). 
The program lists their “long names” on the console.
> 2) The program displays the following additional information:
The name of the subway route with the most stops as well as a count of its stops 
The name of the subway route with the fewest stops as well as a count of its stops 
A list of the stops that connect two or more subway routes along with the relevant route names for each of those stops.
> 3) Provide 2 stops in file trip.txt. The program will list the route to take.
NB: This version is limited to 2 stops on the same line.
```
The program provides optional args to print detailed diagnostics and/or save key data structures to csv files. 
Invocation example with optional flags: 
  python mbta.py -c -v
Invocation to show which args are available: 
  python mbta.py -h   

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  Turn on output verbosity
  -c, --csv      Flag to write optional csv files of key data structures
  
Unit tests:
 python test_mbta.py
```

## To run locally, from the main directory:
```
Tested on python 3.7.3

Get source via git.
Move to directory into which you'll install the code.
$ git clone https://github.com/ashirshac/mbta.git

$ change to 'mbta' dir

Setup a virtual environment and install required packages via pip and requirements.txt
If necessary install virtualenv

$ virtualenv venv
on linux:
$ source venv/bin/activate
on Windows:
> venv\Scripts\activate
$ pip install -r requirements.txt
$ python mbta.py
$ python test_mbta.py

