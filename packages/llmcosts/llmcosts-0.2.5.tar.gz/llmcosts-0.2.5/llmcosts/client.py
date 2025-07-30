"""HTTP client for the llmcosts.com API."""

from __future__ import annotations

import configparser
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import jwt
import requests
from environs import Env


class LLMCostsClient:
    """Simple wrapper around the llmcosts.com REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        framework: Optional[str] = None,
    ) -> None:
        env = Env()
        api_key = api_key or env.str("LLMCOSTS_API_KEY", None)
        if not api_key:
            raise ValueError("LLMCOSTS_API_KEY is required")
        base_url = base_url or env.str(
            "LLMCOSTS_BASE_URL", "https://llmcosts.com/api/v1"
        )
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.framework = framework
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

        # Initialize triggered thresholds
        self._initialize_triggered_thresholds()

    def _initialize_triggered_thresholds(self) -> None:
        """Initialize by checking for any active triggered thresholds."""
        try:
            response = self.get("/health", timeout=10)

            if response and "triggered_thresholds" in response:
                self._store_triggered_thresholds(response["triggered_thresholds"])
                logging.info("⚠️ SDK initialized with active triggered thresholds")
            else:
                # Clear any stale triggered thresholds
                self._clear_triggered_thresholds()
                logging.info("✅ SDK initialized - no active triggered thresholds")

        except Exception as e:
            logging.warning(f"❌ SDK initialization error: {e}")

    @property
    def _config_file_path(self) -> Path:
        """Get the path for the triggered thresholds config file."""
        env = Env()
        config_path = env.str("LLMCOSTS_INI_PATH", None)

        if config_path:
            return Path(config_path)
        else:
            # Default to ~/.llmcosts_settings.json (but we'll use .ini format)
            return Path.home() / ".llmcosts_settings.ini"

    def _store_triggered_thresholds(self, triggered_thresholds: Dict[str, Any]) -> None:
        """Store triggered thresholds in local config file."""
        config_file = self._config_file_path

        # Ensure parent directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Create and configure parser
        config = configparser.ConfigParser()
        config.clear()
        config.add_section("triggered_thresholds")

        config["triggered_thresholds"]["version"] = triggered_thresholds["version"]
        config["triggered_thresholds"]["public_key"] = triggered_thresholds[
            "public_key"
        ]
        config["triggered_thresholds"]["key_id"] = triggered_thresholds["key_id"]
        config["triggered_thresholds"]["encrypted_payload"] = triggered_thresholds[
            "encrypted_payload"
        ]
        config["triggered_thresholds"]["last_updated"] = str(
            int(datetime.now().timestamp())
        )

        # Write to file
        with open(config_file, "w") as f:
            config.write(f)

        # Set restrictive permissions
        os.chmod(config_file, 0o600)

    def _clear_triggered_thresholds(self) -> None:
        """Clear triggered thresholds cache when none are active."""
        config_file = self._config_file_path
        if config_file.exists():
            config_file.unlink()

    def _load_triggered_thresholds(self) -> Optional[Dict[str, str]]:
        """Load triggered thresholds from local cache."""
        try:
            config_file = self._config_file_path
            if not config_file.exists():
                return None

            config = configparser.ConfigParser()
            config.read(config_file)

            if "triggered_thresholds" not in config:
                return None

            return {
                "version": config["triggered_thresholds"]["version"],
                "public_key": config["triggered_thresholds"]["public_key"],
                "key_id": config["triggered_thresholds"]["key_id"],
                "encrypted_payload": config["triggered_thresholds"][
                    "encrypted_payload"
                ],
                "last_updated": config["triggered_thresholds"]["last_updated"],
            }
        except Exception as e:
            logging.warning(f"⚠️ Error loading triggered thresholds: {e}")
            return None

    def _verify_triggered_threshold_jwt(
        self, token: str, public_key: str
    ) -> Optional[Dict]:
        """Verify and decode triggered threshold JWT."""
        try:
            payload = jwt.decode(
                token, public_key, algorithms=["RS256"], issuer="llmcosts-api"
            )
            return payload
        except jwt.ExpiredSignatureError:
            logging.warning("⚠️ Triggered threshold JWT has expired")
            return None
        except jwt.InvalidTokenError as e:
            logging.warning(f"⚠️ Invalid triggered threshold JWT: {e}")
            return None

    def check_triggered_thresholds(
        self, provider: str = None, model_id: str = None, client_key: str = None
    ) -> Dict[str, Any]:
        """Check if current request violates any active triggered thresholds."""
        config = self._load_triggered_thresholds()
        if not config:
            # If no config exists, make a health call to check for triggered thresholds
            # This prevents threshold avoidance by bypassing the config cache
            try:
                response = self.get("/health", timeout=10)
                if (
                    response
                    and "triggered_thresholds" in response
                    and response["triggered_thresholds"]
                ):
                    self._store_triggered_thresholds(response["triggered_thresholds"])
                    # Reload config after storing
                    config = self._load_triggered_thresholds()
                else:
                    return {
                        "status": "no_triggered_thresholds",
                        "allowed": True,
                        "violations": [],
                    }
            except Exception as e:
                logging.warning(f"⚠️ Failed to fetch triggered thresholds: {e}")
                return {
                    "status": "no_triggered_thresholds",
                    "allowed": True,
                    "violations": [],
                }

        if not config:
            return {
                "status": "no_triggered_thresholds",
                "allowed": True,
                "violations": [],
            }

        # Verify and decode JWT
        payload = self._verify_triggered_threshold_jwt(
            config["encrypted_payload"], config["public_key"]
        )

        if not payload:
            return {"status": "invalid_jwt", "allowed": True, "violations": []}

        # Log threshold check for debugging (as requested)
        logging.info("🔍 Checking triggered thresholds for pre-call validation")

        # Check each triggered threshold
        violations = []
        warnings = []
        current_time = datetime.now(timezone.utc)

        for triggered_threshold in payload.get("triggered_thresholds", []):
            # Check if this triggered threshold applies to current request
            if self._threshold_applies(
                triggered_threshold, provider, model_id, client_key
            ):
                # Check if threshold has expired
                expires_at_str = triggered_threshold.get("expires_at")
                if expires_at_str:
                    expires_at = datetime.fromisoformat(
                        expires_at_str.replace("Z", "+00:00")
                    )

                    if current_time < expires_at:
                        threshold_info = {
                            "event_id": triggered_threshold["event_id"],
                            "threshold_type": triggered_threshold["threshold_type"],
                            "amount": triggered_threshold["amount"],
                            "period": triggered_threshold["period"],
                            "expires_at": expires_at_str,
                            "triggered_at": triggered_threshold["triggered_at"],
                            "provider": triggered_threshold.get("provider"),
                            "model_id": triggered_threshold.get("model_id"),
                            "client_customer_key": triggered_threshold.get(
                                "client_customer_key"
                            ),
                        }

                        if triggered_threshold["threshold_type"] == "limit":
                            violations.append(
                                {
                                    **threshold_info,
                                    "message": f"Usage blocked: {triggered_threshold['threshold_type']} threshold of ${triggered_threshold['amount']} exceeded",
                                }
                            )
                        elif triggered_threshold["threshold_type"] == "alert":
                            warnings.append(
                                {
                                    **threshold_info,
                                    "message": f"Usage warning: {triggered_threshold['threshold_type']} threshold of ${triggered_threshold['amount']} exceeded",
                                }
                            )

        return {
            "status": "checked",
            "allowed": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "version": payload.get("version"),
        }

    def _threshold_applies(
        self, triggered_threshold: Dict, provider: str, model_id: str, client_key: str
    ) -> bool:
        """Check if a triggered threshold applies to the current request."""

        # Check provider scope
        threshold_provider = triggered_threshold.get("provider")
        if (
            threshold_provider
            and threshold_provider.lower() != (provider or "").lower()
        ):
            return False

        # Check model scope
        threshold_model = triggered_threshold.get("model_id")
        if threshold_model and threshold_model.lower() != (model_id or "").lower():
            return False

        # Check client scope
        threshold_client = triggered_threshold.get("client_customer_key")
        if threshold_client and threshold_client != client_key:
            return False

        return True

    def refresh_triggered_thresholds(self) -> bool:
        """Manually refresh triggered thresholds from server."""
        try:
            response = self.get("/health", timeout=10)

            if response and "triggered_thresholds" in response:
                current_config = self._load_triggered_thresholds()
                new_version = response["triggered_thresholds"]["version"]

                # Check if version has changed
                if not current_config or current_config["version"] != new_version:
                    logging.info(f"🔄 Triggered thresholds updated: {new_version}")

                self._store_triggered_thresholds(response["triggered_thresholds"])
                return True
            else:
                # No triggered thresholds - clear cache
                self._clear_triggered_thresholds()
                return True
        except Exception as e:
            logging.error(f"❌ Failed to refresh triggered thresholds: {e}")
            return False

    @property
    def has_triggered_thresholds(self) -> bool:
        """Check if there are active triggered thresholds."""
        config = self._load_triggered_thresholds()
        return config is not None

    @property
    def triggered_thresholds_version(self) -> Optional[str]:
        """Get the version of currently stored triggered thresholds."""
        config = self._load_triggered_thresholds()
        return config["version"] if config else None

    def get_decrypted_triggered_thresholds(self) -> Optional[Dict[str, Any]]:
        """Get and decrypt the triggered thresholds payload if available."""
        config = self._load_triggered_thresholds()
        if not config:
            return None

        # Verify and decode JWT
        payload = self._verify_triggered_threshold_jwt(
            config["encrypted_payload"], config["public_key"]
        )
        return payload

    def _handle_triggered_thresholds_in_response(
        self, response: Dict[str, Any]
    ) -> None:
        """Handle triggered thresholds updates from API responses."""
        if not response or "triggered_thresholds" not in response:
            return

        triggered_thresholds = response["triggered_thresholds"]
        if not triggered_thresholds:
            # Clear cache if no triggered thresholds
            self._clear_triggered_thresholds()
            return

        # Check if version has changed
        current_config = self._load_triggered_thresholds()
        new_version = triggered_thresholds["version"]

        if not current_config or current_config["version"] != new_version:
            logging.info(
                f"🔄 Triggered thresholds updated from API response: {new_version}"
            )
            self._store_triggered_thresholds(triggered_thresholds)

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def get(self, path: str, **kwargs: Any) -> Any:
        res = self.session.get(self._url(path), **kwargs)
        res.raise_for_status()
        return self._maybe_json(res)

    def post(self, path: str, **kwargs: Any) -> Any:
        res = self.session.post(self._url(path), **kwargs)
        res.raise_for_status()
        return self._maybe_json(res)

    def put(self, path: str, **kwargs: Any) -> Any:
        res = self.session.put(self._url(path), **kwargs)
        res.raise_for_status()
        return self._maybe_json(res)

    def delete(self, path: str, **kwargs: Any) -> Any:
        res = self.session.delete(self._url(path), **kwargs)
        res.raise_for_status()
        return self._maybe_json(res)

    @staticmethod
    def _maybe_json(response: requests.Response) -> Any:
        if response.content:
            try:
                return response.json()
            except ValueError:
                return response.text
        return None
