import unittest
from app.main import app


class InventoryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_post_response(self):
        payload = {
            "item_name": "test name",
            "quantity": 1,
            "item_value": 1,
        }
        response = self.app.post('/inventory', json=payload)
        expected_resp = 200
        self.assertEqual(response.status_code, expected_resp)
        resp = self.app.get('/inventory')
        assert resp.data is not None

    def test_put_response(self):
        payload = {
            "id": 13,
            "quantity": 234567
        }
        response = self.app.put('/inventory', json=payload)
        expected_resp = 200
        self.assertEqual(response.status_code, expected_resp)

    def test_delete_response(self):
        payload = {
            "id": 13,
        }
        response = self.app.delete('/inventory', json=payload)
        expected_resp = 200
        self.assertEqual(response.status_code, expected_resp)
