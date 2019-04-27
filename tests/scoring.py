import json
import requests
import unittest

class BasicTests(unittest.TestCase):
 
###############
#### tests ####
###############

    def test_endpointcheck(self):
        
        data = {'title':'Pretty decent', 
        'review':'Pretty decent game.'}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        req = requests.post("http://127.0.0.1:80/score", data=json.dumps(data), headers=headers)
        self.assertNotEqual(len(req.json()), 0)
        assert req.json()['stars'] == 3

if __name__ == "__main__":
    unittest.main()   