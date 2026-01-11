import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

TOKEN_URL = "https://www.strava.com/oauth/token"
BASE_URL = "https://www.strava.com/api/v3"


class StravaClient:
    def __init__(self):
        self.access_token = None
        self.expires_at = 0

    def _refresh_token(self):
        """Refresh the Strava access token using the refresh token."""
        print("🔄 Refreshing Strava access token...")

        payload = {
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": STRAVA_REFRESH_TOKEN,
        }

        response = requests.post(TOKEN_URL, data=payload)
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]
        self.expires_at = data["expires_at"]

        print("✅ Token refreshed successfully.")

    def _ensure_token(self):
        """Ensure the access token is valid, refresh if expired."""
        if not self.access_token or time.time() >= self.expires_at:
            self._refresh_token()

    def _get(self, endpoint, params=None):
        """Perform an authenticated GET request to Strava."""
        self._ensure_token()

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{BASE_URL}{endpoint}"

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_activities(self, after_timestamp=None, per_page=50):
        """Fetch athlete activities, optionally after a given timestamp."""
        params = {
            "per_page": per_page,
        }

        if after_timestamp:
            params["after"] = after_timestamp

        return self._get("/athlete/activities", params=params)
