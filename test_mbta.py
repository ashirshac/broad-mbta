import unittest
from mbta import Mbta

### Class to test mbta.py

class TestMbta(unittest.TestCase):

    def setUp(self):
        self.mbta = Mbta()
        self.mbta.verbose_mode = False


    def test_get_input_stations_for_trip_valid(self):
        from_st, to_st = self.mbta.get_input_stations_for_trip('trip_valid.txt')
        self.assertEqual( from_st, "Davis", 'from_st should be Davis')
        self.assertEqual( to_st, "Kendall", 'to_st should be Kendall')

    #def test_get_input_stations_for_trip_invalid(self):
        #from_st, to_st = self.mbta.get_input_stations_for_trip('trip_invalid.txt')
        #self.assertIn('*** Error: Field other than from or to was specified in file' in str(context.exception))
        #self.assertRaises(RuntimeError, self.mbta.get_input_stations_for_trip, '\n *** Error: Field other than from or to was specified in file: trip_invalid.txt')


    def test_route_list(self):
        route_lst = self.mbta.get_route_names()
        self.assertEqual( len(route_lst), 8, "Subway Route List length should be 8")
        self.assertIn( 'Red Line', route_lst,  "Red Line should be in route list")
        self.assertIn( 'Blue Line', route_lst, "Blue Line should be in route list")


    def test_get_all_trip_ids(self):
        trip_ids_dict = self.mbta.get_all_trip_ids()
        self.assertIn( 'Red', trip_ids_dict.keys(),  "Red should be in trip id list")
        self.assertIn( 'Blue', trip_ids_dict.keys(),  "Blue should be in trip id list")


    def test_get_stop_info_70105(self):
        stop_name, parent_station_data_id = self.mbta.get_stop_info(70105)
        self.assertEqual( 'Braintree - Red Line', stop_name, "Incorrect stop info (name)")
        self.assertEqual( 'place-brntn', parent_station_data_id, "Incorrect stop info (parent_station_data_id)")


    def test_get_stop_info_65(self):
        stop_name, parent_station_data_id = self.mbta.get_stop_info(65)
        #self.assertEqual( 'null', stop_name, "Incorrect stop info (name)")
        self.assertIsNone( stop_name, "Incorrect stop info (name)")
        self.assertIsNone( parent_station_data_id, "Incorrect stop info (parent_station_data_id)")


    def test_response_status(self):

        stop_endpoint = '{}{}'.format(self.mbta.endpoint_stops, str(70105))
        params = {'include':'invalidIncludeValue'}

        exception_flag = False
        exc_text = ''
        try:
            resp = self.mbta.request_api( stop_endpoint, params, False)
        except Exception as exc:
            exception_flag = True
            exc_text = str(exc)
            #print('exc is: {}'.format(exc_text))

        error_txt = '400 Client Error: Bad Request for url'

        self.assertEqual( exception_flag, True, "Incorrect status_code for stop info (name)")
        self.assertIn( error_txt, exc_text, "Incorrect 400 Bad Request error text")

    def test_max_min_counts(self):
        stop_dict = {'Smallest': ['70169','70167','70165','70163','70161'],
                     'Largest':['70169','70167','70165','70163','70161','99999']}
        max_key_lst, max_list_len, min_key_lst, min_list_len = self.mbta.get_value_count(stop_dict)
        self.assertEqual( max_key_lst[0], 'Largest', "Incorrect max key")
        self.assertEqual( min_key_lst[0], 'Smallest', "Incorrect min key")
        self.assertEqual( max_list_len, 6, "Incorrect max list len")
        self.assertEqual( min_list_len, 5, "Incorrect min list len")


    def test_blue_line_stops(self):
        stop_lst = ['70038','70039','70040','70041','70042','70043','70044','70045','70046','70047',
                    '70048','70049','70050','70051','70052','70053','70054','70055','70056','70057']

        stop_name_lst = []
        for stop in stop_lst:
            stop_name = self.mbta.get_stop_info(stop)
            stop_name_lst.append(stop_name)
        # Look for state anywhere in stop list
        # lowercase list and convert list to string, then strip list brackets
        self.assertIn( 'state', str([x for x in stop_name_lst]).lower().strip('[]'), "state not in Blue Line stop list")


    def test_blue_line_stops_using_list_fn(self):
        #stop_lst = ['70038','70039','70040','70041','70042','70043','70044','70045','70046','70047',
        #            '70048','70049','70050','70051','70052','70053','70054','70055','70056','70057']

        stop_lst = [70105,70038]
        #stop_name_lst = []
        #for stop in stop_lst:
        #stop_name = self.mbta.get_stop_list_info(stop_lst)
        #stop_name_lst.append(stop_name)

        tpl_lst = self.mbta.get_stop_list_info(stop_lst)
        # returns list of tuples of (stop_name, place_id)
        self.assertEqual( tpl_lst[0][0], '70105', 'Incorrect stop id: {}'.format(tpl_lst[0][0]) )
        self.assertEqual( tpl_lst[0][1], 'Braintree - Red Line', 'Incorrect stop: {}'.format(tpl_lst[0][1]) )
        self.assertEqual( tpl_lst[0][2], 'place-brntn', 'Incorrect place: {}'.format(tpl_lst[0][2]) )

        self.assertEqual( tpl_lst[1][0], '70038', 'Incorrect stop id: {}'.format(tpl_lst[1][0]) )
        self.assertEqual( tpl_lst[1][1], 'Bowdoin - Blue Line - Wonderland', 'Incorrect stop: {}'.format(tpl_lst[1][1]) )
        self.assertEqual( tpl_lst[1][2], 'place-bomnl', 'Incorrect place: {}'.format(tpl_lst[1][2]) )

        #tpl_lst[0]
        #for stop_name, place_id in tpl_lst:
        #    #print('stop_name: {}, place_id: {}'.format(stop_name, place_id))



        #stop list: 70105,70038
        #0 stop_name: Braintree - Red Line, stop_id: 70105, place_id: place-brntn
        #1 stop_name: Bowdoin - Blue Line - Wonderland, stop_id: 70038, place_id: place-bomnl
        #Elapsed time: 0.7

        #stop_name: Braintree - Red Line, place_id: place-brntn
        #stop_name: Bowdoin - Blue Line - Wonderland, place_id: place-bomnl


        # Look for state anywhere in stop list
        # lowercase list and convert list to string, then strip list brackets
        #self.assertIn( 'state', str([x for x in stop_name_lst]).lower().strip('[]'), "state not in Blue Line stop list")


if __name__ == '__main__':
    unittest.main()
