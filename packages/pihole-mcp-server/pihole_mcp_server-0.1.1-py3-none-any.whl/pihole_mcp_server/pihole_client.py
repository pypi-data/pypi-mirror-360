"""Pi-hole API client for interacting with Pi-hole server."""

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import requests
import urllib3
from pydantic import BaseModel, Field, validator


class PiHoleConfig(BaseModel):
    """Configuration for Pi-hole connection."""

    host: str = Field(..., description="Pi-hole server hostname or IP")
    port: int = Field(default=80, description="Pi-hole server port")
    api_key: str | None = Field(None, description="Pi-hole API key (for legacy API)")
    web_password: str | None = Field(
        None, description="Pi-hole web password (for modern API)"
    )
    use_https: bool = Field(default=False, description="Use HTTPS for connection")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    api_version: str | None = Field(None, description="API version (legacy or modern)")

    @validator("host")
    def validate_host(cls, v: str) -> str:
        """Validate host format."""
        if not v.strip():
            raise ValueError("Host cannot be empty")
        return v.strip()

    @validator("port")
    def validate_port(cls, v: int) -> int:
        """Validate port range."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @property
    def base_url(self) -> str:
        """Get the base URL for Pi-hole server."""
        scheme = "https" if self.use_https else "http"
        return f"{scheme}://{self.host}:{self.port}"

    def get_api_url(self, api_version: str = "legacy") -> str:
        """Get the API URL for the specified version."""
        if api_version == "modern":
            return f"{self.base_url}/api"
        else:
            return f"{self.base_url}/admin/api.php"


class PiHoleStatus(BaseModel):
    """Pi-hole status response."""

    status: str = Field(..., description="Pi-hole status (enabled/disabled)")
    version: str | None = Field(None, description="Pi-hole version")
    gravity_last_updated: dict[str, Any] | None = Field(
        None, description="Last gravity update"
    )
    queries_today: int | None = Field(None, description="Queries today")
    ads_blocked_today: int | None = Field(None, description="Ads blocked today")
    ads_percentage_today: float | None = Field(
        None, description="Percentage of ads blocked today"
    )
    unique_domains: int | None = Field(None, description="Unique domains")
    queries_forwarded: int | None = Field(None, description="Queries forwarded")
    queries_cached: int | None = Field(None, description="Queries cached")
    clients_ever_seen: int | None = Field(None, description="Clients ever seen")
    unique_clients: int | None = Field(None, description="Unique clients")
    dns_queries_all_types: int | None = Field(None, description="DNS queries all types")
    reply_nodata: int | None = Field(None, description="Reply NODATA")
    reply_nxdomain: int | None = Field(None, description="Reply NXDOMAIN")
    reply_cname: int | None = Field(None, description="Reply CNAME")
    reply_ip: int | None = Field(None, description="Reply IP")
    privacy_level: int | None = Field(None, description="Privacy level")


class PiHoleError(Exception):
    """Base exception for Pi-hole client errors."""

    pass


class PiHoleConnectionError(PiHoleError):
    """Exception for Pi-hole connection errors."""

    pass


class PiHoleAPIError(PiHoleError):
    """Exception for Pi-hole API errors."""

    pass


class PiHoleAuthenticationError(PiHoleError):
    """Exception for Pi-hole authentication errors."""

    pass


class PiHoleClient:
    """Client for interacting with Pi-hole API."""

    def __init__(self, config: PiHoleConfig) -> None:
        """Initialize Pi-hole client.

        Args:
            config: Pi-hole configuration
        """
        self.config = config
        self.session = requests.Session()
        self._api_version: str | None = config.api_version
        self._session_valid: bool = False
        self._csrf_token: str | None = None
        self._session_cache_file = self._get_session_cache_file()

        # Try to load cached session first
        self._load_cached_session()

        # Set up SSL verification
        if not config.verify_ssl:
            self.session.verify = False
            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get_session_cache_file(self) -> Path:
        """Get path to session cache file."""
        cache_dir = Path(tempfile.gettempdir()) / "pihole-mcp-server"
        cache_dir.mkdir(exist_ok=True)

        # Use host and port to create unique cache file per Pi-hole instance
        cache_filename = f"session_{self.config.host}_{self.config.port}.json"
        return cache_dir / cache_filename

    def _save_session_cache(self) -> None:
        """Save current session to cache file."""
        if not self._session_valid or not self._csrf_token:
            return

        cache_data = {
            "csrf_token": self._csrf_token,
            "session_valid": self._session_valid,
            "timestamp": time.time(),
            "cookies": dict(self.session.cookies),
        }

        try:
            with open(self._session_cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception:
            # Ignore cache save errors
            pass

    def _load_cached_session(self) -> None:
        """Load cached session if available and valid."""
        if not self._session_cache_file.exists():
            return

        try:
            with open(self._session_cache_file) as f:
                cache_data = json.load(f)

            # Check if session is still valid (30 minutes max age)
            session_age = time.time() - cache_data.get("timestamp", 0)
            if session_age > 1800:  # 30 minutes
                self._clear_session_cache()
                return

            # Restore session state
            self._csrf_token = cache_data.get("csrf_token")
            self._session_valid = cache_data.get("session_valid", False)

            # Restore cookies
            cookies = cache_data.get("cookies", {})
            for name, value in cookies.items():
                self.session.cookies.set(name, value)

        except Exception:
            # Ignore cache load errors, will authenticate fresh
            self._clear_session_cache()

    def _clear_session_cache(self) -> None:
        """Clear session cache file."""
        try:
            if self._session_cache_file.exists():
                os.remove(self._session_cache_file)
        except Exception:
            pass

    def _detect_api_version(self) -> str:
        """Detect which API version the Pi-hole supports.

        Returns:
            'modern' for new API structure, 'legacy' for old API structure
        """
        if self._api_version:
            return self._api_version

        # Try modern API first
        try:
            modern_url = self.config.get_api_url("modern") + "/stats/summary"
            response = self.session.get(modern_url, timeout=self.config.timeout)
            if response.status_code in [
                200,
                401,
            ]:  # 200 = success, 401 = unauthorized but API exists
                self._api_version = "modern"
                return "modern"
        except requests.exceptions.RequestException:
            # Network/connection errors, try legacy
            pass
        except Exception:
            # Any other error, try legacy
            pass

        # Try legacy API
        try:
            legacy_url = self.config.get_api_url("legacy")
            response = self.session.get(
                legacy_url, params={"summary": ""}, timeout=self.config.timeout
            )
            if response.status_code == 200:
                self._api_version = "legacy"
                return "legacy"
        except requests.exceptions.RequestException:
            # Network/connection errors
            pass
        except Exception:
            # Any other error
            pass

        # Default to modern if both fail (since you confirmed it's modern)
        self._api_version = "modern"
        return "modern"

    def _authenticate_modern(self) -> bool:
        """Authenticate with modern Pi-hole API.

        Returns:
            True if authentication successful
        """
        if not self.config.web_password:
            return False

        auth_url = f"{self.config.get_api_url('modern')}/auth"
        auth_data = {"password": self.config.web_password}

        try:
            response = self.session.post(
                auth_url, json=auth_data, timeout=self.config.timeout
            )

            # Don't raise for HTTP errors, check response manually
            if response.status_code != 200:
                self._session_valid = False
                self._csrf_token = None
                self._clear_session_cache()
                return False

            data = response.json()
            session_info = data.get("session", {})
            self._session_valid = session_info.get("valid", False)

            # Store CSRF token for authenticated requests
            if self._session_valid:
                self._csrf_token = session_info.get("csrf")
                # Save successful session to cache
                self._save_session_cache()
            else:
                self._csrf_token = None
                self._clear_session_cache()

            return self._session_valid
        except requests.exceptions.RequestException as e:
            # Log the actual error for debugging
            logging.error(f"Request exception in authentication: {e}")
            self._session_valid = False
            self._csrf_token = None
            self._clear_session_cache()
            return False
        except json.JSONDecodeError as e:
            # Log the actual error for debugging
            logging.error(f"JSON decode error in authentication: {e}")
            self._session_valid = False
            self._csrf_token = None
            self._clear_session_cache()
            return False
        except Exception as e:
            # Log the actual error for debugging
            logging.error(f"Unexpected error in authentication: {e}")
            self._session_valid = False
            self._csrf_token = None
            self._clear_session_cache()
            return False

    def _ensure_authentication(self, api_version: str) -> bool:
        """Ensure proper authentication for the API version.

        Args:
            api_version: API version to authenticate for

        Returns:
            True if authentication is ready
        """
        if api_version == "modern":
            if not self._session_valid:
                return self._authenticate_modern()
            return True
        else:
            # Legacy API uses API key directly in requests
            return bool(self.config.api_key)

    def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        require_auth: bool = False,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Make a request to the Pi-hole API.

        Args:
            endpoint: API endpoint (e.g., 'summary', 'enable', 'disable')
            params: Additional parameters
            require_auth: Whether authentication is required
            method: HTTP method

        Returns:
            API response data

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAuthenticationError: If authentication fails
            PiHoleAPIError: If API returns an error
        """
        api_version = self._detect_api_version()

        if require_auth:
            if api_version == "modern" and not self.config.web_password:
                raise PiHoleAuthenticationError(
                    "Web password is required for modern API"
                )
            elif api_version == "legacy" and not self.config.api_key:
                raise PiHoleAuthenticationError("API key is required for legacy API")

            if not self._ensure_authentication(api_version):
                raise PiHoleAuthenticationError("Authentication failed")

        if params is None:
            params = {}

        # Prepare request based on API version
        if api_version == "modern":
            # Modern API uses different structure
            if endpoint == "summary":
                url = f"{self.config.get_api_url('modern')}/stats/summary"
            elif endpoint == "enable":
                url = f"{self.config.get_api_url('modern')}/dns/blocking"
                method = "POST"  # Use POST method (confirmed working)
                params = {"blocking": True}
            elif endpoint == "disable":
                url = f"{self.config.get_api_url('modern')}/dns/blocking"
                method = "POST"  # Use POST method (confirmed working)
                duration = params.get("duration")
                params = {"blocking": False}
                if duration:
                    params["timer"] = duration
            elif endpoint == "version":
                url = f"{self.config.get_api_url('modern')}/version"
            else:
                url = f"{self.config.get_api_url('modern')}/{endpoint}"

            # Modern API uses sessions and CSRF token
            headers = {}
            if require_auth and self._csrf_token:
                headers["X-CSRF-Token"] = self._csrf_token
        else:
            # Legacy API structure
            url = self.config.get_api_url("legacy")
            headers = {}

            # Legacy API uses query params for everything
            if endpoint == "summary":
                params["summary"] = ""
            elif endpoint == "enable":
                params["enable"] = ""
            elif endpoint == "disable":
                duration = params.get("duration")
                if duration:
                    params["disable"] = str(duration)
                else:
                    params["disable"] = ""
            elif endpoint == "version":
                params["version"] = ""

            # Legacy API uses auth param
            if self.config.api_key:
                params["auth"] = self.config.api_key

        try:
            if method == "GET":
                response = self.session.get(
                    url, params=params, headers=headers, timeout=self.config.timeout
                )
            elif method in ["PATCH", "PUT", "POST"]:
                response = self.session.request(
                    method,
                    url,
                    json=params,
                    headers=headers,
                    timeout=self.config.timeout,
                )
            else:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout,
                )

            response.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise PiHoleConnectionError(f"Failed to connect to Pi-hole: {e}")
        except requests.exceptions.Timeout as e:
            raise PiHoleConnectionError(f"Request timeout: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Session might have expired for modern API
                if api_version == "modern":
                    self._session_valid = False
                    self._csrf_token = None
                    self._clear_session_cache()
                raise PiHoleAuthenticationError(
                    "Authentication failed - check credentials"
                )
            raise PiHoleAPIError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            raise PiHoleConnectionError(f"Request failed: {e}")

        try:
            data = response.json()
        except json.JSONDecodeError:
            raise PiHoleAPIError("Invalid JSON response from Pi-hole")

        # Check for API errors
        if isinstance(data, dict):
            if "error" in data:
                error_info = data["error"]
                if isinstance(error_info, dict):
                    if error_info.get("key") == "unauthorized":
                        if api_version == "modern":
                            self._session_valid = False
                            self._csrf_token = None
                            self._clear_session_cache()
                        raise PiHoleAuthenticationError(
                            "Authentication failed - check credentials"
                        )
                    elif error_info.get("key") == "api_seats_exceeded":
                        # Try to reuse existing session or wait before retrying
                        if api_version == "modern":
                            self._session_valid = False
                            self._csrf_token = None
                            self._clear_session_cache()
                        raise PiHoleAuthenticationError(
                            "API session limit exceeded - try again in a few minutes"
                        )
                    else:
                        raise PiHoleAPIError(
                            f"API error: {error_info.get('message', 'Unknown error')}"
                        )

        # Check for legacy auth errors
        if isinstance(data, list) and len(data) == 1 and data[0] == "[]":
            raise PiHoleAuthenticationError("Authentication failed - check API key")

        return data  # type: ignore[no-any-return]

    def get_status(self) -> PiHoleStatus:
        """Get Pi-hole status.

        Returns:
            Pi-hole status

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAPIError: If API returns an error
        """
        # Modern Pi-hole requires authentication for stats
        api_version = self._detect_api_version()
        require_auth = api_version == "modern"

        data = self._make_request("summary", require_auth=require_auth)

        # Handle modern API response format
        if api_version == "modern":
            # Modern API has different structure and doesn't include status
            if "data" in data:
                stats_data = data["data"]
            else:
                stats_data = data

            # Get real-time blocking status from DNS endpoint
            try:
                blocking_data = self._make_request("dns/blocking", require_auth=True)
                blocking_status = blocking_data.get("blocking", "enabled")
                status_str = "enabled" if blocking_status == "enabled" else "disabled"
            except Exception:
                # Fallback: determine from query statistics if blocking endpoint fails
                if "queries" in stats_data:
                    queries_data = stats_data["queries"]
                    percent_blocked = queries_data.get("percent_blocked", 0)
                    status_str = "enabled" if percent_blocked > 0 else "disabled"
                else:
                    status_str = "enabled"

            # Transform modern API response to match PiHoleStatus model
            if "queries" in stats_data:
                queries_data = stats_data["queries"]
                return PiHoleStatus(
                    status=status_str,
                    queries_today=queries_data.get("total"),
                    ads_blocked_today=queries_data.get("blocked"),
                    ads_percentage_today=queries_data.get("percent_blocked"),
                    unique_domains=queries_data.get("unique_domains"),
                    # Map other fields as available
                )
            else:
                # Fallback for unexpected format
                return PiHoleStatus(
                    status=status_str,
                    **{
                        k: v
                        for k, v in stats_data.items()
                        if k in PiHoleStatus.model_fields
                    },
                )
        else:
            # Legacy API format
            return PiHoleStatus(**data)

    def is_enabled(self) -> bool:
        """Check if Pi-hole is enabled.

        Returns:
            True if Pi-hole is enabled

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAPIError: If API returns an error
        """
        status = self.get_status()
        return status.status == "enabled"

    def enable(self) -> bool:
        """Enable Pi-hole.

        Returns:
            True if successfully enabled

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAuthenticationError: If authentication fails
            PiHoleAPIError: If API returns an error
        """
        data = self._make_request("enable", require_auth=True)

        # Handle different API response formats
        api_version = self._detect_api_version()
        if api_version == "modern":
            # Modern API returns {"blocking": "enabled/disabled", ...}
            blocking_status = data.get("blocking")
            return blocking_status == "enabled"
        else:
            return data.get("status") == "enabled"

    def disable(self, duration: int | None = None) -> bool:
        """Disable Pi-hole.

        Args:
            duration: Duration in seconds to disable (None for permanent)

        Returns:
            True if successfully disabled

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAuthenticationError: If authentication fails
            PiHoleAPIError: If API returns an error
        """
        params = {}
        if duration is not None:
            params["duration"] = duration

        data = self._make_request("disable", params=params, require_auth=True)

        # Handle different API response formats
        api_version = self._detect_api_version()
        if api_version == "modern":
            # Modern API returns {"blocking": "enabled/disabled", ...}
            blocking_status = data.get("blocking")
            return blocking_status == "disabled"
        else:
            return data.get("status") == "disabled"

    def disable_for_minutes(self, minutes: int) -> bool:
        """Disable Pi-hole for specified minutes.

        Args:
            minutes: Number of minutes to disable

        Returns:
            True if successfully disabled

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAuthenticationError: If authentication fails
            PiHoleAPIError: If API returns an error
        """
        if minutes <= 0:
            raise ValueError("Minutes must be positive")

        seconds = minutes * 60
        return self.disable(seconds)

    def get_version(self) -> dict[str, str]:
        """Get Pi-hole version information.

        Returns:
            Version information

        Raises:
            PiHoleConnectionError: If connection fails
            PiHoleAPIError: If API returns an error
        """
        data = self._make_request("version")

        # Handle modern API response format
        api_version = self._detect_api_version()
        if api_version == "modern" and "data" in data:
            return data["data"]

        return data

    def test_connection(self) -> bool:
        """Test connection to Pi-hole.

        Returns:
            True if connection successful
        """
        try:
            # Test basic connectivity without authentication
            api_version = self._detect_api_version()
            if api_version == "modern":
                # Modern API - test with a simple endpoint
                url = f"{self.config.get_api_url('modern')}/stats/summary"
                response = self.session.get(url, timeout=self.config.timeout)
                # 200 = success, 401 = unauthorized but server is reachable
                return response.status_code in [200, 401]
            else:
                # Legacy API - test with summary endpoint
                url = self.config.get_api_url("legacy")
                response = self.session.get(
                    url, params={"summary": ""}, timeout=self.config.timeout
                )
                # 200 = success, any valid response means server is reachable
                return response.status_code == 200
        except Exception:
            return False

    def test_authentication(self) -> bool:
        """Test authentication with Pi-hole.

        Returns:
            True if authentication successful
        """
        api_version = self._detect_api_version()

        # Check if we have the right credentials for the API version
        if api_version == "modern":
            if not self.config.web_password:
                return False
        else:
            if not self.config.api_key:
                return False

        try:
            # For modern API, just test the authentication step
            if api_version == "modern":
                # Test authentication by trying to login
                return self._authenticate_modern()
            else:
                # For legacy API, try an authenticated endpoint
                self._make_request("overTimeDataForTotalQueries", require_auth=True)
                return True
        except Exception:
            # Any error indicates auth failure
            return False

    def logout(self) -> None:
        """Logout and clear session cache.

        This method clears the local session cache and invalidates
        the current session to free up API seats.
        """
        self._session_valid = False
        self._csrf_token = None
        self._clear_session_cache()

        # Clear session cookies
        self.session.cookies.clear()
