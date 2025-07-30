import os
import json
from typing import Tuple, Union


class PerimeterExtractor:
    @classmethod
    def for_ob_cli(
        cls, config_dir: str, profile: str
    ) -> Union[Tuple[str, str], Tuple[None, None]]:
        """
        This function will be called when we are trying to extract the perimeter
        via the ob cli's execution. We will rely on the following logic:
        1. check environment variables like OB_CURRENT_PERIMETER / OBP_PERIMETER
        2. run init config to extract the perimeter related configurations.

        Returns
        -------
            Tuple[str, str] : Tuple containing perimeter name , API server url.
        """
        from outerbounds.utils import metaflowconfig

        perimeter = None
        api_server = None
        if os.environ.get("OB_CURRENT_PERIMETER") or os.environ.get("OBP_PERIMETER"):
            perimeter = os.environ.get("OB_CURRENT_PERIMETER") or os.environ.get(
                "OBP_PERIMETER"
            )

        if os.environ.get("OBP_API_SERVER"):
            api_server = os.environ.get("OBP_API_SERVER")

        if perimeter is None or api_server is None:
            metaflow_config = metaflowconfig.init_config(config_dir, profile)
            perimeter = metaflow_config.get("OBP_PERIMETER")
            api_server = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

        return perimeter, api_server  # type: ignore

    @classmethod
    def during_metaflow_execution(cls) -> str:
        # TODO: implement this
        return ""
