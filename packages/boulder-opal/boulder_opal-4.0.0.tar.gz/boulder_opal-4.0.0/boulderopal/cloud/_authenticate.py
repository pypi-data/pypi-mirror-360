# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

import os
from typing import Optional

from qctrlclient.defaults import get_default_api_url
from qctrlworkflowclient.defaults import get_authenticated_client_for_product
from qctrlworkflowclient.router import ApiRouter

from boulderopal._configuration.configuration import (
    _show_usage_time,
    configure,
    get_configuration,
    get_default_api_key_auth,
)
from boulderopal._constants import (
    API_KEY_NAME,
    PACKAGE_INFO,
)


def authenticate(api_key: Optional[str] = None) -> None:
    """
    Authenticate a Boulder Opal session.

    Parameters
    ----------
    api_key : str or None, optional
        Your Q-CTRL API key. If you don't provide one,
        the key should be saved in an environment variable
        called QCTRL_API_KEY.
    """
    if api_key is None:
        try:
            api_key = os.environ[API_KEY_NAME]
        except KeyError as error:
            raise RuntimeError(
                "No API key provided in environment or function call. "
                "To call this function without arguments, "
                f"save your API key's value in the {API_KEY_NAME} environment variable."
            ) from error

    # Create a router that uses the global settings and an internal
    # client with token-based authentication.
    client = get_authenticated_client_for_product(
        package_name=PACKAGE_INFO.install_name,
        api_url=get_default_api_url(),
        auth=get_default_api_key_auth(api_key),
    )

    # Grab the global Boulder Opal settings, which specify a default router
    # whose internal GQL client uses browser-based authentication.
    settings = get_configuration()

    router = ApiRouter(client, settings)
    _show_usage_time(router)

    # Configure the global settings to use the router with token-based
    # authentication.
    configure(router=router)

    print("Q-CTRL authentication successful!")
