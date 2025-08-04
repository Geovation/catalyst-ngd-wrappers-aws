import os
import requests as r
import unittest
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
        print(KEY or 'NO KEY')
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        keys = json_response.keys()
        self.assertIn('description', keys)
        self.assertIn('errorSource', keys)
        startswith_text = 'Not supported query parameter(s): test. Supported NGD parameters are:'
        self.assertTrue(json_response.get('description', '').startswith(startswith_text))
        self.assertEqual(json_response.get('errorSource', ''), 'OS NGD API')

    def test_complex_request(self):
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
        self.assertEqual(feature_keys, [
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

        if __name__ == '__main__':
            unittest.main()
