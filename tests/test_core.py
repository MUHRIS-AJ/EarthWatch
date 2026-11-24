import unittest
from unittest.mock import patch
from transport import SourceError
import core

NASA={"events":[{"id":"E1","title":"Wildfire near Example","categories":[{"title":"Wildfires"}],
"link":"https://eonet.gsfc.nasa.gov/api/v3/events/E1","geometry":[{"date":"2026-11-01","type":"Point","coordinates":[20,30]}]}]}
USGS={"features":[{"id":"us1","properties":{"title":"M 4.1 example earthquake","mag":4.1,"time":1793000000000,"url":"https://earthquake.usgs.gov/earthquakes/eventpage/us1"},"geometry":{"coordinates":[21,31,4]}}]}

class EarthWatchTests(unittest.TestCase):
    @patch("core.request_json")
    def test_two_sources(self, fetch):
        fetch.side_effect=[NASA,USGS]
        data=core.run("all")
        self.assertEqual(data["match_count"],2)
        self.assertEqual({x["provider"] for x in data["events"]},{"NASA EONET","USGS"})
    @patch("core.request_json")
    def test_partial_failure(self, fetch):
        fetch.side_effect=[SourceError("offline"),USGS]
        result=core.run("earthquake")
        self.assertEqual(result["match_count"],1)
        self.assertEqual(len(result["source_errors"]),1)
    @patch("core.request_json",side_effect=SourceError("offline"))
    def test_both_failed(self, _):
        with self.assertRaises(SourceError): core.run("all")
    def test_input_check(self):
        with self.assertRaises(ValueError): core.run("")

if __name__=="__main__":unittest.main()
