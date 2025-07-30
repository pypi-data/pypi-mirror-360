*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic browser controls
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
*** Keywords ***

LPS.Open Browser To URL
    [Arguments]    ${url}    ${browser}
    Open Browser    ${url}    ${browser}
    Maximize Browser Window

LPS.Maximize Browser Window
    Maximize Browser Window

LPS.Minimize Browser Window
    Minimize Browser Window

LPS.Close Window
    Close Window

LPS.Close All Browser
    Close All Browsers

LPS.Go To URL
    [Arguments]    ${url}
    Go To    ${url}

LPS.Go Back To Previous Page
    Go Back

LPS.Get Browser Aliases
    ${aliases}=    Get Browser Aliases
    RETURN    ${aliases}

LPS.Get Browser Id
    ${ids}=    Get Browser Ids
    RETURN    ${ids}

LPS.Get Cookie
    [Arguments]    ${name}
    ${cookie}=    Get Cookie    ${name}
    RETURN    ${cookie}

LPS.Get Cookies
    ${cookies}=    Get Cookies
    RETURN    ${cookies}

LPS.Get Location
    ${location}=    Get Location
    RETURN    ${location}

LPS.Get Locations
    ${locations}=    Get Locations
    RETURN    ${locations}

LPS.Get Session Id
    ${session_id}=    Get Session Id
    RETURN    ${session_id}

LPS.Get Windows Handles
    ${handles}=    Get Window Handles
    RETURN    ${handles}

LPS.Get Window Identifiers
    ${ids}=    Get Window Identifiers
    RETURN    ${ids}

LPS.Get Window Names
    ${names}=    Get Window Names
    RETURN    ${names}

LPS.Title Should Be
    [Arguments]    ${title}
    Title Should Be    ${title}

LPS.Get Window Titles
    ${titles}=    Get Window Titles
    RETURN    ${titles}

LPS.Location Should Be
    [Arguments]    ${url}
    Location Should Be    ${url}

LPS.Location Should Contain
    [Arguments]    ${expected}
    Location Should Contain    ${expected}

LPS.Close Browser
    Close Browser

LPS.Log
    [Arguments]    ${message}
    Log    ${message}

LPS.Should Contain
    [Arguments]    ${container}    ${item}    ${msg}=None    ${values}=None
    Should Contain    ${container}    ${item}    ${msg}    ${values}

LPS.Should Not Contain
    [Arguments]    ${container}    ${item}    ${msg}=None    ${values}=None
    Should Not Contain    ${container}    ${item}    ${msg}    ${values}

LPS.Log Location
    Log Location

LPS.Set Browser Implicit Wait in Seconds
    [Arguments]    ${seconds}
    Set Browser Implicit Wait    ${seconds}

LPS.Set Selenium Implicit Wait in Seconds
    [Arguments]    ${seconds}
    Set Selenium Implicit Wait    ${seconds}

LPS.Switch Browser
    [Arguments]    ${browser_id_or_alias}
    Switch Browser    ${browser_id_or_alias}

LPS.Switch Window
    Switch Window

LPS.Page Should Contain
    [Arguments]     ${text}
    Page Should Contain    ${text}