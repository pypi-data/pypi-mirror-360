*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic Collection Steps
# ---------------------------------------------

*** Settings ***
Library    Collections

*** Keywords ***
LPS.Append To List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Append To List    @{args}
    RETURN    ${output}

LPS.Combine Lists
    [Arguments]    @{args}
    ${output}=    Run Keyword    Combine Lists    @{args}
    RETURN    ${output}

LPS.Copy List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Copy List    @{args}
    RETURN    ${output}

LPS.Count Values In List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Count Values In List    @{args}
    RETURN    ${output}

LPS.Get Index From List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get Index From List    @{args}
    RETURN    ${output}

LPS.Get Slice From List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get Slice From List    @{args}
    RETURN    ${output}

LPS.Insert Into List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Insert Into List    @{args}
    RETURN    ${output}

LPS.Lists Should Be Equal
    [Arguments]    @{args}
    ${output}=    Run Keyword    Lists Should Be Equal    @{args}
    RETURN    ${output}

LPS.Remove From List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Remove From List    @{args}
    RETURN    ${output}

LPS.Remove Duplicates
    [Arguments]    @{args}
    ${output}=    Run Keyword    Remove Duplicates    @{args}
    RETURN    ${output}

LPS.Set List Value
    [Arguments]    @{args}
    ${output}=    Run Keyword    Set List Value    @{args}
    RETURN    ${output}

LPS.Sort List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Sort List    @{args}
    RETURN    ${output}

LPS.Reverse List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Reverse List    @{args}
    RETURN    ${output}

LPS.Copy Dictionary
    [Arguments]    @{args}
    ${output}=    Run Keyword    Copy Dictionary    @{args}
    RETURN    ${output}

LPS.Get Dictionary Keys
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get Dictionary Keys    @{args}
    RETURN    ${output}

LPS.Get Dictionary Values
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get Dictionary Values    @{args}
    RETURN    ${output}

LPS.Get From Dictionary
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get From Dictionary    @{args}
    RETURN    ${output}

LPS.Dictionary Should Contain Key
    [Arguments]    @{args}
    ${output}=    Run Keyword    Dictionary Should Contain Key    @{args}
    RETURN    ${output}

LPS.Dictionary Should Contain Value
    [Arguments]    @{args}
    ${output}=    Run Keyword    Dictionary Should Contain Value    @{args}
    RETURN    ${output}

LPS.Dictionary Should Contain Item
    [Arguments]    @{args}
    ${output}=    Run Keyword    Dictionary Should Contain Item    @{args}
    RETURN    ${output}

LPS.Dictionaries Should be Equal
    [Arguments]    @{args}
    ${output}=    Run Keyword    Dictionaries Should Be Equal    @{args}
    RETURN    ${output}

LPS.Remove From Dictionary
    [Arguments]    @{args}
    ${output}=    Run Keyword    Remove From Dictionary    @{args}
    RETURN    ${output}

LPS.Set To Dictionary
    [Arguments]    @{args}
    ${output}=    Run Keyword    Set To Dictionary    @{args}
    RETURN    ${output}

LPS.Convert To Dictionary
    [Arguments]    @{args}
    ${output}=    Run Keyword    Convert To Dictionary    @{args}
    RETURN    ${output}

LPS.Get From List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get From List    @{args}
    RETURN    ${output}

LPS.List Should Contain Value
    [Arguments]    @{args}
    ${output}=    Run Keyword    List Should Contain Value    @{args}
    RETURN    ${output}

LPS.List Should Not Contain Value
    [Arguments]    @{args}
    ${output}=    Run Keyword    List Should Not Contain Value    @{args}
    RETURN    ${output}

LPS.Get Matches
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get Matches    @{args}
    RETURN    ${output}

LPS.Get Match Count
    [Arguments]    @{args}
    ${output}=    Run Keyword    Get Match Count    @{args}
    RETURN    ${output}

LPS.Remove Values From List
    [Arguments]    @{args}
    ${output}=    Run Keyword    Remove Values From List    @{args}
    RETURN    ${output}