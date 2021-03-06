# coding=utf-8
"""Views to handle url requests. Flask main entry point is also defined here.
:copyright: (c) 2013 by Tim Sutton, Akbar Gumbira
:license: GPLv3, see LICENSE for more details.
"""
import json

from flask import render_template, Response, request, current_app
from werkzeug.exceptions import default_exceptions

# App declared directly in __init__ as per
# http://flask.pocoo.org/docs/patterns/packages/#larger-applications
from . import APP
from users.utilities.helpers import make_json_error, send_async_mail
from users.utilities.validator import (
    is_email_address_valid,
    is_required_valid,
    is_boolean)
from users.models import (
    add_user,
    edit_user,
    delete_user,
    get_user,
    get_user_by_email,
    get_all_users,
    )


@APP.route('/')
def map_view():
    """Default view - shows a map with users."""
    #noinspection PyUnresolvedReferences
    information_modal = render_template('html/information_modal.html')
    #noinspection PyUnresolvedReferences
    data_privacy_content = render_template('html/data_privacy.html')
    #noinspection PyUnresolvedReferences
    user_form_template = render_template('html/user_form.html')
    user_menu = dict(
        add_user=True,
        download=True,
        reminder=True
    )
    #noinspection PyUnresolvedReferences
    #pylint: disable=W0142
    user_menu_button = render_template(
        'html/user_menu_button.html',
        **user_menu
    )

    context = dict(
        current_tag_name='None',
        error='None',
        project_name=APP.config['PROJECT_NAME'],
        project_favicon_file=APP.config['PROJECT_FAVICON_FILE'],
        user_icons=APP.config['USER_ICONS'],
        information_modal=information_modal,
        data_privacy_content=data_privacy_content,
        user_form_template=user_form_template,
        user_menu=user_menu,
        user_menu_button=user_menu_button
    )
    #noinspection PyUnresolvedReferences
    #pylint: disable=W0142
    return render_template('html/index.html', **context)


@APP.route('/users.json', methods=['GET'])
def users_view():
    """Return a json document of users who have registered."""
    # Create model user
    all_users = get_all_users()

    #noinspection PyUnresolvedReferences
    json_users = render_template('json/users.json', users=all_users)

    users_json = (
        '{'
        ' "users": %s'
        '}' % json_users
    )
    # Return Response
    return Response(users_json, mimetype='application/json')


@APP.route('/add_user', methods=['POST'])
def add_user_view():
    """Controller to add a user.

    Handle post request via ajax and add the user to the user.db

    :returns: A new json response as in users.json.
    :rtype: HttpResponse

    .. note:: JavaScript on client must update the map on ajax completion
        callback.
    """
    # return any errors as json - see http://flask.pocoo.org/snippets/83/
    for code in default_exceptions.iterkeys():
        APP.error_handler_spec[None][code] = make_json_error

    # Get data from form
    name = str(request.form['name']).strip()
    email = str(request.form['email']).strip()
    website = str(request.form['website'])
    email_updates = str(request.form['email_updates'])
    latitude = str(request.form['latitude'])
    longitude = str(request.form['longitude'])
    twitter = request.form["twitter"]

    # Validate the data:
    message = {}
    if not is_required_valid(name):
        message['name'] = 'Name is required'
    if not is_email_address_valid(email):
        message['email'] = 'Email address is not valid'
    if not is_required_valid(email):
        message['email'] = 'Email is required'
    elif not is_boolean(email_updates):
        message['email_updates'] = 'Notification must be checked'

    # Check if the email has been registered by other user:
    user = get_user_by_email(email)
    if user is not None:
        message['email'] = 'Email has been registered by other user.'

    # Process data
    if len(message) != 0:
        message['type'] = 'Error'
        return Response(json.dumps(message), mimetype='application/json')
    else:
        # Modify the data:
        if email_updates == 'true':
            email_updates = True
        else:
            email_updates = False

        if len(website.strip()) != 0 and 'http' not in website:
            website = 'http://%s' % website

        # Create model for user and add user
        guid = add_user(
            name=name,
            email=email,
            website=website,
            email_updates=bool(email_updates),
            latitude=float(latitude),
            longitude=float(longitude),
            social_account=dict(twitter=twitter),
            )

    # Prepare json for added user
    added_user = get_user(guid)

    # Send Email Confirmation:
    subject = '%s User Map Registration' % APP.config['PROJECT_NAME']
    #noinspection PyUnresolvedReferences
    body = render_template(
        'text/registration_confirmation_email.txt',
        project_name=APP.config['PROJECT_NAME'],
        url=APP.config["PUBLIC_URL"],
        user=added_user)
    recipient = added_user.email
    send_async_mail(
        sender=current_app.config["MAIL_ADMIN"],
        recipients=[recipient],
        subject=subject,
        text_body=body,
        html_body='')

    #noinspection PyUnresolvedReferences
    added_user_json = render_template('json/users.json', users=[added_user])
    # Return Response
    return Response(added_user_json, mimetype='application/json')


