import requests

class GenderAPI:
    """
    Python SDK for GenderAPI.io

    This SDK allows determining gender from:
      - personal names
      - email addresses
      - social media usernames

    It supports additional options like country filtering,
    direct AI queries, and forced genderization for nicknames.
    """

    def __init__(self, api_key, base_url="https://api.genderapi.io"):
        """
        Initialize the GenderAPI SDK.

        :param api_key: Your API key as a Bearer token.
        :param base_url: API base URL. Default: https://api.genderapi.io
        """
        self.api_key = api_key
        self.base_url = base_url

    def get_gender_by_name(self, name, country=None, askToAI=False, forceToGenderize=False):
        """
        Determine gender from a personal name.

        :param name: The name to analyze. (Required)
        :param country: Optional two-letter country code (e.g. "US") to improve accuracy.
        :param askToAI: See class docstring for details.
        :param forceToGenderize: See class docstring for details.
        :return: JSON response as a Python dictionary.
        """
        return self._post_request(
            "/api",
            {
                "name": name,
                "country": country,
                "askToAI": askToAI,
                "forceToGenderize": forceToGenderize
            }
        )

    def get_gender_by_email(self, email, country=None, askToAI=False):
        """
        Determine gender from an email address.

        :param email: The email address to analyze. (Required)
        :param country: Optional two-letter country code (e.g. "US") to improve accuracy.
        :param askToAI: See class docstring for details.
        :return: JSON response as a Python dictionary.
        """
        return self._post_request(
            "/api/email",
            {
                "email": email,
                "country": country,
                "askToAI": askToAI
            }
        )

    def get_gender_by_username(self, username, country=None, askToAI=False, forceToGenderize=False):
        """
        Determine gender from a social media username.

        :param username: The username to analyze. (Required)
        :param country: Optional two-letter country code (e.g. "US") to improve accuracy.
        :param askToAI: See class docstring for details.
        :param forceToGenderize: See class docstring for details.
        :return: JSON response as a Python dictionary.
        """
        return self._post_request(
            "/api/username",
            {
                "username": username,
                "country": country,
                "askToAI": askToAI,
                "forceToGenderize": forceToGenderize
            }
        )

    def get_gender_by_name_bulk(self, data):
        """
        Determine gender for multiple names (bulk).

        :param data: List of dicts, each containing:
            - name (str): The name to analyze (required)
            - country (str, optional)
            - id (str or int, optional): Your own ID to match results
        :return: JSON response as Python dictionary.
        :raises ValueError: if data exceeds limit.
        """
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("get_gender_by_name_bulk requires a non-empty list of data objects.")

        if len(data) > 100:
            raise ValueError("get_gender_by_name_bulk cannot exceed 100 records per request.")

        return self._post_request(
            "/api/name/multi/country",
            {
                "data": data
            }
        )

    def get_gender_by_email_bulk(self, data):
        """
        Determine gender for multiple email addresses (bulk).

        :param data: List of dicts, each containing:
            - email (str): The email to analyze (required)
            - country (str, optional)
            - id (str or int, optional): Your own ID to match results
        :return: JSON response as Python dictionary.
        :raises ValueError: if data exceeds limit.
        """
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("get_gender_by_email_bulk requires a non-empty list of data objects.")

        if len(data) > 50:
            raise ValueError("get_gender_by_email_bulk cannot exceed 50 records per request.")

        return self._post_request(
            "/api/email/multi",
            {
                "data": data
            }
        )

    def get_gender_by_username_bulk(self, data):
        """
        Determine gender for multiple usernames (bulk).

        :param data: List of dicts, each containing:
            - username (str): The username to analyze (required)
            - country (str, optional)
            - id (str or int, optional): Your own ID to match results
        :return: JSON response as Python dictionary.
        :raises ValueError: if data exceeds limit.
        """
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("get_gender_by_username_bulk requires a non-empty list of data objects.")

        if len(data) > 50:
            raise ValueError("get_gender_by_username_bulk cannot exceed 50 records per request.")

        return self._post_request(
            "/api/username/multi",
            {
                "data": data
            }
        )

    def _post_request(self, endpoint, payload):
        """
        Internal helper method to send POST requests.

        Handles:
          - Authentication via Bearer token
          - Error handling:
              - HTTP 500: Raises an HTTPError exception.
              - Other non-200 errors: Raises HTTPError and includes the error JSON for easier debugging.
          - Parses JSON response and returns a Python dictionary.

        :param endpoint: API endpoint path (e.g. "/api")
        :param payload: Dictionary of payload parameters.
        :return: JSON response as a Python dictionary.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [500, 502, 503, 504, 408]:
            # Raise HTTPError for server-side issues and timeouts
            response.raise_for_status()
        else:
            try:
                return response.json()
            except ValueError:
                raise ValueError("Response content is not valid JSON.")
