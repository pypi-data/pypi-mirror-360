import argparse
import os
import requests
from getpass import getpass
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from xdg import xdg_data_home
from dotenv import load_dotenv

from qmenta.core.errors import (
    ActionFailedError,
    ConnectionError,
    InvalidResponseError,
    PlatformError
)


class InvalidLoginError(ActionFailedError):
    """
    When the provided credentials are incorrect, or when the used token
    is not valid.
    """
    pass


class Needs2FAError(ActionFailedError):
    """
    When a 2FA code must to be provided to log in.
    """
    pass


class Auth:
    """
    Class for authenticating to the platform.
    Do not use the constructor directly, but use the login() function to
    create a new authentication.

    Attributes
    ----------
    base_url : str
        The base URL of the platform. Example: 'https://platform.qmenta.com'
    token : str
        The authentication token, returned by the platform when logging in.
    """
    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url
        self.token = token
        self._session: Optional[requests.Session] = None

    @staticmethod
    def qmenta_auth_env_file() -> Path:
        """
        Return the path of the qmenta auth env file
        """
        return xdg_data_home() / 'QMENTA' / 'auth' / '.env'

    @classmethod
    def from_env(cls, dot_env: Optional[Path] = None) -> 'Auth':
        """
        Create an Auth object using the QMENTA_URL and QMENTA_AUTH_TOKEN
        environment variables.
        If the variables are not set in the environment, but they exist in
        the file dot_env, then those values are used.

        This function can be used to create an Auth object in scripts to
        communicate with QMENTA Platform, after the `qmenta-auth` command
        has been run to authenticate.

        Parameters
        ----------
        dot_env: Path
            The location of the .env file to read the environment variables.
            If no value is supplied, qmenta_auth_env_file() is used as
            the default value. (Optional)

        Raises
        ------
        InvalidLoginError
            When one of the needed environment variables was not found
        """

        # Loads variables from the .env file, but does NOT override existing
        #   values already set in the environment.
        # No exception is raised if the file is not found.
        dotenv_file = dot_env or cls.qmenta_auth_env_file()
        load_dotenv(dotenv_file)

        try:
            token: str = os.environ["QMENTA_AUTH_TOKEN"]
            url: str = os.environ["QMENTA_URL"]
        except KeyError as e:
            raise InvalidLoginError(f'Missing environment variable: {e}')

        print(f'Using authentication token for {url}')
        return cls(url, token)

    @classmethod
    def login(cls, username: str, password: str,
              code_2fa: Optional[str] = None,
              ask_for_2fa_input: bool = False,
              base_url: str = 'https://platform.qmenta.com') -> 'Auth':
        """
        Authenticate to the platform using username and password.

        Parameters
        ----------
        username : str
            The username to log in on the platform. For all new platform
            accounts, this is the e-mail address of the user.
            Example: 'example@qmenta.com'
        password : str
            The QMENTA platform password of the user.
        code_2fa : str
            The 2FA code that was sent to your phone (optional).
        ask_for_2fa_input: bool
            When set to True, the user is asked input the 2FA code
            in the command-line interface when it is needed. If the user does
            not have 2FA enabled, no input is requested.
            This is useful for scripts.
            When set to False, a Needs2FAError exception is raised when
            a 2FA code is needed. This is useful for GUIs.
            Default value: False
        base_url : str
            The URL of the platform to connect to.
            Default value: 'https://platform.qmenta.com'

        Returns
        -------
        Auth
            The Auth object that was logged in with.

        Raises
        ------
        ConnectionError
            If there was a problem setting up the network connection with the
            platform.
        InvalidResponseError
            If the platform returned an invalid response.
        InvalidLoginError
            If the login was invalid. This can happen when the
            username/password combination is incorrect, or when the account is
            not active or 2FA is required to be set up.
        Needs2FAError
            When a login attempt was done without a valid 2FA code.
            The 2FA code has been sent to your phone, and must be provided
            in the next call to the login function.
        """
        url: str = urljoin(base_url, '/login')

        try:
            r: requests.Response = requests.post(
                url, data={
                    'username': username, 'password': password,
                    'code_2fa': code_2fa
                }
            )
        except requests.RequestException as e:
            raise ConnectionError(str(e))

        try:
            d: Dict[str, Any] = r.json()
        except ValueError:
            raise InvalidResponseError(
                f'Could not decode JSON for response {r}')

        try:
            if d["success"] != 1:
                # Login was not successful
                if 'account_state' in d and d['account_state'] == '2fa_need':
                    if ask_for_2fa_input:
                        input_2fa = input("Please enter your 2FA code: ")
                        return Auth.login(
                            username, password, code_2fa=input_2fa,
                            ask_for_2fa_input=True, base_url=base_url
                        )
                    else:
                        raise Needs2FAError(
                            'Provide the 2FA code sent to your phone, '
                            'or set the ask_for_2fa_input parameter'
                        )
                else:
                    raise InvalidLoginError(d['error'])

            token: str = d['token']
        except KeyError as e:
            raise InvalidResponseError(f'Missing key: {e}')

        return cls(base_url, token)

    def get_session(self) -> requests.Session:
        if not self._session:
            self._session = requests.Session()

            # Session may store other cookies such as 'route'
            auth_cookie = requests.cookies.create_cookie(
                name='AUTH_COOKIE', value=self.token
            )
            # Add or update it
            self._session.cookies.set_cookie(auth_cookie)
            self._session.headers.update(self._headers())

        return self._session

    def _headers(self) -> Dict[str, str]:
        h = {
            'Mint-Api-Call': '1'
        }
        return h


