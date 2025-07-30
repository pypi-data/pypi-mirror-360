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
        :param askToAI:
            - False (default): GenderAPI first tries its internal database.
              Only if uncertain, it queries AI without spending 3 credits.
            - True: Directly queries AI for higher accuracy but consumes 3 credits per request.
        :param forceToGenderize:
            - False (default): GenderAPI only analyzes real names.
              If the input seems like a nickname, it returns "null".
            - True: Even nicknames, emojis, or unconventional strings
              like "spider man" or "🌸 butterfly dream" are analyzed for gender.
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
        :param askToAI:
            - False (default): GenderAPI first tries its internal database.
              Only if uncertain, it queries AI without spending 3 credits.
            - True: Directly queries AI for higher accuracy but consumes 3 credits per request.
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
        :param askToAI:
            - False (default): GenderAPI first tries its internal database.
              Only if uncertain, it queries AI without spending 3 credits.
            - True: Directly queries AI for higher accuracy but consumes 3 credits per request.
        :param forceToGenderize:
            - False (default): GenderAPI only analyzes real names.
              If the input seems like a nickname, it returns "null".
            - True: Even nicknames, emojis, or unconventional strings
              like "spider man" or "🌸 butterfly dream" are analyzed for gender.
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



