*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic input
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Input Text Into Alert
    [Arguments]    ${text}
    Input Text Into Alert    ${text}

LPS.Input Text By Id
    [Arguments]    ${id}    ${text}
    Input Text    id=${id}    ${text}

LPS.Input Text By XPath
    [Arguments]    ${xpath}    ${text}
    Input Text    xpath=${xpath}    ${text}

LPS.Input Text By Class
    [Arguments]    ${class}    ${text}
    Input Text    class=${class}    ${text}

LPS.Input Password By Id
    [Arguments]    ${id}    ${text}
    Input Password    id=${id}    ${text}

LPS.Input Password By XPath
    [Arguments]    ${xpath}    ${text}
    Input Password    xpath=${xpath}    ${text}

LPS.Input Password By Class
    [Arguments]    ${class}    ${text}
    Input Password    class=${class}    ${text}

LPS.Clear Text By Id
    [Arguments]    ${id}
    Clear Element Text    id=${id}

LPS.Clear Text By XPath
    [Arguments]    ${xpath}
    Clear Element Text    xpath=${xpath}

LPS.Clear Text By Class
    [Arguments]    ${class}
    Clear Element Text    class=${class}

LPS.Choose File By Id
    [Arguments]    ${id}    ${path}
    Choose File    id=${id}    ${path}

LPS.Choose File By XPath
    [Arguments]    ${xpath}    ${path}
    Choose File    xpath=${xpath}    ${path}

LPS.Choose File By Class
    [Arguments]    ${class}    ${path}
    Choose File    class=${class}    ${path}

LPS.Press Key by Id
    [Arguments]    ${id}    ${key}
    Press Key    id=${id}    ${key}

LPS.Press Key by XPath
    [Arguments]    ${xpath}    ${key}
    Press Key    xpath=${xpath}    ${key}

LPS.Press Key by Class
    [Arguments]    ${class}    ${key}
    Press Key    class=${class}    ${key}

LPS.Press Keys
    Press Keys
