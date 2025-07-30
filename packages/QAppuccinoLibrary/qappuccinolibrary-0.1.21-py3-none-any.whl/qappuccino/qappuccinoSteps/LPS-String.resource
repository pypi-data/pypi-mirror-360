*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic String Steps
# ---------------------------------------------

*** Settings ***
Library    String

*** Keywords ***
LPS.Convert To Lower Case
    [Arguments]    ${string}
    ${result}=    Convert To Lower Case    ${string}
    RETURN    ${result}

LPS.Convert To Title Case
    [Arguments]    ${string}
    ${result}=    Convert To Title Case    ${string}
    RETURN    ${result}

LPS.Convert To Upper Case
    [Arguments]    ${string}
    ${result}=    Convert To Upper Case    ${string}
    RETURN    ${result}

LPS.Decode Bytes To String
    [Arguments]    ${bytes}    ${encoding}=UTF-8    ${errors}=strict
    ${result}=    Decode Bytes To String    ${bytes}    ${encoding}    ${errors}
    RETURN    ${result}

LPS.Encode String To Bytes
    [Arguments]    ${string}    ${encoding}=UTF-8    ${errors}=strict
    ${result}=    Encode String To Bytes    ${string}    ${encoding}    ${errors}
    RETURN    ${result}

LPS.Fetch From Left
    [Arguments]    ${string}    ${marker}
    ${result}=    Fetch From Left    ${string}    ${marker}
    RETURN    ${result}

LPS.Fetch From Right
    [Arguments]    ${string}    ${marker}
    ${result}=    Fetch From Right    ${string}    ${marker}
    RETURN    ${result}

LPS.Format String
    [Arguments]    ${string}    @{positional_args}    &{named_args}
    ${result}=    Format String    ${string}    @{positional_args}    &{named_args}
    RETURN    ${result}

LPS.Generate Random String
    [Arguments]    ${length}    ${chars}=[LETTERS]
    ${result}=    Generate Random String    ${length}    ${chars}
    RETURN    ${result}

LPS.Get Line
    [Arguments]    ${string}    ${line_number}
    ${result}=    Get Line    ${string}    ${line_number}
    RETURN    ${result}

LPS.Get Line Count
    [Arguments]    ${string}
    ${result}=    Get Line Count    ${string}
    RETURN    ${result}

LPS.Get Lines Containing String
    [Arguments]    ${string}    ${pattern}    ${case_insensitive}=False
    ${result}=    Get Lines Containing String    ${string}    ${pattern}    ${case_insensitive}
    RETURN    ${result}

LPS.Get Lines Matching Pattern
    [Arguments]    ${string}    ${pattern}    ${case_insensitive}=False
    ${result}=    Get Lines Matching Pattern    ${string}    ${pattern}    ${case_insensitive}
    RETURN    ${result}

LPS.Get Lines Matching Regexp
    [Arguments]    ${string}    ${pattern}    ${case_insensitive}=False
    ${result}=    Get Lines Matching Regexp    ${string}    ${pattern}    ${case_insensitive}
    RETURN    ${result}

LPS.Get Regexp Matches
    [Arguments]    ${string}    ${pattern}
    ${result}=    Get Regexp Matches    ${string}    ${pattern}
    RETURN    ${result}

LPS.Get Substring
    [Arguments]    ${string}    ${start}    ${end}
    ${result}=    Get Substring    ${string}    ${start}    ${end}
    RETURN    ${result}

LPS.Remove String
    [Arguments]    ${string}    ${substring}
    ${result}=    Remove String    ${string}    ${substring}
    RETURN    ${result}

LPS.Remove String Using Regexp
    [Arguments]    ${string}    ${pattern}
    ${result}=    Remove String Using Regexp    ${string}    ${pattern}
    RETURN    ${result}

LPS.Replace String
    [Arguments]    ${string}    ${search}    ${replace}    ${count}=-1
    ${result}=    Replace String    ${string}    ${search}    ${replace}    ${count}
    RETURN    ${result}

LPS.Replace String Using Regexp
    [Arguments]    ${string}    ${pattern}    ${replace}    ${count}=-1
    ${result}=    Replace String Using Regexp    ${string}    ${pattern}    ${replace}    ${count}
    RETURN    ${result}

LPS.Should Be Byte String
    [Arguments]    ${string}    ${msg}=
    Should Be Byte String    ${string}    ${msg}

LPS.Should Be Lower Case
    [Arguments]    ${string}    ${msg}=
    Should Be Lower Case    ${string}    ${msg}

LPS.Should Be String
    [Arguments]    ${item}    ${msg}=
    Should Be String    ${item}    ${msg}

LPS.Should Be Title Case
    [Arguments]    ${string}    ${msg}=
    Should Be Title Case    ${string}    ${msg}

LPS.Should Be Unicode String
    [Arguments]    ${string}    ${msg}=
    Should Be Unicode String    ${string}    ${msg}

LPS.Should Be Upper Case
    [Arguments]    ${string}    ${msg}=
    Should Be Upper Case    ${string}    ${msg}

LPS.Should Not Be String
    [Arguments]    ${item}    ${msg}=
    Should Not Be String    ${item}    ${msg}

LPS.Split String
    [Arguments]    ${string}    ${separator}=    ${max_split}=-1
    ${result}=    Split String    ${string}    ${separator}    ${max_split}
    RETURN    ${result}

LPS.Split String From Right
    [Arguments]    ${string}    ${separator}=    ${max_split}=-1
    ${result}=    Split String From Right    ${string}    ${separator}    ${max_split}
    RETURN    ${result}

LPS.Split String To Characters
    [Arguments]    ${string}
    ${result}=    Split String To Characters    ${string}
    RETURN    ${result}

LPS.Split To Lines
    [Arguments]    ${string}    ${keep_ends}=False
    ${result}=    Split To Lines    ${string}    ${keep_ends}
    RETURN    ${result}

LPS.Strip String
    [Arguments]    ${string}    ${characters}=None
    ${result}=    Strip String    ${string}    ${characters}
    RETURN    ${result}