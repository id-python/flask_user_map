# coding=utf-8
"""Module for saving all configuration."""
import os

# PROJECT_NAME: Project Name.
# It would override page title, email confirmation to user, so on.
PROJECT_NAME = 'Python Indonesia'

# PUBLIC_URL: Public URL that is used for publishing this apps.
# It will be used for detail of the email confirmation, and other things if
# it's needed
PUBLIC_URL = 'http://members.python.or.id'

# PROJECT_FAVICON_FILE: Path to project favicon file
PROJECT_FAVICON_FILE = '/static/img/favicon.png'

# PATH TO SQLITE DB
SQLITE_DB_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        'users.db'
    )
)

# Alternatively, set to ``127.0.0.1`` for development/testing.
MAIL_SERVER = 'smtp.gmail.com'

# Alternatively, set to ``25`` for development/testing.
MAIL_PORT = 587

MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = ''
MAIL_PASSWORD = ''

# Set the value to ``True`` to suppress email sending.
# Useful for testing/development where machine doesn't have
# mail server installed in it.
MAIL_SUPPRESS_SEND = False

# MAIL ADMINISTRATOR
MAIL_ADMIN = ('Python Indonesia User Map Administrator', MAIL_USERNAME)

# USER ICONS: All icon paths that are used.
USER_ICONS = dict(
    user='/static/img/marker.png',
    shadow='/static/img/marker-shadow.png'
)

# Directory location for log file
LOG_DIR = '/tmp'

# By default it uses postgres, hence you'll need to ``psycopg2``.
# If you're using MySQL, refer to
# http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# for details.
SQLALCHEMY_DATABASE_URI = "postgresql://scott:tiger@localhost:5432/mydatabase"
