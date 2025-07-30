"""PhotoPrism API client for interacting with PhotoPrism instance."""
from typing import Generator, Optional

import requests


class PhotoPrismClient:
    """Client for interacting with PhotoPrism API."""

    def __init__(self, base_url: str, auth_token: str):
        """Initialize the PhotoPrism client.

        Args:
            base_url: Base URL of the PhotoPrism instance (e.g., 'http://localhost:2342')
            auth_token: Authentication token for the PhotoPrism API
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.headers = {"X-Auth-Token": self.auth_token}

    def get_photos(
        self,
        order: str = "newest",
        count: int = 100,
        start_offset: int = 0,
    ) -> Generator[dict, None, None]:
        """Yield photo metadata in pages from PhotoPrism.

        Args:
            order: Sort order for photos (e.g., 'newest', 'oldest')
            count: Number of photos to fetch per page
            start_offset: Offset to start fetching from

        Yields:
            dict: Photo metadata
        """
        offset = start_offset
        while True:
            resp = requests.get(
                f"{self.base_url}/api/v1/photos/view",
                params={"order": order, "count": count, "offset": offset},
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
            photos = resp.json()
            if not photos:
                break
            for photo in photos:
                yield photo
            offset += count

    def download_photo(self, photo: dict) -> Optional[bytes]:
        try:
            response = requests.get(
                f"{self.base_url}{photo['DownloadUrl']}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to download photo {photo}: {e}")
            return None

    def update_photo_description(
        self,
        photo_uid: str,
        description: str,
        source: str = "manual"
    ) -> None:
        """Update the description of a photo in PhotoPrism.

        Args:
            photo_uid: Unique ID of the photo to update
            description: New description text
            source: Source of the description (default: "manual")
        """
        try:
            resp = requests.put(
                f"{self.base_url}/api/v1/photos/{photo_uid}",
                json={
                    "Description": description,
                    "DescriptionSrc": source
                },
                headers=self.headers,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to update photo {photo_uid}: {e}")
            raise
