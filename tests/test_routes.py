import unittest
import make_a_data_object


class TestTesting(unittest.TestCase):
    """Just testing that the test framework is in place."""
    def test_testing(self):
        self.assertTrue(True)


class TestRoutes(unittest.TestCase):
    """Instead of a fixture, also a context can be used, like this

           with make_a_data_object.app.test_request_context('/'):
               assert flask.request.path == '/'
    """

    def setUp(self):
        make_a_data_object.app.testing = True
        self.app = make_a_data_object.app.test_client()

    def test_get_hello(self):
        rv = self.app.get('/hello')
        self.assertIn(b"Hello world.", rv.data)
        self.assertEqual(200, rv.status_code)

    def test_get_missing_route(self):
        rv = self.app.get('/thisdoesnotexist')
        self.assertEqual(404, rv.status_code)

    def test_post_missing_route(self):
        rv = self.app.post('/thisdoesnotexist')
        self.assertEqual(404, rv.status_code)

    def test_get_index_template(self):
        rv = self.app.get('/')
        self.assertEqual(200, rv.status_code)
        self.assertIn(b"<!doctype html>", rv.data)


if __name__ == '__main__':
    unittest.main()
