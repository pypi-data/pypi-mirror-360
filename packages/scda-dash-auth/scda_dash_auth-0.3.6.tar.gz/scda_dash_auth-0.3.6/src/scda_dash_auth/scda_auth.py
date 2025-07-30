# type: ignore
import time
import json
import logging
import os
import re
from typing import Optional, Tuple, Union, List, Any
from urllib.parse import urlencode, urljoin

import dash
import dash_auth
import dash_auth.auth
import requests
from flask import Response, flash, redirect, request, session


class SCDAAuth(dash_auth.auth.Auth):
    """Implements auth via SCDA/QDT OpenID."""

    AUTH_REASON_APP_NOT_ASSOCIATED = "auth_reason_app_not_associated"
    AUTH_REASON_NO_EFFECTIVE_PERMISSIONS = "auth_reason_no_effective_permissions"
    AUTH_REASON_ROUTE_PERMISSION_MISSING = "auth_reason_route_permission_missing"
    AUTH_REASON_SERVICE_ERROR = "auth_reason_service_error"
    AUTH_REASON_USER_NOT_FOUND_IN_AUTH_SERVICE = "auth_reason_user_not_found_in_auth_service"
    AUTH_REASON_APP_ID_MISSING = "auth_reason_app_id_missing"
    AUTH_REASON_INVALID_DECLARED_PERMISSION = "auth_reason_invalid_declared_permission"
    AUTH_REASON_CALLBACK_SECURITY_CONTEXT_MISSING = "auth_reason_callback_security_context_missing"

    def __init__(
        self,
        app: dash.Dash,
        app_name: str,
        secret_key: str,
        auth_url: str,
        login_route: str = "/login",
        logout_route: str = "/logout",
        callback_route: str = "/callback",
        log_signin: bool = False,
        cache_timeout: int = 60 * 60 * 24,  # Default to 1 day
        public_routes: Optional[list] = None,
        public_callbacks: Optional[list] = None,
        logout_page: Optional[Union[str, Response]] = None,
        secure_session: bool = False,
    ):
        """
        Secure a Dash app through SCDA/QDT Auth service.

        Parameters
        ----------
        app : dash.Dash
            Dash app to secure
        app_name : str
            Name of the app registered in the SCDA/QDT Auth service
        secret_key : str
            Secret key used to sign the session for the app
        auth_url : str
            URL to the SCDA/QDT Auth service
        login_route : str, optional
            Route to login, by default "/login"
        logout_route : str, optional
            Route to logout, by default "/logout"
        callback_route : str, optional
            Route to callback for the current service. By default "/callback"
        log_signin : bool, optional
            Log sign-ins, by default False
        cache_timeout : int, optional
            Timeout for the cache in seconds, by default 60 * 60 * 24 (1 day)
        public_routes : Optional[list], optional
            List of public routes, by default None
        logout_page : Union[str, Response], optional
            Page to redirect to after logout, by default None
        secure_session : bool, optional
            Whether to ensure the session is secure, setting the flasck config
            SESSION_COOKIE_SECURE and SESSION_COOKIE_HTTPONLY to True,
            by default False
        """
        # NOTE: The public routes should be passed in the constructor of the Auth
        # but because these are static values, they are set here as defaults.
        # This is only temporal until a better solution is found. For now it
        # works.
        if public_routes is None:
            public_routes = []

        public_routes.extend(["/scda_login", "/scda_logout", "/callback"])

        super().__init__(app, public_routes = public_routes)

        self.app_name = app_name
        self.auth_url = auth_url
        self.login_route = login_route
        self.logout_route = logout_route
        self.callback_route = callback_route
        self.log_signin = log_signin
        self.cache_timeout = cache_timeout
        self.logout_page = logout_page
        self.app_id: Optional[str] = None

        if not self.__app_name_registered():
            raise RuntimeError(
                f"App name {app_name} is not registered in the auth service. "
                f"Please register it at {self.auth_url}/register/apps"
            )

        if secret_key is not None:
            if hasattr(app, "server") and app.server is not None:
                app.server.secret_key = secret_key
            else:
                raise RuntimeError(
                    "app.server is None. Ensure that the Dash app is properly initialized before setting the secret_key."
                )

        if app.server.secret_key is None:
            raise RuntimeError(
                """
                app.server.secret_key is missing.
                Generate a secret key in your Python session
                with the following commands:
                >>> import os
                >>> import base64
                >>> base64.b64encode(os.urandom(30)).decode('utf-8')
                and assign it to the property app.server.secret_key
                (where app is your dash app instance), or pass is as
                the secret_key argument to SCDAAuth.__init__.
                Note that you should not do this dynamically:
                you should create a key and then assign the value of
                that key in your code/via a secret.
                """
            )
        if secure_session:
            app.server.config["SESSION_COOKIE_SECURE"] = True
            app.server.config["SESSION_COOKIE_HTTPONLY"] = True

        app.server.add_url_rule(
            login_route,
            endpoint = "scda_login",
            view_func = self.login_request,
            methods = ["GET"],
        )
        app.server.add_url_rule(
            logout_route,
            endpoint = "scda_logout",
            view_func = self.logout,
            methods = ["GET"],
        )
        app.server.add_url_rule(
            callback_route,
            endpoint = "callback",
            view_func = self.callback,
            methods = ["GET"],
        )

        if public_callbacks:
            from dash_auth.public_routes import PUBLIC_CALLBACKS
            existing_public_callbacks = dash_auth.auth.get_public_callbacks(app)
            all_public_callbacks = list(set(existing_public_callbacks + public_callbacks))
            app.server.config[PUBLIC_CALLBACKS] = all_public_callbacks


    # #################################### #
    #             Basic Routes             #
    # #################################### #
    def logout(self):
        session.clear()
        base_url = self.app.config.get("url_base_pathname") or "/"
        page = self.logout_page or f"""
        <div style="display: flex; flex-direction: column;
        gap: 0.75rem; padding: 3rem 5rem;">
            <div>Logged out successfully</div>
            <div><a href="{base_url}">Go back</a></div>
        </div>
        """
        return page


    def callback(self):
        token = request.args.get("token")
        next_url = request.args.get("next", self.app.config["routes_pathname_prefix"])

        if not token:
            logging.error("No token received in callback.")
            return redirect(self.login_request())

        response = redirect(next_url)
        response.set_cookie(
            "access_token",
            token,
            httponly = True,
            max_age = 60 * 60 * 24 * 7,
            domain = None,
            path = "/",
        )

        return response


    def registration_request(self) -> Response:
        registration_url = urljoin(self.auth_url, "/register/user")
        query_params = urlencode({'app': self.app_name})
        full_url = f"{registration_url}?{query_params}"
        return redirect(full_url)


    def permission_request(self) -> Response:
        permissions_url = urljoin(self.auth_url, "/request-permissions")
        permission_route = session.get("missing_permission_detail", '')
        permission_action = "view" # Default action is always 'view' for now
        query_params = urlencode(
            {
                'app': self.app_name,
                'permission_route': permission_route,
                'permission_action': permission_action
            }
        )
        full_url = f"{permissions_url}?{query_params}"
        return redirect(full_url)


    def login_request(self) -> Response:
        if request.path == "/_dash-update-component":
            redirect_url = self._get_redirect_url()
            return Response(
                json.dumps(
                    {"error": "Authorization Required"}
                ),
                status = 401,
                mimetype = "application/json",
                headers = {"X-Redirect-URL": redirect_url}
            )

        # Logic for regular HTTP requests
        if session.get("needs_registration", False):
            session.pop("needs_registration")
            return self.registration_request()

        if session.get("needs_permissions", False):
            session['scda_auth_awaiting_update'] = True
            session.pop("needs_permissions")
            flash("You need to request permissions for this app. Please contact an administrator.")
            return self.permission_request()

        next_url = request.url_root
        auth_url_with_next = urljoin(self.auth_url, '/login')
        query_params = urlencode({'next': next_url})
        full_url = f"{auth_url_with_next}?{query_params}"
        return redirect(full_url)


    # #################################### #
    #         Authorization Methods        #
    # #################################### #
    def is_authorized(self) -> bool:
        """
        Check if the current user is authorized to access the app.
        """
        # NOTE: These are already checked againts in the public routes.
        # But for resources like assets and static files, we need to allow them
        # to be accessed without authorization.
        if request.path.startswith('/assets/') or request.path.startswith('/_dash-component-suites/'):
            return True

        # 1. check that the user has an access token
        access_token = self._get_access_token()
        if not access_token:
            return False

        # 2. check if the user is already authorized
        cached_auth = session.get('scda_auth_cache')
        is_cache_stale = not cached_auth or (time.time() - cached_auth.get('timestamp', 0)) > self.cache_timeout

        force_refresh = session.pop('scda_auth_awaiting_update', False)

        if is_cache_stale or force_refresh:
            if force_refresh:
                logging.info("Forcing refresh of auth data due to scda_auth_awaiting_update flag.")
            if not self._fetch_and_cache_auth_data(access_token):
                return False
            cached_auth = session.get('scda_auth_cache')

        # 3. We have a valid cache, now perform the permission check
        session["user"] = cached_auth.get('user_info')

        return self.check_user_authorization()


    def check_user_authorization(self) -> bool:
        """
        Check if the user is authorized to access the app based on cached permissions.
        """
        cached_permissions = session.get('scda_auth_cache', {}).get('permissions', [])
        required_permission = ""

        if request.path == "/_dash-update-component":
            body = request.get_json() or {}
            changed_props = body.get("changedPropIds", [])

            # Navigation events
            if any(".pathname" in prop for prop in changed_props):
                pathname = next(
                    (
                        inp.get("value") for inp in body.get("inputs", [])
                        if isinstance(inp, dict)
                        and inp.get("property") == "pathname"
                    ),
                    None,
                )

                if pathname:
                    session['current_page_path'] = pathname
                    required_permission = f"{self.app_name}:{pathname}:view"
                else:
                    # This shouldn't really happen, but if no pathname is found,
                    # we log a warning and return False.
                    logging.warning("Navigation event detected, but no pathname found in inputs.")
                    return False
            else:
                # Component interaction callbacks
                current_path = session.get('current_page_path', '/')
                required_permission = f"{self.app_name}:{current_path}:view"
        else:
            # Direct page load, store the path and check its permissions
            session['current_page_path'] = request.path
            required_permission = f"{self.app_name}:{request.path}:view"

        if required_permission in cached_permissions:
            return True
        else:
            logging.warning(
                f"User {session.get('user', {}).get('id', 'unknown')} denied access to {request.path}. "
                f"Missing required permission: '{required_permission}'."
            )
            session['authorization_failure_reason'] = self.AUTH_REASON_ROUTE_PERMISSION_MISSING
            session['missing_permission_detail'] = required_permission
            session['needs_permissions'] = True
            return False


    def verify_token(self, token: str) -> Tuple[bool, dict]:
        try:
            response = requests.post(
                self.auth_url + "/verify_token",
                json = {
                    "access_token": token,
                    "token_type": "bearer",
                }
            )
            response.raise_for_status()
            is_verified = response.json()["is_verified"]
            return is_verified, response.json()["token_payload"]
        except requests.exceptions.RequestException as e:
            logging.exception(f"Error verifying token: {e}")
            return False, {}


    def get_user_effective_permissions(self, user_id: str, access_token: str) -> Tuple[Optional[List[dict]], Optional[str]]:
        """
        Get all effective permissions for a user within this app.
        """
        if not self.app_id:
            logging.error("Cannot get user effective permissions: app_id is not set.")
            return None, self.AUTH_REASON_APP_ID_MISSING

        permissions_url = urljoin(
            self.auth_url, f"/apps/{self.app_id}/users/{user_id}/permissions/effective"
        )

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.get(permissions_url, headers = headers)
            response.raise_for_status()
            permissions_response = response.json()
            return permissions_response.get("data", []), None

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error fetching effective permissions from {permissions_url} for user {user_id}, app {self.app_id}")
            if e.response.status_code == 404:
                return None, self.AUTH_REASON_NO_EFFECTIVE_PERMISSIONS
            return None, self.AUTH_REASON_SERVICE_ERROR

        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching effective permissions from {permissions_url} for user {user_id}, app {self.app_id}: {e}",)
            return None, self.AUTH_REASON_SERVICE_ERROR

        except ValueError:
            logging.error(
                f"Failed to decode JSON response from {permissions_url} "
                f"when fetching effective permissions for user {user_id}, app {self.app_id}.",
            )
            return None, self.AUTH_REASON_SERVICE_ERROR


    def has_permission(self, required_permission: str) -> bool:
        """
        Checks if the current user has a specific permission based on the session cache.
        This is a high-performance utility for use inside Dash callbacks.

        Args:
            required_permission: The full permission string (e.g., 'my-app:reports:edit').

        Returns:
            True if the user has the permission, False otherwise.
        """
        cached_permissions = session.get('scda_auth_cache', {}).get('permissions', [])
        return required_permission in cached_permissions


    def check_current_user_authorization(self) -> bool:
        """
        Check if the current user is authorized to access the app. This method
        expects the user to be logged in and the user info to be stored in the
        session.
        """
        url = urljoin(self.auth_url, "/users/me/apps")
        try:
            access_token = request.cookies.get("access_token", None)
            response = requests.get(url, headers = {"Authorization": f"Bearer {access_token}"})
            response.raise_for_status()
            return response.json().get("is_authorized", False)
        except requests.exceptions.RequestException as e:
            logging.exception(f"Error checking user authorization: {e}")
            return False


    def force_refresh_permissions(self) -> bool:
        """
        Forces an immediate re-fetch of the user's permissions from the
        authentication backend, bypassing the cache timer.

        Returns:
            True if the refresh was successful, False otherwise.
        """
        access_token = request.cookies.get("access_token") or re.sub("Bearer ", "", request.headers.get("Authorization", ""))
        if not access_token:
            return False

        logging.info("Forcing a manual refresh of user permissions cache.")
        return self._fetch_and_cache_auth_data(access_token)


    # #################################### #
    #            Private Methods           #
    # #################################### #
    def __app_name_registered(self) -> bool:
        url_app_path = f"/apps/name/{self.app_name}"
        url = urljoin(self.auth_url, url_app_path)
        try:
            response = requests.get(url)
            response.raise_for_status()
            app_data = response.json()
            if self.app_name == app_data.get("name"):
                self.app_id = app_data.get("id")
                if self.app_id is None:
                    logging.error(
                        f"App name {self.app_name} found but 'id' is missing in the response from {url}."
                    )
                    raise RuntimeError(f"Auth service response for '{self.app_name}' is missing an ID.")
                    # return False
                logging.info(f"Successfully verified app '{self.app_name}' with ID '{self.app_id}'.")
                return True
            else:
                logging.warning(
                    f"App name {self.app_name} does not match the name in the response from {url}."
                )
                raise RuntimeError("Received mismatched app data from the auth service.")
                # return False
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                f"Could not reach to the auth service at {self.auth_url}. "
                "Please check the network is stable, and ensure the service is running."
            ) from e

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                e_msg = (
                    f"App name {self.app_name} not registered in auth service. "
                    f"Did you register it? You can request a registration at {self.auth_url}/register/apps"
                )
                logging.exception(e_msg)
                raise RuntimeError(e_msg) from e
            if e.response.status_code >= 500:
                e_msg = (
                    f"Internal server error when verifying app name {self.app_name}. "
                    "Please try again later or contact the administrator."
                )
                logging.exception(e_msg)
                raise RuntimeError(e_msg) from e
            else:
                e_msg = (
                    f"Unexpected HTTP error when verifying app name {self.app_name}: "
                    f"{e.response.status_code} - {e.response.text}"
                )
                logging.exception(e_msg)
                raise RuntimeError(e_msg) from e

        except requests.exceptions.RequestException as e:
            e_msg = (
                f"A network error occurred while trying to verify app name {self.app_name}: {str(e)}"
            )
            logging.exception(e_msg)
            raise RuntimeError(e_msg) from e


    def _get_redirect_url(self) -> str:
        """Helper method to determine the correct redirect URL based on session state"""
        if session.get("needs_registration", False):
            session.pop("needs_registration")
            registration_url = urljoin(self.auth_url, "/register/user")
            query_params = urlencode({'app': self.app_name})
            return f"{registration_url}?{query_params}"

        if session.get("needs_permissions", False):
            session['scda_auth_awaiting_update'] = True

            session.pop("needs_permissions")
            permissions_url = urljoin(self.auth_url, "/request-permissions")
            permission_route = session.get("missing_permission_detail", '')
            permission_action = "view"
            query_params = urlencode({
                'app': self.app_name,
                'permission_route': permission_route,
                'permission_action': permission_action
            })
            return f"{permissions_url}?{query_params}"

        # Default login redirect
        next_url = request.url_root
        auth_url_with_next = urljoin(self.auth_url, '/login')
        query_params = urlencode({'next': next_url})
        return f"{auth_url_with_next}?{query_params}"


    def _get_access_token(self) -> Optional[str]:
        """
        Helper method to retrieve the access token from cookies or headers.
        """
        access_token = (
            request.cookies.get("access_token")
            or
            re.sub("Bearer ", "", request.headers.get("Authorization", ""))
        )
        return access_token if access_token else None


    def _fetch_and_cache_auth_data(self, access_token: str) -> bool:
        """Verifies token and fetches permissions, then caches them in the session."""
        # NOTE: This is a *hack* for now, the dash_update-component endpoint
        # keeps sending requests when failed to set the session.
        # This is a workaround to avoid the infinite loop of requests.
        if request.path == "/_dash-update-component":
            return True

        try:
            is_verified, token_payload = self.verify_token(access_token)
            if not is_verified:
                flash("Your session is invalid or has expired. Please log in again.")
                return False

            user_id = token_payload["user_info"]["id"]

            permissions_data, failure_reason = self.get_user_effective_permissions(user_id, access_token)

            if failure_reason:
                session['authorization_failure_reason'] = failure_reason
                return False

            session['scda_auth_cache'] = {
                'user_info': token_payload.get("user_info"),
                'permissions': list({p.get('name') for p in permissions_data if p.get('name')}),
                'timestamp': time.time()
            }
            return True
        except Exception as e:
            logging.exception(f"Critical error during auth data fetch: {e}")
            session['authorization_failure_reason'] = self.AUTH_REASON_SERVICE_ERROR
            return False
