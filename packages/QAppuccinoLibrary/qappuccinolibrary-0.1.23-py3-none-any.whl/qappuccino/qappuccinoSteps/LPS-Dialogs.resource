*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic Dialog Steps
# ---------------------------------------------

*** Settings ***
Library    Dialogs

*** Keywords ***
LPS.Execute Manual Step
    [Arguments]    ${message}    ${default_return_value}=None
    Execute Manual Step    ${message}    ${default_return_value}

LPS.Get Selection From User
    [Arguments]    ${message}    ${options}
    ${selection}=    Get Selection From User    ${message}    ${options}
    RETURN    ${selection}

LPS.Get Selections From User
    [Arguments]    ${message}    ${options}
    @{selections}=    Get Selections From User    ${message}    ${options}
    RETURN    @{selections}

LPS.Get Value From User
    [Arguments]    ${message}    ${default_value}=None
    ${value}=    Get Value From User    ${message}    ${default_value}
    RETURN    ${value}

LPS.Pause Execution
    [Arguments]    ${message}=Execution paused. Click OK to continue.
    Pause Execution    ${message}
