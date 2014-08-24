# coding=utf-8
"""Tests for the application web urls.
:copyright: (c) 2013 by Tim Sutton
:license: GPLv3, see LICENSE for more details.
"""
from flask.ext.testing import TestCase as FlaskTestCase
from flask.ext.migrate import downgrade, upgrade

from users import LOGGER
from users.views import APP
from users.database import db
from users.models import add_user, get_user  # noqa


class AppTestCase(FlaskTestCase):
    """Test the application."""
    def create_app(self):
        app = APP
        app.config["TESTING"] = True
        return app

    #noinspection PyPep8Naming
    def setUp(self):
        """Constructor."""
        self.correct_user_data = dict(
            name='Akbar',
            email='test@gmail.com',
            website='http://www.ac.com',
            email_updates=True,
            latitude=12.32,
            longitude=-13.03,
            twitter="johndoe",
            )

        self.wrong_user_data = dict(
            name='',
            email='testgmaicom',
            website='http://www.ac.com',
            email_updates=True,
            latitude=12.32,
            longitude=-13.03,
            twitter="johndoe",
            )

        self.edited_user_data = dict(
            name='Akbar Gumbira',
            email='test@gmail.com',
            website='http://www.ac.com',
            email_updates=True,
            latitude=12.32,
            longitude=-13.03,
            twitter="mrsmith",
            )

    @classmethod
    def setUpClass(cls):
        with APP.test_request_context():
            upgrade(revision="head")

    #noinspection PyPep8Naming
    def tearDown(self):
        """Destructor."""
        db.session.remove()

    @classmethod
    def tearDownClass(cls):
        with APP.test_request_context():
            downgrade(revision="base")

    def test_home(self):
        """Test the home page works."""
        try:
            return self.client.post('/', data=dict(), follow_redirects=True)
        except Exception, e:
            LOGGER.exception('Basic front page load failed.')
            raise e

    def test_users_view(self):
        """Test the users json response works."""
        data = self.correct_user_data
        data["social_account"] = {
            "twitter": data.pop("twitter", ""),
        }
        guid = add_user(**data)
        if guid is not None:
            try:
                result = self.client.get(
                    '/users.json',
                    data=dict(),
                    follow_redirects=True)
                self.assertTrue('Akbar' in result.data)
            except Exception, e:
                LOGGER.exception('Basic front page load failed.')
                raise e

    def test_add_user_view(self):
        """Test the user added json response works."""
        # Test correct data
        try:
            result = self.client.post(
                '/add_user',
                data=self.correct_user_data,
                follow_redirects=True)
            data = result.data
            self.assertTrue('Akbar' in data)
        except Exception, e:
            LOGGER.exception('Page load failed.')
            raise e

        # Test wrong data
        try:
            result = self.client.post(
                '/add_user',
                data=self.wrong_user_data,
                follow_redirects=True,
                )
            self.assertTrue('Error' in result.data)
        except Exception, e:
            LOGGER.exception('Page load failed.')
            raise e

    def test_edit_user_view(self):
        """Test the edit_user_view function.
        """
        data = self.wrong_user_data
        data["social_account"] = {
            "twitter": data.pop("twitter", ""),
        }

        guid = add_user(**data)
        url = '/edit/%s' % guid
        try:
            return self.client.get(url, data=dict(), follow_redirects=True)
        except Exception, e:
            LOGGER.exception('Basic front page load failed.')
            raise e

    def test_edit_user_controller(self):
        """Test the edit_user_view function.
        """
        data = self.correct_user_data
        data["social_account"] = {
            "twitter": data.pop("twitter", ""),
        }

        guid = add_user(**data)

        edited_data = self.edited_user_data
        edited_data['guid'] = guid

        url = '/edit_user'
        try:
            result = self.client.post(
                url,
                data=edited_data,
                follow_redirects=True)
            data = result.data
            self.assertTrue('Akbar Gumbira' in data)
        except Exception, e:
            LOGGER.exception('Basic front page load failed.')
            raise e

    def test_delete_user_view(self):
        """Test the delete_user_view function.
        """
        data = self.correct_user_data
        data["social_account"] = {
            "twitter": data.pop("twitter", ""),
        }

        guid = add_user(**data)
        url = '/delete/%s' % guid
        try:
            self.client.post(
                url,
                data=dict(),
                follow_redirects=True)
            user = get_user(guid)
            self.assertIsNone(user)

        except Exception, e:
            LOGGER.exception('Basic front page load failed.')
            raise e

    def test_download_view(self):
        """Test the download_view function.
        """
        url = '/download'
        try:
            return self.client.get(url, data=dict(), follow_redirects=True)
        except Exception, e:
            LOGGER.exception('Basic front page load failed.')
            raise e

    def test_reminder_view(self):
        """Test the download_view function.
            """
        data = self.correct_user_data
        data["social_account"] = {
            "twitter": data.pop("twitter", ""),
        }

        url = '/reminder'

        # Test OK
        guid = add_user(**data)
        if guid is not None:
            email = data['email']
            try:
                result = self.client.post(
                    url, data=dict(email=email), follow_redirects=True)
                self.assertTrue('Success' in result.data)
            except Exception, e:
                LOGGER.exception('Basic front page load failed.')
                raise e

        # Test Error
        try:
            result = self.client.post(
                url,
                data=dict(
                    email='notok@email.com'),
                follow_redirects=True)
            self.assertTrue('Error' in result.data)
        except Exception, e:
            LOGGER.exception('Basic front page load failed.')
            raise e
