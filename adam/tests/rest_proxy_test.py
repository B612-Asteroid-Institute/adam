from adam.rest_proxy import _RestProxyForTest
from adam.rest_proxy import AuthenticatingRestProxy
from adam.rest_proxy import RetryingRestProxy
import unittest

from unittest import mock


# TODO: fix this so that we are testing with fake access tokens

class RetryingRestProxyTest(unittest.TestCase):
    """Unit tests for retrying rest proxy.
    """

    def test_good_response(self):
        rest = _RestProxyForTest()
        retrying_rest = RetryingRestProxy(rest)

        expected_data = {}

        def check_input(data_dict):
            self.assertEqual(expected_data, data_dict)
            return True

        # A 200 (or 204 for deletes) results in no retrying.
        rest.expect_post("/test", check_input, 200, {'a': 1})
        code, response = retrying_rest.post("/test", {})
        self.assertEqual(200, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_get("/test?a=1&b=2", 200, {'a': 1})
        code, response = retrying_rest.get("/test?a=1&b=2")
        self.assertEqual(200, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_delete("/test?a=1&b=2", 204)
        code, _ = retrying_rest.delete("/test?a=1&b=2")
        self.assertEqual(204, code)

    def test_retry_on_retryable_error(self):
        rest = _RestProxyForTest()
        retrying_rest = RetryingRestProxy(rest)

        expected_data = {}

        def check_input(data_dict):
            self.assertEqual(expected_data, data_dict)
            return True

        # A 403, 502, or 503 results in retrying.
        rest.expect_post("/test", check_input, 403, {'a': 1})
        rest.expect_post("/test", check_input, 200, {'a': 1})
        code, response = retrying_rest.post("/test", {})
        self.assertEqual(200, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_get("/test?a=1&b=2", 502, {'a': 1})
        rest.expect_get("/test?a=1&b=2", 200, {'a': 1})
        code, response = retrying_rest.get("/test?a=1&b=2")
        self.assertEqual(200, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_delete("/test?a=1&b=2", 503)
        rest.expect_delete("/test?a=1&b=2", 204)
        code, _ = retrying_rest.delete("/test?a=1&b=2")
        self.assertEqual(204, code)

    def test_no_retry_on_nonretryable_error(self):
        rest = _RestProxyForTest()
        retrying_rest = RetryingRestProxy(rest)

        expected_data = {}

        def check_input(data_dict):
            self.assertEqual(expected_data, data_dict)
            return True

        # An error other than 403, 502, and 503 results in no retrying.
        rest.expect_post("/test", check_input, 404, {'a': 1})
        code, response = retrying_rest.post("/test", {})
        self.assertEqual(404, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_get("/test?a=1&b=2", 418, {'a': 1})
        code, response = retrying_rest.get("/test?a=1&b=2")
        self.assertEqual(418, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_delete("/test?a=1&b=2", 500)
        code, _ = retrying_rest.delete("/test?a=1&b=2")
        self.assertEqual(500, code)

    def test_eventually_stops_retrying(self):
        rest = _RestProxyForTest()
        retrying_rest = RetryingRestProxy(rest, num_tries=3)

        expected_data = {}

        def check_input(data_dict):
            self.assertEqual(expected_data, data_dict)
            return True

        # The retryable errors will eventually no longer be retried.
        rest.expect_post("/test", check_input, 403, {'a': 1})
        rest.expect_post("/test", check_input, 403, {'a': 1})
        rest.expect_post("/test", check_input, 403, {'a': 1})
        code, response = retrying_rest.post("/test", {})
        self.assertEqual(403, code)
        self.assertDictEqual({'a': 1}, response)

        rest.expect_get("/test?a=1&b=2", 502, {'a': 1})
        rest.expect_get("/test?a=1&b=2", 502, {'a': 1})
        rest.expect_get("/test?a=1&b=2", 502, {'a': 1})
        code, response = retrying_rest.get("/test?a=1&b=2")
        self.assertEqual(502, code)
        self.assertDictEqual({'a': 1}, response)

        # Mixing errors is allowed - all count toward the same cumulative total.
        # The error on the final try will be reported.
        rest.expect_delete("/test?a=1&b=2", 403)
        rest.expect_delete("/test?a=1&b=2", 502)
        rest.expect_delete("/test?a=1&b=2", 503)
        code, _ = retrying_rest.delete("/test?a=1&b=2")
        self.assertEqual(503, code)


class AuthenticatingRestProxyTest(unittest.TestCase):
    """Unit tests for authenticating rest proxy.

    """

    @mock.patch('adam.rest_proxy.RestRequests')
    def test_authc_use_credentials(self, mocked_rest):
        mocked_rest.post = mock.MagicMock(return_value=(200, {}))
        mocked_rest.get = mock.MagicMock(return_value=(200, {}))
        mocked_rest.delete = mock.MagicMock(return_value=(200, {}))
        auth_rest = AuthenticatingRestProxy(mocked_rest)

        auth_rest.post("/create_something", {})
        mocked_rest.post.assert_called_with('/create_something', {}, use_credentials=True)

        auth_rest.get("/get_something")
        mocked_rest.get.assert_called_with('/get_something', use_credentials=True)

        auth_rest.delete("/delete_something")
        mocked_rest.delete.assert_called_with('/delete_something', use_credentials=True)


    def test_post(self):
        rest = _RestProxyForTest()
        auth_rest = AuthenticatingRestProxy(rest)

        expected_data = {}

        def check_input(data_dict):
            self.assertEqual(expected_data, data_dict)
            return True

        expected_data = {}
        rest.expect_post("/test", check_input, 200, {})
        auth_rest.post("/test", {})

        expected_data = {'a': 1, 'b': 2}
        rest.expect_post("/test", check_input, 200, {})
        auth_rest.post("/test", {'b': 2, 'a': 1})

    def test_get(self):
        rest = _RestProxyForTest()
        auth_rest = AuthenticatingRestProxy(rest)

        rest.expect_get("/test", 200, {})
        auth_rest.get("/test")

        rest.expect_get("/test?a=1&b=2", 200, {})
        auth_rest.get("/test?a=1&b=2")

        rest.expect_get("/test?a=1&b=2", 4123, {'c': 3})
        code, response = auth_rest.get("/test?a=1&b=2")
        self.assertEqual(code, 4123)
        self.assertEqual(response, {'c': 3})

    def test_delete(self):
        # DELETE behaves exactly like GET, so only the basics are tested.
        rest = _RestProxyForTest()
        auth_rest = AuthenticatingRestProxy(rest)

        rest.expect_delete("/test", 200)
        auth_rest.delete("/test")

        rest.expect_delete("/test?a=1&b=2", 200)
        auth_rest.delete("/test?a=1&b=2")


if __name__ == '__main__':
    unittest.main()
