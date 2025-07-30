import json
from typing import Dict, List, Optional, cast, final

from flask import Request

from .types import AdapterRequest, RequestInterceptor


@final
class PayloadParamsModifierInterceptor(RequestInterceptor):
    """Adapter for modifying request payload by removing, adding, and renaming parameters"""

    _params_to_remove: List[str]
    _params_to_add: Dict[str, any]
    _params_to_rename: Dict[str, str]

    def __init__(
        self,
        params_to_remove: Optional[List[str]] = None,
        params_to_add: Optional[Dict[str, any]] = None,
        params_to_rename: Optional[Dict[str, str]] = None,
    ):
        self._params_to_remove = params_to_remove or []
        self._params_to_add = params_to_add or {}
        self._params_to_rename = params_to_rename or {}

    @final
    def intercept_request(self, ar: AdapterRequest) -> AdapterRequest:
        # Parse the original request data
        original_data = json.loads(ar.r.get_data())

        # Create a new payload starting with the original
        new_data = original_data.copy()

        # Remove specified parameters
        for param in self._params_to_remove:
            if param in new_data:
                del new_data[param]

        # Add new parameters
        new_data.update(self._params_to_add)

        # Rename parameters
        for old_key, new_key in self._params_to_rename.items():
            if old_key in new_data:
                new_data[new_key] = new_data.pop(old_key)

        # Create new request with modified data
        new_request = cast(
            Request,
            Request.from_values(
                method=ar.r.method,
                headers=dict(ar.r.headers),
                data=json.dumps(new_data),
            ),
        )

        return AdapterRequest(
            r=new_request,
            meta=ar.meta,
        )
