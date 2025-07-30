*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic Timestamp and Screenshot
# ---------------------------------------------

*** Settings ***
Library    SeleniumLibrary
Library    AllureLibrary
Library    Screenshot

*** Keywords ***
LPS.Get Current Timestamp
    ${timestamp}=    Evaluate    datetime.datetime.now().strftime("%Y%m%d%H%M%S")    modules=datetime
    RETURN    ${timestamp}

LPS.Capture Screenshot With Timestamp And Attach To Allure
    [Arguments]    ${directory}
    ${timestamp}=    LPS.Get Current Timestamp
    ${filename}=    Set Variable    ${timestamp}_screenshot.png
    ${path}=    Set Variable    ${directory}/${filename}
    Capture Page Screenshot    ${path}
    Attach File    ${path}    Screenshot

LPS.Set Screenshot Directory
    [Arguments]    ${directory}
    Set Screenshot Directory    ${directory}

LPS.Take Screenshot
    [Arguments]    ${filename}=    ${embed}=True
    ${result}=    Take Screenshot    ${filename}    ${embed}
    RETURN    ${result}

LPS.Take Screenshot Without Embedding
    [Arguments]    ${filename}=
    ${result}=    Take Screenshot Without Embedding    ${filename}
    RETURN    ${result}