@APP.route('/edit/<guid>')
def edit_user_view(guid):
    """View to edit a user with given guid.

    :param guid: The unique identifier of a user.
    :type guid: str

    :returns: Page where user can edit his/her data
    :rtype: HttpResponse
    """
    user = get_user(guid)
    #noinspection PyUnresolvedReferences
    user_json = render_template('json/user.json', user=user)
    #noinspection PyUnresolvedReferences
    user_popup_content = render_template(
        'html/user_info_popup_content.html', user=user
    )
    #noinspection PyUnresolvedReferences
    information_modal = render_template('html/information_modal.html')
    #noinspection PyUnresolvedReferences
    data_privacy_content = render_template('html/data_privacy.html')
    #noinspection PyUnresolvedReferences
    user_form_template = render_template('html/user_form.html')
    user_menu = dict(
        edit_user=True,
        delete_user=True,
        download=True
    )
    #noinspection PyUnresolvedReferences
    #pylint: disable=W0142
    user_menu_button = render_template(
        'html/user_menu_button.html',
        **user_menu
    )

    context = dict(
        current_tag_name='None',
        error='None',
        project_name=APP.config['PROJECT_NAME'],
        project_favicon_file=APP.config['PROJECT_FAVICON_FILE'],
        user_icons=APP.config['USER_ICONS'],
        user=user_json,
        edited_user_popup_content=user_popup_content,
        information_modal=information_modal,
        data_privacy_content=data_privacy_content,
        user_form_template=user_form_template,
        user_menu=user_menu,
        user_menu_button=user_menu_button
    )
    #noinspection PyUnresolvedReferences
    #pylint: disable=W0142
    return render_template('html/edit.html', **context)


@APP.route('/edit_user', methods=['POST'])
def edit_user_controller():
    """Controller to edit a user.

    Handle post request via ajax and edit the user to the user.db

    :returns: A new json response containing status of editing
    :rtype: HttpResponse
    """
    # return any errors as json - see http://flask.pocoo.org/snippets/83/
    for code in default_exceptions.iterkeys():
        APP.error_handler_spec[None][code] = make_json_error

    # Get data from form
    guid = str(request.form['guid'])
    name = str(request.form['name']).strip()
    email = str(request.form['email']).strip()
    website = str(request.form['website'])
    email_updates = str(request.form['email_updates'])
    latitude = str(request.form['latitude'])
    longitude = str(request.form['longitude'])
    twitter = request.form["twitter"]

    # Validate the data:
    message = {}
    if not is_required_valid(name):
        message['name'] = 'Name is required'
    if not is_email_address_valid(email):
        message['email'] = 'Email address is not valid'
    if not is_required_valid(email):
        message['email'] = 'Email is required'
    elif not is_boolean(email_updates):
        message['email_updates'] = 'Notification must be checked'

    # Modify the data:
    if email_updates == 'true':
        email_updates = True
    else:
        email_updates = False

    if len(website.strip()) != 0 and 'http' not in website:
        website = 'http://%s' % website

    # Process data
    if len(message) != 0:
        message['type'] = 'Error'
        return Response(json.dumps(message), mimetype='application/json')
    else:
        # Edit User
        guid = edit_user(
            guid=guid,
            name=name,
            email=email,
            website=website,
            email_updates=bool(email_updates),
            latitude=float(latitude),
            longitude=float(longitude),
            social_account=dict(twitter=twitter),
            )

    edited_user = get_user(guid)
    #noinspection PyUnresolvedReferences
    edited_user_json = render_template('json/user.json', user=edited_user)
    #noinspection PyUnresolvedReferences
    edited_user_popup_content = render_template(
        'html/user_info_popup_content.html', user=edited_user
    )
    edited_user_response = dict()
    edited_user_response['edited_user'] = edited_user_json
    edited_user_response['edited_user_popup'] = edited_user_popup_content
    # Return Response
    return Response(
        json.dumps(edited_user_response),
        mimetype='application/json')


@APP.route('/delete/<guid>', methods=['POST'])
def delete_user_view(guid):
    """View to delete a user with given guid.

    :param guid: The unique identifier of a user.
    :type guid: str
    :returns: index page
    :rtype: HttpResponse
    """
    # Delete User
    delete_user(guid)
    return APP.config["PUBLIC_URL"]


@APP.route('/download')
def download_view():
    """View to download users.

    Handle post request via ajax and return file to browser

    :returns: A csv file containing all users
    :rtype: HttpResponse
    """
    csv_users = "ID|NAME|WEBSITE|LONGITUDE|LATITUDE|TWITTER"
    users = get_all_users()
    for i, user in enumerate(users, start=1):
        csv_users += '\n%i|%s|%s|%s|%s|%s' % (
            i,
            user.name,
            user.website,
            user.longitude,
            user.latitude,
            user.social_account.twitter,
            )

    filename = '%s-users.csv' % APP.config['PROJECT_NAME']
    content = "attachment;filename='%s'" % filename
    return Response(
        csv_users,
        mimetype='text/csv',
        headers={'Content-Disposition': content})


@APP.route('/reminder', methods=['POST'])
def reminder_view():
    """View to send reminder email to user.

    :returns: JSON Response containing status of the process
    :rtype: JSONResponse
    """
    message = dict()

    email = str(request.form['email']).strip()
    user = get_user_by_email(email)

    if user is None:
        message['type'] = 'Error'
        message['email'] = 'Email is not registered in our database.'
        return Response(json.dumps(message), mimetype='application/json')

    # Send Email Confirmation:
    subject = '%s - User Map Edit Link' % APP.config['PROJECT_NAME']
    #noinspection PyUnresolvedReferences
    body = render_template(
        'text/registration_confirmation_email.txt',
        project_name=APP.config['PROJECT_NAME'],
        url=APP.config["PUBLIC_URL"],
        user=user)
    send_async_mail(
        sender=current_app.config["MAIL_ADMIN"],
        recipients=[email],
        subject=subject,
        text_body=body, html_body='')

    message['type'] = 'Success'
    return Response(json.dumps(message), mimetype='application/json')
