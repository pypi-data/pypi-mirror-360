*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic clicks
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Click Element By Id
    [Arguments]    ${id}
    Click Element    id=${id}

LPS.Click Element By XPath
    [Arguments]    ${xpath}
    Click Element    xpath=${xpath}

LPS.Click Element By Class
    [Arguments]    ${class}
    Click Element    class=${class}

LPS.Click Button By Id
    [Arguments]    ${id}
    Click Button    id=${id}

LPS.Click Button By XPath
    [Arguments]    ${xpath}
    Click Button    xpath=${xpath}

LPS.Click Button By Class
    [Arguments]    ${class}
    Click Button    class=${class}

LPS.Click Link By Id
    [Arguments]    ${id}
    Click Link    id=${id}

LPS.Click Link By XPath
    [Arguments]    ${xpath}
    Click Link    xpath=${xpath}

LPS.Click Link By Class
    [Arguments]    ${class}
    Click Link    class=${class}

LPS.Double Click Element By Id
    [Arguments]    ${id}
    Double Click Element    id=${id}

LPS.Double Click Element By XPath
    [Arguments]    ${xpath}
    Double Click Element    xpath=${xpath}

LPS.Double Click Element By Class
    [Arguments]    ${class}
    Double Click Element    class=${class}

LPS.Click Image By Id
    [Arguments]    ${id}
    Click Image    id=${id}

LPS.Click Image By XPath
    [Arguments]    ${xpath}
    Click Image    xpath=${xpath}

LPS.Click Image By Class
    [Arguments]    ${class}
    Click Image    class=${class}

LPS.Click Element At Coordinates By Id
    [Arguments]    ${id}    ${x_offset}    ${y_offset}
    Click Element At Coordinates    id=${id}    ${x_offset}    ${y_offset}

LPS.Click Element At Coordinates By XPath
    [Arguments]    ${xpath}    ${x_offset}    ${y_offset}
    Click Element At Coordinates    xpath=${xpath}    ${x_offset}    ${y_offset}

LPS.Click Element At Coordinates By Class
    [Arguments]    ${class}    ${x_offset}    ${y_offset}
    Click Element At Coordinates    class=${class}    ${x_offset}    ${y_offset}

LPS.Click Button If Exists
    [Arguments]    ${locator}    ${timeout}=5s
    ${is_present}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    ${timeout}
    Run Keyword If    ${is_present}    Click Element    ${locator}

LPS.Click Element When Visible
    [Arguments]    ${locator}    ${timeout}=10s
    [Documentation]    Waits until the element identified by ${locator} is visible within ${timeout}, then clicks it.
    Wait Until Element Is Visible    ${locator}    ${timeout}
    Click Element    ${locator}