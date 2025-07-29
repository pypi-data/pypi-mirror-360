import logging
import sys

import click

from biolib import api, biolib_errors
from biolib.biolib_api_client.api_client import BiolibApiClient
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.user import sign_in, sign_out


@click.command(help='Login your to BioLib account with web browser')
@click.option(
    '-w',
    is_flag=True,
    default=False,
    required=False,
    type=bool,
    help='Automatically open the login page in the default web browser',
)
def login(w: bool) -> None:  # pylint: disable=invalid-name
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    sign_in(open_in_default_browser=w)


@click.command(help='Logout of your BioLib account')
def logout() -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    sign_out()


@click.command(help='Prints out the full name of the user logged in')
def whoami() -> None:
    client = BiolibApiClient.get()
    if client.is_signed_in:
        user_uuid = None
        if client.access_token is None:
            print('Unable to fetch user credentials. Please try logging out and logging in again.')
            exit(1)
        try:
            user_uuid = client.decode_jwt_without_checking_signature(jwt=client.access_token)['payload']['public_id']
        except biolib_errors.BioLibError as error:
            print(
                f'Unable to reference user public_id in access token:\n {error.message}',
                file=sys.stderr,
            )
            exit(1)
        response = api.client.get(path=f'/user/{user_uuid}/')
        user_dict = response.json()
        email = user_dict['email']
        intrinsic_account = [account for account in user_dict['accounts'] if account['role'] == 'intrinsic'][0]
        display_name = intrinsic_account['display_name']
        print(f'Name: {display_name}\nEmail: {email}\nLogged into: {client.base_url}')
    else:
        print('Not logged in', file=sys.stderr)
        exit(1)
