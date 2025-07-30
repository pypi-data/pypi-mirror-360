*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic waits
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Wait Until Element Is Visible By Id
    [Arguments]    ${id}    ${timeout}=30s
    Wait Until Page Contains Element    id=${id}    ${timeout}

LPS.Wait Until Element Is Visible By XPath
    [Arguments]    ${xpath}    ${timeout}=30s
    Wait Until Page Contains Element    xpath=${xpath}    ${timeout}

LPS.Wait Until Element Is Visible By Class
    [Arguments]    ${class}    ${timeout}=30s
    Wait Until Page Contains Element    class=${class}    ${timeout}

LPS.Wait Until Element Contains Text By Id
    [Arguments]    ${id}    ${text}    ${timeout}=30s
    Wait Until Element Contains    id=${id}    ${text}    ${timeout}

LPS.Wait Until Element Contains Text By XPath
    [Arguments]    ${xpath}    ${text}    ${timeout}=30s
    Wait Until Element Contains    xpath=${xpath}    ${text}    ${timeout}

LPS.Wait Until Element Contains Text By Class
    [Arguments]    ${class}    ${text}    ${timeout}=30s
    Wait Until Element Contains    class=${class}    ${text}    ${timeout}

LPS.Wait Until Element Is Not Visible By Id
    [Arguments]    ${id}    ${timeout}=30s
    Wait Until Element Is Not Visible    id=${id}    ${timeout}

LPS.Wait Until Element Is Not Visible By XPath
    [Arguments]    ${xpath}    ${timeout}=30s
    Wait Until Element Is Not Visible    xpath=${xpath}    ${timeout}

LPS.Wait Until Element Is Not Visible By Class
    [Arguments]    ${class}    ${timeout}=30s
    Wait Until Element Is Not Visible    class=${class}    ${timeout}

LPS.Wait Until Page Contains Text
    [Arguments]    ${text}    ${timeout}=30s
    Wait Until Page Contains    ${text}    ${timeout}

LPS.Wait Until Element Is Interactable by Id
    [Arguments]    ${id}    ${timeout}=30s
    Wait Until Element Is Visible    id=${id}    ${timeout}
    Wait Until Element Is Enabled    id=${id}    ${timeout}

LPS.Wait Until Element Is Interactable by XPath
    [Arguments]    ${xpath}    ${timeout}=30s
    Wait Until Element Is Visible    xpath=${xpath}    ${timeout}
    Wait Until Element Is Enabled    xpath=${xpath}    ${timeout}

LPS.Wait Until Element Is Interactable by Class
    [Arguments]    ${class}    ${timeout}=30s
    Wait Until Element Is Visible    class=${class}    ${timeout}
    Wait Until Element Is Enabled    class=${class}    ${timeout}

LPS.Wait For Seconds
    [Arguments]    ${seconds}=3s
    Log    ⏳ Waiting for ${seconds} ...
    Sleep    ${seconds}
