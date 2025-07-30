#  ---------------------------------------------------------------------------------
#  Copyright (c) 2025 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2025.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------
import json
import os

from datarobot_dome.constants import RUNTIME_PARAMETER_PREFIX


def get_runtime_parameter_value_bool(param_name: str, default_value: bool) -> bool:
    """
    Retrieve the value of a boolean-typed model runtime parameter with the specified name.

    Parameters
    ----------
    param_name
        The name of the model runtime parameter to retrieve (without the env variable prefix).
    default_value
        The default value to return if the model runtime parameter is undefined or underspecified.

    Returns
    -------
    The parsed runtime parameter value.
    """
    env_var_name = f"{RUNTIME_PARAMETER_PREFIX}{param_name}"
    param_body = json.loads(os.environ.get(env_var_name, "{}"))

    if not param_body:
        return default_value

    if "payload" not in param_body:
        return default_value

    return bool(param_body["payload"])
