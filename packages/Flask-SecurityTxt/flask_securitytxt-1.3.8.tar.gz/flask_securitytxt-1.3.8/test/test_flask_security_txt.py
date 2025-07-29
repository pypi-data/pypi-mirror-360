"""
A test case for the Flask-SecurityTxt extension.
"""

from unittest import TestCase

from flask import Flask

from flask_security_txt import SecurityTxt


class TestFlaskSecurityTxt(TestCase):
    """
    Test the view end-points of the Flask app. Verify correct functionality by
    asserting that each known end-point has a response with an HTTP response
    code of 200.
    """

    def setUp(self) -> None:
        app = Flask(__name__)
        self.ext = SecurityTxt(app)
        self.app = app.test_client()

    # Have PyLint ignore the casing of this method, in favor of the casing
    # conventions of the unittest module.
    #
    # pylint: disable=invalid-name
    def assertOK(self, request_uri: str):
        """
        Helper function to assert that the specified request URI returns a
        response with an HTTP status code of 200.

        @param request_uri:
            The request URI asserted to result in an HTTP status code of 200.
        """
        self.assertEqual(self.app.get(request_uri).status_code, 200)

    def test_security_txt(self):
        """
        Assert that the security.txt end-point returns a response with an HTTP
        status code of 200.
        """
        self.assertOK("/.well-known/security.txt")
