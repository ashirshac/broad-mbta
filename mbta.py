import requests
import pandas as pd
import argparse
from collections import defaultdict
import os
import timeit
import json

# Mbta written by Andrew Shirhsac ashirshac@gmail.com
# Provide some basic features of the MBTA rest apis and manipulation of the data they provide.
# Invocation example: python mbta.py
# Invocation example with optional flags: python mbta.py -c -v
# Change trip.txt in this directory to specify from/to stops for a trip.


class Mbta():

    def __init__(self):

        self.start = timeit.default_timer()

        # Accept optional input argument (csv, verbose)
        parser = argparse.ArgumentParser(description='Process several calls to mbta api')

        # Variable name	is indicated by	double dashes: --verbose	is args.verbose
        # Example python Mbta.py -c -v
        parser.add_argument("-v", "--verbose", help="Turn on output verbosity", action="store_true")
        parser.add_argument("-c", "--csv",     help="Flag to write optional csv files of key data structures", action="store_true")
        args = parser.parse_args()

        #self.verbose_mode = True # used for giving detailed output
        self.verbose_mode = args.verbose if args.verbose else False
        self.in_file = 'trip.txt'

        self.csv_write = True # used to capture key structures for reference
        self.csv_write = args.csv if args.csv else False

        print ('\nMbta Running with verbose_mode: {}, csv write: {}\n'.format(self.verbose_mode, self.csv_write))

        self.ENDPOINT = 'https://api-v3.mbta.com'
        self.API_KEY = 'e2e7f6ffc6f3427c9e478a76ae568ca3'
        path_routes = '/routes'
        self.path_trips = '/trips/'
        self.endpoint_routes = self.ENDPOINT + path_routes
        self.endpoint_stops = self.ENDPOINT + '/stops/'

        # Data that can be reused across multiple functions, questions
        self.trip_id_stop_dict = {}         # trip_id: trip_stop_lst
        self.stops_places_routes_dict = {}  # stopid|name|route: parent_place_id
        # All trip ids for all relevant routes:
        self.route_trip_ids_dict = {}
        self.stop_route_dict = {}

        self.csv_dir = 'csvs'
        if self.csv_write and not os.path.exists(self.csv_dir):
            os.makedirs(self.csv_dir)

    # Question 1 - get the subway routes and display on console.
    def run_get_routes(self):
        route_lst = self.get_route_names()

        print('\nQuestion 1 - Route Long Names:')

        for item in route_lst:
            print('\t{}'.format(item))

        print('\n\tElapsed  time: {}\n'.format(round(timeit.default_timer() - self.start, 2)))


    # Question 2 - get the subway routes with max/min stops and display on console.
    #   Print stops that connect 2 or more routes.
    def run_subway_routes_stop_max_min(self):
        # Detailed steps:
        # Get subway routes
        # Get Trip ids
        # Get stops for trip ids
        # Find route with most and fewest stops
        # Print name of that route
        # Print stops that connect 2 or more routes.

        # Get the route id, name dict for subway routes
        routes_dict = self.get_route_id_name_dict()

        # Get Trip ids - key: line id, value: trip id list
        #TODO1 route_trip_ids_dict = self.get_route_trip_ids_dict()
        self.route_trip_ids_dict = self.get_route_trip_ids_dict()

        # Get trip id dict - key: trip_id, value: stop list

        # Get unique list of all trip ids, and add the stops
        for trip_lst in self.route_trip_ids_dict.values():   #TODO1 this is empty after self chg
            # trip_lst is a list of trip ids
            for trip_id in trip_lst:
                # Put the key in the trip dict, None value for now
                # For each trip id, get stop ids
                trip_stop_lst = self.get_trip_stops(trip_id)
                self.trip_id_stop_dict.update({ trip_id: trip_stop_lst })

        ## self.trip_id_stop_dict has all trips and stops

        trip_id_stop_d = self.trip_id_stop_dict
        max_keys, max_list_len, min_keys, min_list_len = self.get_value_count(trip_id_stop_d)

        # Get route name for trip with most stops (max_keys list)
        # Since each trip has same stops in 2 directions, just list it once.

        trip_id = max_keys[0]
        #TODO1 don't need to pass self.route_trip_ids_dict
        route_nm = self.get_route_name_from_trip_id(trip_id, self.route_trip_ids_dict, routes_dict)
        print('\nQuestion 2.1 - The subway route with the most stops is {} with {} stops. Stops in 1 direction are: '.format(route_nm, max_list_len))

        # The stops are:
        for stop in self.trip_id_stop_dict[trip_id]:
            #TODO optional make this the list call
            stop_nm, place_id = self.get_stop_info(stop)
            print('\t{}'.format(stop_nm))

        trip_id = min_keys[0]
        #TODO1 don't need to pass self.route_trip_ids_dict
        route_nm = self.get_route_name_from_trip_id(trip_id, self.route_trip_ids_dict, routes_dict)
        print('\nQuestion 2.2 - The subway route with the fewest stops is {} with {} stops. Stops in 1 direction are: '.format(route_nm, min_list_len))

        # The stops are:
        for stop in self.trip_id_stop_dict[trip_id]:
            #TODO optional make this the list call
            stop_nm, place_id = self.get_stop_info(stop)
            print('\t{}'.format(stop_nm))
            #print('Stop suppressed for now: {}'.format(stop))


        print('\nGetting stop info to find connecting stops - call function.\n' )

        print('\n\tElapsed  time: {}\n'.format(round(timeit.default_timer() - self.start, 2)))

        ## For Q 2.3, Normalize stops by route. We'll have an entry for each route once

        self.get_stop_info_for_connecting_stops_via_list()

        print('\n\tElapsed  time: {}\n'.format(round(timeit.default_timer() - self.start, 2)))

        ### Question 3 begins
        # Read trip input from file:

        from_st, to_st = self.get_input_stations_for_trip(self.in_file)
        print('\nQuestion 3 \nFrom station: {}, To station: {}'.format(from_st, to_st))

        from_stop_id, from_stop_route = self.get_stop_id_from_places_routes(from_st)
        to_stop_id, to_stop_route = self.get_stop_id_from_places_routes(to_st)

        print('\nFrom stop_nm: {}, from_stop_id: {}, from_stop_route: {}'.format(from_st, from_stop_id, from_stop_route))
        print('To stop_nm: {}, to_stop_id: {}, to_stop_route: {}'.format(to_st, to_stop_id, to_stop_route))

        #TODO  alter print

        # See if we can find a single trip with the 2 stations we want
        trip_lst = []
        for trip_key, trip_station_ids_lst in self.trip_id_stop_dict.items():
            if str(from_stop_id) in trip_station_ids_lst and str(to_stop_id) in trip_station_ids_lst:

                trip_lst.append(trip_key)
                #print('Found trip_key with both stops: {}'.format(trip_key))
                break

        if len(trip_lst):
            print('Found tripid(s) for from/to: {} / {}: trip {}'.format(from_st, to_st, trip_lst))
        else:
            raise RuntimeError('Could not find single tripid(s) for from/to: {} / {}'.format(from_st, to_st))
            #print('Could not find single tripid(s) for from/to: {} / {}'.format(from_st, to_st))
            #TODO Must use alternate multi-line method

        #TODO Alter code to handle connections when not on same line

        # If found on 1 route:
        stops_with_from_to_lst = self.trip_id_stop_dict[ trip_lst[0] ]
        from_idx = stops_with_from_to_lst.index(from_stop_id)
        to_idx = stops_with_from_to_lst.index(to_stop_id)

        if self.verbose_mode:
            print('stoplist: {}\n'.format(stops_with_from_to_lst))
            print('From/to index: {}/{}'.format(from_idx, to_idx))

        if to_idx > from_idx:
            stops_in_order_lst = stops_with_from_to_lst[from_idx : to_idx + 1]
            if self.verbose_mode:
                print('Order of stops: {}'.format(stops_in_order_lst))
        else:
            stops_in_order_lst = stops_with_from_to_lst[ to_idx : from_idx + 1]
            stops_in_order_lst.reverse()
            if self.verbose_mode:
                print('Need to reverse the order of these: {}'.format(stops_in_order_lst))

        print('\nRoute: ')
        for stop in stops_in_order_lst:
            stop_name = self.get_stop_name_from_places_routes(stop)
            print('\t Stop name: {}, stop id: {}'.format(stop_name, stop))


        print('\n\tElapsed  time: {}\n'.format(round(timeit.default_timer() - self.start, 2)))


    def get_input_stations_for_trip(self, in_file):
        # Defaults to self.in_file

        if in_file is None:
            in_file = self.in_file

        from_st = None
        to_st = None

        with open(in_file, 'r') as fr:
            for line in fr.readlines():
                if not line.startswith('#'): # skip lines starting with '#'
                    line = line.rstrip()
                    fields = line.split('=')
                    if fields[0] == 'from':
                        from_st = fields[1]
                    elif fields[0] == 'to':
                        to_st = fields[1]
                    else:
                        raise RuntimeError("\n *** Error: Field other than 'from' or 'to' was specified in file: {}".format(in_file))

        from_st = from_st.replace("'", "")
        to_st   = to_st.replace("'", "")

        if from_st == None or to_st == None:
            raise RuntimeError('\n *** Error: Field other than from or to was specified in file: {}'.format(in_file))

        return from_st, to_st


    def get_stop_name_from_places_routes(self, stop_id):
        self.stops_places_routes_dict  # stopid|name|route: parent_place_id

        # Look in stops_places_route_dict for stop id
        for k in self.stops_places_routes_dict.keys():
            if stop_id in k:   # key: 12345|StationName
                stop_name = k.split('|')[1]
                route = k.split('|')[2]
                if self.verbose_mode:
                    print('Found key for stop_id: {} / {} / {}, on route: {}'.format(k, stop_id, stop_name, route))
                break

        #print('get_stop_name_from_places_routes Found stop_name for id: {} / {}, route:{}'.format(stop_name, stop_id, route))
        return stop_name

    def get_stop_id_from_places_routes(self, stop_name):
        # Given a stop_name, find the stop_id

        stop_id = None
        route = None
        # Look in stops_places_route_dict for name of stop. Get stop id
        for k in self.stops_places_routes_dict.keys():
            # Look for stop_name anywhere in stop name text
            #if k.startswith(stop_name):  # key: 12345|StationName
            if stop_name in k:   # key: 12345|StationName

                stop_id = k.split('|')[0]
                route = k.split('|')[2]
                #TODO could inspect for diretion
                # Taking 1st key
                if self.verbose_mode:
                    print('Found key for stop_name: {} / {}'.format(k, stop_id))
                break

        if self.verbose_mode:
            print('get_stop_id_from_places_routes Found id for stop_name: {} / {}, route:{}'.format(stop_name, stop_id, route))

        return stop_id, route


    def get_stop_info_for_connecting_stops_via_list(self):

        if self.verbose_mode:
            print('\nGetting stop info to find connecting stops via stop list.\n' )

        # In this process, because we have both directions, each stop will be listed twice.
        # Ensure we put 1 value into output dict and skip unnecessary api calls

        # self.stops_places_routes_dict -- key: stop | name | route	value: parent_place_id

        #stop_ids_lst = [] # used to only call api once per stop_id
        stop_ids_set = set()  # used to only call api once per stop_id

        for route, trip_lst in self.route_trip_ids_dict.items():
            for trip in trip_lst:
                # Add the stops from the next trip. Any dupes are not added to the set
                stop_ids_set = stop_ids_set.union( self.trip_id_stop_dict[trip] )

                # Create the dict - stop : route
                for stop_id in self.trip_id_stop_dict[trip]:
                    self.stop_route_dict[stop_id] = route
                    #print('TODO adding stop_id: {}, route: {}'.format(stop_id, self.stop_route_dict[stop_id]))


        # All stops are now in stop_ids_set. Use this to get the stop info.
        # Need to add the key for this stop_id
        # Get the stop info using the list capability to minimize api calls

        #print('stop id set: {}'.format(stop_ids_set))
        stop_tpl_lst = self.get_stop_list_info( list(stop_ids_set) )
        for stop_id, stop_name, parent_place_id in stop_tpl_lst:
            #print('stop_id: {}, stop_name: {}, place_id: {}'.format(stop_id, stop_name, parent_place_id)) #TODO Remove
            key = '{}|{}|{}'.format(str(stop_id), stop_name, self.stop_route_dict[stop_id])
            self.stops_places_routes_dict[key] = parent_place_id

        #stop_name, place_id = self.get_stop_info(stop_id)
        # end of previous logic



        # Dictionary built, scan for multiple stops(using places_id) in different routes
        # and add them to place_id route list
        multi_places_dict = defaultdict(list)

        for index, place_id in self.stops_places_routes_dict.items():
            stop_id, stop_name, route = index.split('|')

            if route in multi_places_dict.get(place_id, []):
                pass
            else:
                multi_places_dict[place_id].append(route)

        # Look for places with > 1 route

        keys_with_multiples = { k:v for k,v in multi_places_dict.items() if len(v) > 1 }

        # Using the place_id key in keys_with_multiples, look through values to find stops with those place_ids.
        # Those are the values we need to display
        stops_connecting_multiple_routes_dict = defaultdict(list)

        for index, places_id in self.stops_places_routes_dict.items():
            if places_id in keys_with_multiples.keys():
                #places_id has multiple routes
                stop_id, stop_name, route = index.split('|')
                stops_connecting_multiple_routes_dict[places_id].append([stop_id, stop_name, route])

        print('\nQuestion 2.3 - stops connecting 2 or more subway routes:')

        for places_id, values in stops_connecting_multiple_routes_dict.items():
            print('\nStop parent station: {}'.format(places_id))
            for value in values:
                print('\t Route: {}, \tName: {}, \tStopID: {}'.format(value[2], value[1], value[0]))

        ### End of questions 2.3


    def get_route_name_from_trip_id(self, in_trip_id, route_trip_ids_dict, routes_dict):

        route_key = None
        route_long_name = None
        for route, trip_lst in route_trip_ids_dict.items():
            if str(in_trip_id) in trip_lst:
                route_key = route
                route_long_name = routes_dict[route_key]

        # print('Matched route key: {}'.format(route_key))

        return route_long_name


    def get_value_count(self, trip_stop_dict):
        # Pass: trip id dict - key: trip_id, value: stop list
        # Return max and min stop count values, and max, min lists of keys
        # If there is > 1 max/min, return all in respective list

        max_list_len = 0
        min_list_len = 0

        max_keys = []
        min_keys = []

        for key in trip_stop_dict.keys():
            stop_len = len(trip_stop_dict[key])

            if stop_len > max_list_len:
                max_list_len = stop_len

            if min_list_len == 0:
                min_list_len = stop_len
            elif stop_len <= min_list_len:
                min_list_len = stop_len

        # Get the keys that match min, max and add to respective key lists
        for key in trip_stop_dict.keys():
            stop_len = len(trip_stop_dict[key])
            #print('k:v - {} length: {}, list:{}'.format( key, len(trip_stop_dict[key]), trip_stop_dict[key] ))
            if stop_len == max_list_len:
                max_keys.append(key)

            if stop_len == min_list_len:
                min_keys.append(key)

        return max_keys, max_list_len, min_keys, min_list_len



    # Get subway routes for Light Rail (type 0) and Heavy Rail (type 1)
    # Return a list of long_names for these routes
    def get_route_names(self):

        #Optional filter: fields[type] = 'long_name'
        params = {'filter[type]':'0,1'}
        #params_names_only = {'filter[type]':'0,1', 'fields[route]':'long_name'}

        route_filter = params
        resp = self.request_api(self.endpoint_routes, route_filter, self.verbose_mode)

        # Pass response dict to parser
        df = self.parse_response_to_dataframe(resp.json(), self.verbose_mode)

        if self.csv_write:
            Mbta.dataframe_to_csv('csvs/routes.csv', df)

        # df('attributes) is Series containing rows of dictionaries, key: long_name
        # df['attributes'] looks like:
        #0    {'long_name': 'Red Line'}
        #1    {'long_name': 'Mattapan Trolley'}

        subway_name_lst = []
        for index, value in df['attributes'].items():
            subway_name_lst.append(value['long_name'])

        return subway_name_lst


    # Get list of route links for subway routes
    # Return a list of long_names for these routes
    def get_route_links(self):

        params = {'filter[type]':'0,1'}

        route_filter = params
        resp = self.request_api(self.endpoint_routes, route_filter, self.verbose_mode)

        # Pass response dict to parser
        df = self.parse_response_to_dataframe(resp.json(), self.verbose_mode)

        # df['links']
        #     {'self': '/routes/Red'}

        links_lst = []
        for index, value in df['links'].items():
            #print("Index : {}, links Value : {}".format(index, value['self']))
            links_lst.append(value['self'])

        return links_lst



    def get_route_id_name_dict(self):

        #test: add stop, had no effect
        #/Users/ashirshac/Documents/personal/python/routes-route_patterns.json
        params = {'filter[type]':'0,1', 'include':'route_patterns' }
        # line,route_patterns

        route_filter = params
        #print('\nFilter: {}\n'.format(route_filter))

        resp = self.request_api(self.endpoint_routes, route_filter, self.verbose_mode)

        # parse json list of dicts
        df = pd.DataFrame( resp.json()['data'] )
        if self.csv_write:
            Mbta.dataframe_to_csv('csvs/route_patterns-data.csv', df, False)

        #Structure: /data/{index}/attributes/long_name
        #Structure: /data/{index}/id

        route_id_names = {}
        for i in range(len(df.index)):
            id        = df.iloc[i]['id']  # Red
            long_name = df.iloc[i]['attributes']['long_name'] # Red LIne
            #print('Id: {}, long name: {}'.format(id, long_name))
            route_id_names.update({ id:long_name })

        return route_id_names

    def get_route_trip_ids_dict(self):
        # Get all trip ids for all relevant routes.
        # These are 'representative trips'
        # Return: route_trip_id as dict with key: line_id(numeric), value: trip_id(numeric)

        #Structure:

        params = {'filter[type]':'0,1', 'include':'route_patterns' }
        # line,route_patterns

        route_filter = params

        resp = self.request_api(self.endpoint_routes, route_filter, self.verbose_mode)

        # parse json list of dicts
        df = pd.DataFrame( resp.json()['included'] )
        if self.csv_write:
            Mbta.dataframe_to_csv('csvs/route_patterns-included.csv', df, False)

        #print('df len: {}'.format(len(df.index)))
        # Series df['relationships']
        #    0     {'representative_trip': {'data': {'id': '41527...
        #    1     {'representative_trip': {'data': {'id': '41839...

        # df['relationships'] is Series containing rows of dictionaries, key: representative_trip

        route_trip_ids = defaultdict(list)  # key: line_id, value: trip_id list

        for index, value in df['relationships'].items():
            line_id = value['route']['data']['id']  # e.g. Green-D
            trip_id = value['representative_trip']['data']['id']  # e.g., 41527109
            route_trip_ids[line_id].append(trip_id)
            #print('Lines: line_id: {} trip_id: {}'.format(line_id, trip_id))

        return route_trip_ids


    def get_all_trip_ids(self):

        #TODO remove this if not being used, and take last lines only

        #Optional filter: fields[type] = 'long_name'
        '''
        include
        string
        Relationships to include.

        stop
        line
        route_patterns
        The value of the include parameter MUST be a comma-separated (U+002C COMMA, “,”) list of relationship paths. A relationship path is a dot-separated (U+002E FULL-STOP, “.”) list of relationship names. JSONAPI “include” behavior

        include=stop only works when filter[stop] is also used

        filter[stop]
        string
        '''

        # Get the route id, name dict
        route_trip_ids = self.get_route_trip_ids_dict()

        return route_trip_ids


    def get_stop_info(self, stop_id):

        #Structure: /data/{index}/attributes/description     description is the name

        params = {}

        stop_endpoint = self.endpoint_stops + str(stop_id)

        resp = self.request_api( stop_endpoint, params, self.verbose_mode)

        #TODO decide to parameterize/switchable
        with open('csvs/get_stop_info_{}.json'.format(stop_id), 'w') as file_writer: file_writer.write(json.dumps(resp.json()))

        # parse json list of dicts
        df = pd.DataFrame( resp.json()['data'] )

        if self.csv_write:
            Mbta.dataframe_to_csv('csvs/stop_id_{}.csv'.format(stop_id), df, False)

        stop_name = df['attributes']['description'] # ex: Braintree - Red Line

        # The parent_station > data > id element may or may not be present.
        # Populate with None if missing
        try:
            parent_station_data_id = df['relationships']['parent_station']['data']['id'] # ex: 'place-lake'
        except TypeError:
            #print('TypeError in get_stop_info')
            parent_station_data_id = None

        #print('get_stop_info StopId: {}, description as stop_name: {}, parent_station_data_id: {}'.format(stop_id, stop_name, parent_station_data_id))

        return stop_name, parent_station_data_id


    def get_stop_list_info(self, stop_lst):
        # Input list of stopids

        #Structure: /data/{index}/attributes/description     description is the name

        #TODO may need to add some include parameters

        # list of tuples for output
        stops_places_tpls = []

        # remove spaces and brackets #TODO single quotes
        lst = str(stop_lst).strip('[]').replace(' ', '').replace("'", "")
        #print('stop list: {}'.format(lst))

        params = {'filter[id]':lst}

        stop_endpoint = self.endpoint_stops

        resp = self.request_api( stop_endpoint, params, self.verbose_mode)

        #TODO parameterize as switch
        with open('csvs/get_stop_list_info.json', 'w') as file_writer: file_writer.write(json.dumps(resp.json()))
        #TODO test only:
        with open('csvs/get_stop_list_info_text.json', 'w') as file_writer: file_writer.write(resp.text)

        #TODO left off here: need to recursively parse....

        # parse json list of dicts
        df = pd.DataFrame( resp.json()['data'] )
        '''
        df['attributes'][0]
        {'address': None, 'at_street': None, 'description': 'Braintree - Red Line', 'latitude': 42.208371, 'location_type': 0, 'longitude': -71.001423, 'municipality': 'Braintree', 'name': 'Braintree', 'on_street': None, 'platform_code': None, 'platform_name': 'Red Line', 'vehicle_type': 1, 'wheelchair_boarding': 1}
        df['attributes'][0]['description'] -> 'Braintree - Red Line'
        df['id'][0] -> '70105'
        df['relationships'][0]['parent_station']['data']['id'] -> 'place-brntn
        len(df['attributes']) -> 2 (0,1)
        df['attributes'].size -> 2
        '''

        #for index, value in df['attributes'].items():
        #    #print(f"Index : {index}, Value : {value}")
        #    print(f"Index : {index}, Value : {value['description']}")

        i = 0
        while i < df['attributes'].size:
            stop_name = df['attributes'][i]['description']
            stop_id = df['id'][i]

            # The parent_station > data > id element may or may not be present.
            # Populate with None if missing
            try:
                 # ex: 'place-lake'
                parent_station_data_id = df['relationships'][i]['parent_station']['data']['id']
            except TypeError:
                #print('TypeError in get_stop_info') #TODO remove
                parent_station_data_id = None

            #print('{} stop_name: {}, stop_id: {}, place_id: {}'.format(i, stop_name, stop_id, parent_station_data_id))
            stops_places_tpls.append( (stop_id, stop_name, parent_station_data_id) )
            i += 1

        if self.csv_write:
            Mbta.dataframe_to_csv('csvs/stop_ids.csv', df, False)

        #stop_name = df['attributes']['description'] # ex: Braintree - Red Line
        #place_id = df['relationships']['parent_station']['data']['id'] # ex: 'place-lake'
        #print('Id: {}, long name: {}, place_id:'.format(place_id, stop_name))

        print('\n\tElapsed  time: {}\n'.format(round(timeit.default_timer() - self.start, 2)))
        return stops_places_tpls



    def get_trip_stops(self, trip_id):
        # Get the stops for a specific trip id
        # Structure:
        #   trips/41837263?include=stops

        params = {'include':'stops'}

        trip_endpoint = self.ENDPOINT + self.path_trips + trip_id + '?'

        resp = self.request_api(trip_endpoint, params, self.verbose_mode)

        # parse json list of dicts
        df = pd.DataFrame( resp.json()['data'] )

        if self.csv_write:
            Mbta.dataframe_to_csv('csvs/trips_for_id.csv', df, False)

        # relationships > stops > data > id, type
        # Series: df['relationships']

        df['relationships']['stops']['data']

        #id = df['relationships']['stops']['data'][0]['id']
        #stop_type = df['relationships']['stops']['data'][0]['type']

        trip_stop_lst = []
        for item in df['relationships']['stops']['data']:
            id = item['id']
            #type = item['type']
            trip_stop_lst.append(id)

        ''' Example:
          "stops":{
            "data":[{
                "id":"70105",
                "type":"stop"
              },
              {
                "id":"70104",
                "type":"stop"
              },
        '''
        return trip_stop_lst

    def parse_response_to_dataframe(self, resp_json_dict, verbose_mode=False):
        """
        Take a json response and parse it into a Pandas Dataframe for analysis.

        Args:
            resp_json_dict (json/dict):
                Essentially a json dictionary of values returned from  API.
                The structure is a list of dictionaries.
                Each key will become a column name.
                Each value will become a row value under that column name.

            verbose_mode (bool): optionally prints dataframe sample

        Returns:
            Dataframe (obj): Dataframe containing keys as column names and values as rows.

        Errors: None - you can interrogate status code before attempting parsing.
        """

        results_lst = resp_json_dict['data']
        df = pd.DataFrame(results_lst)    #ingest list of dicts into dataframe

        if verbose_mode:
            print ("\n",df.head(5))

        return df


    # For parameters, include all except api_key, which will be added here
    def request_api(self, endpoint, parameters, verbose_mode=False):
        """
        Send a request to an API and return a response obj

        Args:
            endpoint (str):   The uri of the query api.
                                    Example: https://api.localytics.com/v1/query
            parameters (dict): Dictionary of parameters and values

            verbose_mode (bool): optionally prints query params

        Returns:
            Response (obj): A Response object. Interesting values can be retrieved
                            using response.json() method.

        Errors: in case of errors, will only have response.status_code
                Or will raise an error.
                Under successful calls, status_code = 200.
        """

        # add the api_key, which is needed for each request
        parameters.update( {'api_key':self.API_KEY} )
        headers = {'accept': 'application/vnd.api+json'}
        requests.adapters.DEFAULT_RETRIES = 5

        if verbose_mode:
            print("Endpoint: ",endpoint)
            for key in parameters.keys():
                print ("API Key value: {}:{}".format(key, parameters[key]))

        response = requests.get(endpoint, params=parameters, headers=headers)

        if verbose_mode:
            print("Api status code: {}".format(response.status_code))

        # Check status codes and act depending on success/failure.
        if response.status_code == requests.codes.ok: #200 is good, everything else is an error
            pass
        elif response.status_code == 400:
            print("400 Bad request - check parameters")
            response.raise_for_status()
        else:
            #print("\n\nError:",response.json()['error'],"\n\n")
            print("parameters: ",parameters)
            response.raise_for_status()

        if self.verbose_mode:
            print('\nresp response: {}\n'.format(response.text))

        return response


    def dataframe_to_csv(local_file, df, verbose_mode = False, gz_flag = False):
        # Set compression flag to True by default
        # fileEncoding is 'utf8' by default

        if gz_flag:
            gz = 'gzip'
            local_file = local_file + '.gz'
        else:
            gz = None

        if verbose_mode:
            print('Writing to csv, file: {}'.format(local_file))

        df.to_csv(path_or_buf = local_file
                  , sep=','
                  , na_rep=''
                  , float_format=None
                  , header=True
                  , index=False
                  , index_label=None
                  , mode='w'
                  , encoding='utf-8'
                  , compression=gz
                  , quoting=None
                  , quotechar='"', line_terminator='\n'
                  , chunksize=None
                  , date_format=None, doublequote=True
                  , escapechar=None, decimal='.')


### Control running the main functions
if __name__ == '__main__':
    mbta = Mbta()

    mbta.run_get_routes()
    mbta.run_subway_routes_stop_max_min()

    #mbta.get_route_links() # test method
    #mbta.get_trip_stops() #test method
    #mbta.get_stop_info(70105) # test method

    #tpl_lst = mbta.get_stop_list_info([70105,70038])

    '''
    tpl_lst = mbta.get_stop_list_info(['70094','70092','70090','70088','70086','70084','70082','70080','70078','70076','70074','70072','70070','70068','70066','70064','70061'])
    for stop_id, stop_name, place_id in tpl_lst:
            print('stop_id: {}, stop_name: {}, place_id: {}'.format(stop_id, stop_name, place_id))

    print( 'tpl_lst[0][0]: {}'.format(tpl_lst[0][0]))
    '''