def write_dot_env_file(token: str, url: str,
                       filename: Optional[Path] = None) -> None:
    """
    Write the token and URL to a .env file.

    Parameters
    ----------
    token: str
        The token to write to the .env file
    url: str
        The URL to write to the .env file
    filename: Path
        The filename of the .env file to write to (optional).
        If no value is supplied, it will be written to the default
        location qmenta_auth_env_file().

    Raises
    ------
    OSError
        When the output file could not be written
    """
    filepath = filename or Auth.qmenta_auth_env_file()
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    with open(filepath, 'w') as envFile:
        print(f'QMENTA_URL={url}', file=envFile)
        print(f'QMENTA_AUTH_TOKEN={token}', file=envFile)

    print(f'Auth token was written to {filepath}')


def validate_url(url: str) -> None:
    """
    Validate the URL as a valid http or https URL.

    Raises
    ------
    ValueError
        When the URL is not valid
    """
    parsed_url = urlparse(url)

    if parsed_url.scheme == 'http':
        print('WARNING: Only use http for local testing.')
    elif not parsed_url.scheme == 'https':
        raise ValueError(
            'URL should start with https://. '
            'Example: https://platform.menta.com'
        )
    if parsed_url.path not in ['', '/']:
        raise ValueError(
            'Provide only the root URL of the backend server. '
            'Example: https://platform.qmenta.com'
        )
    if parsed_url.username or parsed_url.password or parsed_url.query:
        raise ValueError(
            'Provide only the root URL of the backend server. '
            'Example: https://platform.qmenta.com'
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            'Log in on QMENTA platform and store the authentication '
            'token in a .env file. Username and password may be '
            'provided as parameters, or will be asked as user input. '
        )
    )
    parser.add_argument('--username', help='Username to login',)
    parser.add_argument('--password', help='Password')
    parser.add_argument(
        'url', help='Platform URL, for example: https://platform.qmenta.com')
    args = parser.parse_args()

    try:
        validate_url(args.url)
    except ValueError as err:
        print(err)
        return

    username = args.username or input("Username: ")
    password = args.password or getpass()

    try:
        auth = Auth.login(
            username=username, password=password,
            ask_for_2fa_input=True, base_url=args.url
        )
    except PlatformError as err:
        print(err)
        return

    write_dot_env_file(token=auth.token, url=auth.base_url)


if __name__ == '__main__':  # pragma: no cover
    main()
