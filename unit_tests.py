import os
import requests as r
from unittest import TestCase
from dotenv import load_dotenv
load_dotenv()

BASE_URL = 'https://kldsi7sxw0.execute-api.eu-west-2.amazonaws.com/prod/catalyst/'
KEY = os.environ.get('CLIENT_ID', '')
GLOBAL_TIMEOUT = 20

class NGDTestCase(TestCase):

    def test_invalid_query_params(self):
        """
        Test for invalid query parameters in the NGD API.
        This function sends a request with an unsupported query parameter and checks the response.
        It expects a 400 status code and specific error messages in the response.
        """
        endpoint = BASE_URL + 'features/lnd-fts-land-1/items'
        response = r.get(
            endpoint,
            params={'test': 'should-fail'},
            headers = {'key': KEY},
            timeout=GLOBAL_TIMEOUT
        )
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        keys = json_response.keys()
        self.assertIn('description', keys)
        self.assertIn('errorSource', keys)
        startswith_text = 'Not supported query parameter(s): test. Supported NGD parameters are:'
        self.assertTrue(json_response.get('description', '').startswith(startswith_text))
        self.assertEqual(json_response.get('errorSource', ''), 'OS NGD API')

    def test_hiearchical_request(self):
        wkt = '''
        GEOMETRYCOLLECTION(
            MULTIPOLYGON(
                ((558288 104518, 558288 104528, 558298 104528, 558298 104518, 558288 104518)),
                ((558388 104318, 558388 104328, 558398 104328, 558398 104318, 558388 104318))
            ),
            LINESTRING(
                558288 104518, 558298 104528, 558398 104328, 558398 104318
            )
        )'''
        endpoint = BASE_URL + 'features/multi-collection/items/geom-col'
        response = r.get(
            endpoint,
            params = {
                'wkt': wkt,
                'filter-crs': 27700,
                'crs': 3857,
                'collection': 'lnd-fts-land,bld-fts-building,wtr-fts-water',
                'hierarchical-output': True,
                'use-latest-collection': True,
            },
            headers = {
                'erroneous-header': 'should-be-ignored',
                'key': KEY
            },
            timeout=GLOBAL_TIMEOUT
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        response_keys = list(json_response.keys())
        self.assertEqual(len(response_keys), 3)
        self.assertTrue(response_keys[0].startswith('lnd-fts-land-'))
        feature_keys = list(
            json_response \
            .get('lnd-fts-land-3',{}) \
            .get('searchAreas',{})[0] \
            .keys()
        )
        self.assertListEqual(feature_keys, [
            'type',
            'links',
            'timeStamp',
            'numberReturned',
            'features',
            'code',
            'numberOfRequests',
            'telemetryData',
            'searchAreaNumber'
        ])

    def test_flat_request(self):
        endpoint = BASE_URL + 'features/multi-collection/items/limit-col'
        response = r.get(
            endpoint,
            params = {
                'crs': 'http://www.opengis.net/def/crs/EPSG/0/27700',
                'collection': 'gnm-fts-crowdsourcednamepoint,bld-fts-building-1,trn-ntwk-pathlink',
                'use-latest-collection': True,
                'limit': 213,
                'key': KEY
            },
            timeout=GLOBAL_TIMEOUT
        )
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        response_keys = list(json_response.keys())
        self.assertListEqual(response_keys, [
            'type',
            'numberOfRequests',
            'numberOfRequestsByCollection',
            'numberReturned',
            'numberReturnedByCollection',
            'features',
            'timeStamp'
        ])
        number_returned_by_collection = json_response.get('numberReturnedByCollection', {})
        self.assertIn('bld-fts-building-1', number_returned_by_collection)
        self.assertEqual(len(number_returned_by_collection), 3)
        self.assertTrue(all(v == 213 for v in number_returned_by_collection.values()))
        self.assertEqual(json_response.get('numberReturned', 0), 639)
        number_of_requests_by_collection = json_response.get('numberOfRequestsByCollection', {})
        self.assertEqual(len(number_of_requests_by_collection), 3)
        self.assertTrue(all(v == 3 for v in number_of_requests_by_collection.values()))
        self.assertEqual(json_response.get('numberOfRequests', 0), 9)
        first_feature_keys = list(json_response.get('features', [])[0].keys())
        self.assertListEqual(first_feature_keys, [
            'id',
            'type',
            'geometry',
            'properties',
            'collection'
        ])

    def test_invalid_key(self):
        """
        Test for invalid API key in the NGD API.
        This function sends a request with an invalid key and checks the response.
        It expects a 401 status code and specific error messages in the response.
        """
        endpoint = BASE_URL + 'features/lnd-fts-land-1/items'
        response = r.get(
            endpoint,
            headers = {'key': 'invalid-key'},
            timeout=GLOBAL_TIMEOUT
        )
        self.assertEqual(response.status_code, 401)
        json_response = response.json()
        self.assertDictEqual(
            json_response,
            {
                "description": "Missing or unsupported API key provided.",
                "errorSource": "OS NGD API"
            }
        )
