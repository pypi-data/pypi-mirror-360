*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic checks
# ---------------------------------------------

*** Settings ***
Resource    settings.resource
Library     DateTime

*** Keywords ***
LPS.Alert Should Be Present
    [Arguments]    ${alert_text}    ${action}
    Alert Should Be Present    ${alert_text}    ${action}

LPS.Element Should Be Visible By Id
    [Arguments]    ${id}
    Element Should Be Visible    id=${id}

LPS.Element Should Be Visible By XPath
    [Arguments]    ${xpath}
    Element Should Be Visible    xpath=${xpath}

LPS.Element Should Be Visible By Class
    [Arguments]    ${class}
    Element Should Be Visible    class=${class}

LPS.Set Focus To Element By Id
    [Arguments]    ${id}
    Set Focus To Element    id=${id}

LPS.Set Focus To Element By XPath
    [Arguments]    ${xpath}
    Set Focus To Element    xpath=${xpath}

LPS.Set Focus To Element By Class
    [Arguments]    ${class}
    Set Focus To Element    class=${class}

LPS.Checkbox Should Be Selected by Id
    [Arguments]    ${id}
    Checkbox Should Be Selected    id=${id}

LPS.Checkbox Should Be Selected by XPath
    [Arguments]    ${xpath}
    Checkbox Should Be Selected    xpath=${xpath}

LPS.Checkbox Should Be Selected by Class
    [Arguments]    ${class}
    Checkbox Should Be Selected    class=${class}

LPS.Checkbox Should Not Be Selected by Id
    [Arguments]    ${id}
    Checkbox Should Not Be Selected    id=${id}

LPS.Checkbox Should Not Be Selected by XPath
    [Arguments]    ${xpath}
    Checkbox Should Not Be Selected    xpath=${xpath}

LPS.Checkbox Should Not Be Selected by Class
    [Arguments]    ${class}
    Checkbox Should Not Be Selected    class=${class}

LPS.Page Should Contain Checkbox by Id
    [Arguments]    ${id}
    Page Should Contain Checkbox    id=${id}

LPS.Page Should Contain Checkbox by XPath
    [Arguments]    ${xpath}
    Page Should Contain Checkbox    xpath=${xpath}

LPS.Page Should Contain Checkbox by Class
    [Arguments]    ${class}
    Page Should Contain Checkbox    class=${class}

LPS.Page Should Contain Button by Id
    [Arguments]    ${id}
    Page Should Contain Button    id=${id}

LPS.Page Should Contain Button by XPath
    [Arguments]    ${xpath}
    Page Should Contain Button    xpath=${xpath}

LPS.Page Should Contain Button by Class
    [Arguments]    ${class}
    Page Should Contain Button    class=${class}

LPS.Page Should Contain Element by Id
    [Arguments]    ${id}
    Page Should Contain Element    id=${id}

LPS.Page Should Contain Element by XPath
    [Arguments]    ${xpath}
    Page Should Contain Element    xpath=${xpath}

LPS.Page Should Contain Element by Class
    [Arguments]    ${class}
    Page Should Contain Element    class=${class}

LPS.Page Should Contain Image by Id
    [Arguments]    ${id}
    Page Should Contain Image    id=${id}

LPS.Page Should Contain Image by XPath
    [Arguments]    ${xpath}
    Page Should Contain Image    xpath=${xpath}

LPS.Page Should Contain Image by Class
    [Arguments]    ${class}
    Page Should Contain Image    class=${class}

LPS.Page Should Contain Radio Button by Id
    [Arguments]    ${id}
    Page Should Contain Radio Button    id=${id}

LPS.Page Should Contain Radio Button by XPath
    [Arguments]    ${xpath}
    Page Should Contain Radio Button    xpath=${xpath}

LPS.Page Should Contain Radio Button by Class
    [Arguments]    ${class}
    Page Should Contain Radio Button    class=${class}

LPS.Page Should Contain Textfield by Id
    [Arguments]    ${id}
    Page Should Contain Textfield    id=${id}

LPS.Page Should Contain Textfield by XPath
    [Arguments]    ${xpath}
    Page Should Contain Textfield    xpath=${xpath}

LPS.Page Should Contain Textfield by Class
    [Arguments]    ${class}
    Page Should Contain Textfield    class=${class}

LPS.Page Should Contain List by Id
    [Arguments]    ${id}
    Page Should Contain List    id=${id}

LPS.Page Should Contain List by XPath
    [Arguments]    ${xpath}
    Page Should Contain List    xpath=${xpath}

LPS.Page Should Contain List by Class
    [Arguments]    ${class}
    Page Should Contain List    class=${class}

LPS.Should Be Equal As Numbers
    [Arguments]    ${first}    ${second}
    Should Be Equal As Numbers    ${first}    ${second}

LPS.Should Be True
    [Arguments]    ${condition}    ${msg}=None
    Should Be True    ${condition}    ${msg}

LPS.Dictionary Should Contain Key
    [Arguments]    ${dictionary}    ${key}    ${msg}=None
    Dictionary Should Contain Key    ${dictionary}    ${key}    ${msg}

LPS.Get Current Date
    [Arguments]    ${result_format}=%Y-%m-%d    ${increment}=0 days
    ${date}=    Get Current Date    result_format=${result_format}    increment=${increment}
    RETURN    ${date}

LPS.File Should Exist
    [Arguments]    ${path}    ${msg}=None
    File Should Exist    ${path}    ${msg}

LPS.Should Be Equal
    [Arguments]    ${first}    ${second}    ${msg}=None    ${values}=None
    Should Be Equal    ${first}    ${second}    ${msg}    ${values}