"""
This module contains the class for interacting with the Goodgame Empire API's authentication-related functions.

The `Auth` class provides methods for checking the availability of usernames, registering new accounts, logging in, and recovering passwords. It is a subclass of `BaseGgeSocket`.
"""

from ..base_gge_socket import BaseGgeSocket

import requests


class Auth(BaseGgeSocket):
    """
    A class for interacting with the Goodgame Empire API's authentication-related functions.

    This class provides methods for checking the availability of usernames, registering new accounts, logging in, and recovering passwords. It is a subclass of `BaseGgeSocket`.
    """

    def check_username_availability(
        self, name: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Check the availability of a username.

        Args:
            name (str): The username to check.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("vln", {"NOM": name})
            if sync:
                response = self.wait_for_json_response("vln")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def check_user_exists(
        self, name: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Check if a user exists.

        Args:
            name (str): The username to check.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("vln", {"NOM": name})
            if sync:
                response = self.wait_for_json_response("vln")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def register(
        self, username: str, email: str, password: str, quiet: bool = False
    ) -> dict:
        """
        Register a new account.

        Args:
            username (str): The username to register.
            email (str): The email address to register.
            password (str): The password to register.
            quiet (bool, optional): If True, suppress exceptions and return the response on failure. Defaults to False.

        Returns:
            dict: The response from the server.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        server_index = (
            self.server_header.split("EmpireEx_")[1]
            if "EmpireEx_" in self.server_header
            else "1"
        )
        request = requests.get(
            f"https://lp2.goodgamestudios.com/register/index.json?gameId=12&networkId=1&COUNTRY=FR&forceGeoip=false&forceInstance=true&PN={username}&LANG=fr-FR&MAIL={email}&PW={password}&AID=0&adgr=0&adID=0&camp=0&cid=&journeyHash=1720629282364650193&keyword=&matchtype=&network=&nid=0&placement=&REF=&tid=&timeZone=14&V=&campainPId=0&campainCr=0&campainLP=0&DID=0&websiteId=380635&gci=0&adClickId=&instance={server_index}"
        )
        request.raise_for_status()
        response = request.json()
        if not response["res"] or response["err"]:
            if not quiet:
                raise Exception(f"Failed to register: {response['err']}")
            else:
                return response
        return response

    def login_with_recaptcha_token(
        self, name: str, password: str, recaptcha_token: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Log in to an account with a reCAPTCHA token.

        Args:
            name (str): The username to log in with.
            password (str): The password to log in with.
            recaptcha_token (str): The reCAPTCHA token to verify the login.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command(
                "lli",
                {
                    "CONM": 175,
                    "RTM": 24,
                    "ID": 0,
                    "PL": 1,
                    "NOM": name,
                    "PW": password,
                    "LT": None,
                    "LANG": "fr",
                    "DID": "0",
                    "AID": "1674256959939529708",
                    "KID": "",
                    "REF": "https://empire.goodgamestudios.com",
                    "GCI": "",
                    "SID": 9,
                    "PLFID": 1,
                    "RCT": recaptcha_token,
                },
            )
            if sync:
                response = self.wait_for_json_response("lli")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def login_without_recaptcha_token(
        self, name: str, password: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Log in to an account without a reCAPTCHA token.

        Args:
            name (str): The username to log in with.
            password (str): The password to log in with.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command(
                "lli",
                {
                    "CONM": 175,
                    "RTM": 24,
                    "ID": 0,
                    "PL": 1,
                    "NOM": name,
                    "PW": password,
                    "LT": None,
                    "LANG": "fr",
                    "DID": "0",
                    "AID": "1674256959939529708",
                    "KID": "",
                    "REF": "https://empire.goodgamestudios.com",
                    "GCI": "",
                    "SID": 9,
                    "PLFID": 1,
                },
            )
            if sync:
                response = self.wait_for_json_response("lli")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def login_facebook(
        self,
        facebook_id: str,
        facebook_token: str,
        facebook_account_id: str,
        sync: bool = True,
        quiet: bool = False,
    ) -> dict | bool:
        """
        Log in to an account using Facebook.

        Args:
            facebook_id: The Facebook ID to log in with.
            facebook_token: The Facebook token to log in with.
            facebook_account_id: The Facebook account ID to log in with.
            sync: If True, wait for a response and return it. Defaults to True.
            quiet: If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command(
                "lli",
                {
                    "CONM": 175,
                    "RTM": 24,
                    "ID": 0,
                    "PL": 1,
                    "NOM": "null",
                    "PW": "null",
                    "LT": None,
                    "LANG": "fr",
                    "DID": "0",
                    "AID": "1674256959939529708",
                    "KID": "",
                    "REF": "https://empire.goodgamestudios.com",
                    "GCI": "",
                    "SID": 9,
                    "PLFID": 1,
                    "FID": facebook_id,
                    "FTK": facebook_token,
                    "FAID": facebook_account_id,
                },
            )
            if sync:
                response = self.wait_for_json_response("lli")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def ask_password_recovery(self, email, sync=True, quiet=False):
        """
        Ask for password recovery.

        Args:
            email (str): The email address to recover the password for.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command("lpp", {"MAIL": email})
            if sync:
                response = self.wait_for_json_response("lpp")
                self.raise_for_status(response)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False

    def login_e4k(
        self, name: str, password: str, sync: bool = True, quiet: bool = False
    ) -> dict | bool:
        """
        Log in to an account using the Empire 4 Kingdoms API.

        Args:
            email (str): The email address to log in with.
            password (str): The password to log in with.
            sync (bool, optional): If True, wait for a response and return it. Defaults to True.
            quiet (bool, optional): If True, suppress exceptions and return False on failure. Defaults to False.

        Returns:
            dict: The response from the server if `sync` is True.
            bool: True if the operation was successful and `sync` is False. False if the operation failed and `quiet` is True.

        Raises:
            Exception: If an error occurs during the operation and `quiet` is False.
        """
        try:
            self.send_json_command(
                "core_lga",
                {
                    "NM": name,
                    "PW": password,
                    "L": "fr",
                    "AID": "1674256959939529708",
                    "DID": 5,
                    "PLFID": "3",
                    "ADID": "null",
                    "AFUID": "appsFlyerUID",
                    "IDFV": "null",
                },
            )
            if sync:
                response = self.wait_for_json_response("core_lga")
                self.raise_for_status(response, expected_status=10005)
                return response
            return True
        except Exception as e:
            if not quiet:
                raise e
            return False
