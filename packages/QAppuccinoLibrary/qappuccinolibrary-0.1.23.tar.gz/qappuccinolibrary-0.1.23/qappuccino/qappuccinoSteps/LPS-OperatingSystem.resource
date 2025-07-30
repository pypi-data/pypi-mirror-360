*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic OS Steps
# ---------------------------------------------

*** Settings ***
Library    OperatingSystem

*** Keywords ***
LPS.Copy Directory
    [Arguments]    @{args}
    Copy Directory    @{args}

LPS.Copy File
    [Arguments]    @{args}
    Copy File    @{args}

LPS.Create Directory
    [Arguments]    @{args}
    Create Directory    @{args}

LPS.Create File
    [Arguments]    @{args}
    Create File    @{args}

LPS.Directory Should Exist
    [Arguments]    @{args}
    Directory Should Exist    @{args}

LPS.Directory Should Not Exist
    [Arguments]    @{args}
    Directory Should Not Exist    @{args}

LPS.File Should Exist
    [Arguments]    ${path}    ${msg}=None
    File Should Exist    ${path}    ${msg}

LPS.File Should Not Exist
    [Arguments]    @{args}
    File Should Not Exist    @{args}

LPS.Get File
    [Arguments]    @{args}
    Get File    @{args}

LPS.Get File Size
    [Arguments]    @{args}
    Get File Size    @{args}

LPS.Get Modification Time
    [Arguments]    @{args}
    Get Modified Time    @{args}

LPS.Get Environment Variable
    [Arguments]    @{args}
    Get Environment Variable    @{args}

LPS.List Directories In Directory
    [Arguments]    @{args}
    List Directories In Directory    @{args}

LPS.List Files In Directory
    [Arguments]    @{args}
    List Files In Directory    @{args}

LPS.List Directory
    [Arguments]    @{args}
    List Directory    @{args}

LPS.Move Directory
    [Arguments]    @{args}
    Move Directory    @{args}

LPS.Move File
    [Arguments]    @{args}
    Move File    @{args}

LPS.Remove Directory
    [Arguments]    @{args}
    Remove Directory    @{args}

LPS.Remove File
    [Arguments]    @{args}
    Remove File    @{args}

LPS.Touch
    [Arguments]    @{args}
    Touch    @{args}

LPS.File Should Be Empty
    [Arguments]    @{args}
    File Should Be Empty    @{args}

LPS.File Should Not Be Empty
    [Arguments]    @{args}
    File Should Not Be Empty    @{args}

LPS.Append To File
    [Arguments]    @{args}
    Append To File    @{args}

LPS.Set Environment Variable
    [Arguments]    @{args}
    Set Environment Variable    @{args}

LPS.Remove Environment Variable
    [Arguments]    @{args}
    Remove Environment Variable    @{args}

LPS.Should Exist
    [Arguments]    @{args}
    Should Exist    @{args}

LPS.Should Not Exist
    [Arguments]    @{args}
    Should Not Exist    @{args}

LPS.Run
    [Arguments]    @{args}
    Run    @{args}

LPS.Run And Return Rc
    [Arguments]    @{args}
    Run And Return Rc    @{args}

LPS.Run And Return Rc And Output
    [Arguments]    @{args}
    Run And Return Rc And Output    @{args}