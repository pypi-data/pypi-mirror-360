*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic XML Steps
# ---------------------------------------------

*** Settings ***
Library    XML

*** Keywords ***
LPS.Add Element
    [Arguments]    ${parent}    ${element}
    Add Element    ${parent}    ${element}

LPS.Clear Element
    [Arguments]    ${element}
    Clear Element    ${element}

LPS.Copy Element
    [Arguments]    ${element}
    ${result}=    Copy Element    ${element}
    RETURN    ${result}

LPS.Element Attribute Should Be
    [Arguments]    ${element}    ${attribute}    ${expected}
    Element Attribute Should Be    ${element}    ${attribute}    ${expected}

LPS.Element Attribute Should Match
    [Arguments]    ${element}    ${attribute}    ${pattern}
    Element Attribute Should Match    ${element}    ${attribute}    ${pattern}

LPS.Element Should Exist
    [Arguments]    ${element}
    Element Should Exist    ${element}

LPS.Element Should Not Exist
    [Arguments]    ${element}
    Element Should Not Exist    ${element}

LPS.Element Should Not Have Attribute
    [Arguments]    ${element}    ${attribute}
    Element Should Not Have Attribute    ${element}    ${attribute}

LPS.Element Text Should Be
    [Arguments]    ${element}    ${expected}
    Element Text Should Be    ${element}    ${expected}

LPS.Element Text Should Match
    [Arguments]    ${element}    ${pattern}
    Element Text Should Match    ${element}    ${pattern}

LPS.Element To String
    [Arguments]    ${element}    ${with_tail}=False
    ${result}=    Element To String    ${element}    ${with_tail}
    RETURN    ${result}

LPS.Elements Should Be Equal
    [Arguments]    ${expected}    ${actual}
    Elements Should Be Equal    ${expected}    ${actual}

LPS.Elements Should Match
    [Arguments]    ${elements}    ${pattern}
    Elements Should Match    ${elements}    ${pattern}

LPS.Evaluate Xpath
    [Arguments]    ${element}    ${xpath}
    ${result}=    Evaluate Xpath    ${element}    ${xpath}
    RETURN    ${result}

LPS.Get Child Elements
    [Arguments]    ${element}
    ${result}=    Get Child Elements    ${element}
    RETURN    ${result}

LPS.Get Element
    [Arguments]    ${source}    ${xpath}
    ${result}=    Get Element    ${source}    ${xpath}
    RETURN    ${result}

LPS.Get Element Attribute
    [Arguments]    ${element}    ${attribute}
    ${result}=    Get Element Attribute    ${element}    ${attribute}
    RETURN    ${result}

LPS.Get Element Attributes
    [Arguments]    ${element}
    ${result}=    Get Element Attributes    ${element}
    RETURN    ${result}

LPS.Get Element Count
    [Arguments]    ${source}    ${xpath}
    ${result}=    Get Element Count    ${source}    ${xpath}
    RETURN    ${result}

LPS.Get Element Text
    [Arguments]    ${element}
    ${result}=    Get Element Text    ${element}
    RETURN    ${result}

LPS.Get Elements
    [Arguments]    ${source}    ${xpath}
    ${result}=    Get Elements    ${source}    ${xpath}
    RETURN    ${result}

LPS.Log Element
    [Arguments]    ${element}
    Log Element    ${element}

LPS.Parse Xml
    [Arguments]    ${xml}
    ${result}=    Parse Xml    ${xml}
    RETURN    ${result}

LPS.Remove Element
    [Arguments]    ${element}
    Remove Element    ${element}

LPS.Remove Element Attribute
    [Arguments]    ${element}    ${attribute}
    Remove Element Attribute    ${element}    ${attribute}

LPS.Remove Element Attributes
    [Arguments]    ${element}
    Remove Element Attributes    ${element}

LPS.Remove Elements
    [Arguments]    ${source}    ${xpath}
    Remove Elements    ${source}    ${xpath}

LPS.Remove Elements Attribute
    [Arguments]    ${source}    ${xpath}    ${attribute}
    Remove Elements Attribute    ${source}    ${xpath}    ${attribute}

LPS.Remove Elements Attributes
    [Arguments]    ${source}    ${xpath}
    Remove Elements Attributes    ${source}    ${xpath}

LPS.Save Xml
    [Arguments]    ${source}    ${path}
    Save Xml    ${source}    ${path}

LPS.Set Element Attribute
    [Arguments]    ${element}    ${attribute}    ${value}
    Set Element Attribute    ${element}    ${attribute}    ${value}

LPS.Set Element Tag
    [Arguments]    ${element}    ${tag}
    Set Element Tag    ${element}    ${tag}

LPS.Set Element Text
    [Arguments]    ${element}    ${text}
    Set Element Text    ${element}    ${text}

LPS.Set Elements Attribute
    [Arguments]    ${source}    ${xpath}    ${attribute}    ${value}
    Set Elements Attribute    ${source}    ${xpath}    ${attribute}    ${value}

LPS.Set Elements Tag
    [Arguments]    ${source}    ${xpath}    ${tag}
    Set Elements Tag    ${source}    ${xpath}    ${tag}

LPS.Set Elements Text
    [Arguments]    ${source}    ${xpath}    ${text}
    Set Elements Text    ${source}    ${xpath}    ${text}