*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic JSON Steps
# ---------------------------------------------

*** Settings ***
Library    JSONLibrary

*** Keywords ***
LPS.Load_JSON_From_File
    [Arguments]    @{args}
    Load JSON From File    @{args}

LPS.Get_Value_From_Json
    [Arguments]    @{args}
    Get Value From Json    @{args}

LPS.Update_Value_To_Json
    [Arguments]    @{args}
    Update Value To Json    @{args}

LPS.Convert_String_To_Json
    [Arguments]    @{args}
    Convert String To Json    @{args}

LPS.Convert_Json_To_String
    [Arguments]    @{args}
    Convert Json To String    @{args}

