*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic DatabaseLibrary Steps
# ---------------------------------------------

*** Settings ***
Library

*** Keywords ***
LPS.Call Method
    [Arguments]    ${object}    ${method_name}    @{args}
    ${result}=    Call Method    ${object}    ${method_name}    @{args}
    RETURN    ${result}

LPS.Catenate
    [Arguments]    ${separator}=    @{items}
    ${result}=    Catenate    SEPARATOR=${separator}    @{items}
    RETURN    ${result}

LPS.Comment
    [Arguments]    @{comments}
    Comment    @{comments}

LPS.Continue For Loop
    Continue For Loop

LPS.Continue For Loop If
    [Arguments]    ${condition}
    Continue For Loop If    ${condition}

LPS.Convert To Binary
    [Arguments]    ${item}
    ${result}=    Convert To Binary    ${item}
    RETURN    ${result}

LPS.Convert To Boolean
    [Arguments]    ${item}
    ${result}=    Convert To Boolean    ${item}
    RETURN    ${result}

LPS.Convert To Bytes
    [Arguments]    ${item}    ${encoding}=UTF-8
    ${result}=    Convert To Bytes    ${item}    encoding=${encoding}
    RETURN    ${result}

LPS.Convert To Hex
    [Arguments]    ${item}
    ${result}=    Convert To Hex    ${item}
    RETURN    ${result}

LPS.Convert To Integer
    [Arguments]    ${item}    ${base}=10
    ${result}=    Convert To Integer    ${item}    base=${base}
    RETURN    ${result}

LPS.Convert To Number
    [Arguments]    ${item}
    ${result}=    Convert To Number    ${item}
    RETURN    ${result}

LPS.Convert To Octal
    [Arguments]    ${item}
    ${result}=    Convert To Octal    ${item}
    RETURN    ${result}

LPS.Convert To String
    [Arguments]    ${item}
    ${result}=    Convert To String    ${item}
    RETURN    ${result}

LPS.Create Dictionary
    [Arguments]    @{items}
    ${result}=    Create Dictionary    @{items}
    RETURN    ${result}

LPS.Create List
    [Arguments]    @{items}
    ${result}=    Create List    @{items}
    RETURN    ${result}

LPS.Evaluate
    [Arguments]    ${expression}    ${modules}=    ${namespace}=None
    ${result}=    Evaluate    ${expression}    modules=${modules}    namespace=${namespace}
    RETURN    ${result}

LPS.Exit For Loop
    Exit For Loop

LPS.Exit For Loop If
    [Arguments]    ${condition}
    Exit For Loop If    ${condition}

LPS.Fail
    [Arguments]    ${message}=Test failed
    Fail    ${message}

LPS.Fatal Error
    [Arguments]    ${message}=Fatal error
    Fatal Error    ${message}

LPS.Get Length
    [Arguments]    ${item}
    ${result}=    Get Length    ${item}
    RETURN    ${result}

LPS.Get Library Instance
    [Arguments]    ${name}
    ${result}=    Get Library Instance    ${name}
    RETURN    ${result}

LPS.Get Time
    [Arguments]    ${format}=timestamp    ${time}=NOW
    ${result}=    Get Time    ${format}    ${time}
    RETURN    ${result}

LPS.Get Variable Value
    [Arguments]    ${variable}    ${default_value}=None
    ${result}=    Get Variable Value    ${variable}    ${default_value}
    RETURN    ${result}

LPS.Get Variables
    ${result}=    Get Variables
    RETURN    ${result}

LPS.Import Resource
    [Arguments]    ${path}
    Import Resource    ${path}

LPS.Import Variables
    [Arguments]    ${path}    @{args}
    Import Variables    ${path}    @{args}

LPS.Keyword Should Exist
    [Arguments]    ${name}
    Keyword Should Exist    ${name}

LPS.Log
    [Arguments]    ${message}    ${level}=INFO    ${console}=False
    Log    ${message}    ${level}    ${console}

LPS.Log Many
    [Arguments]    @{messages}
    Log Many    @{messages}

LPS.Log To Console
    [Arguments]    ${message}    ${newline}=True
    Log To Console    ${message}    ${newline}

LPS.Log Variables
    [Arguments]    ${level}=INFO
    Log Variables    ${level}

LPS.No Operation
    No Operation

LPS.Pass Execution
    [Arguments]    ${message}=Test execution passed
    Pass Execution    ${message}

LPS.Pass Execution If
    [Arguments]    ${condition}    ${message}=Test execution passed
    Pass Execution If    ${condition}    ${message}

LPS.Regexp Escape
    [Arguments]    ${string}
    ${result}=    Regexp Escape    ${string}
    RETURN    ${result}

LPS.Reload Library
    [Arguments]    ${name}    @{args}
    Reload Library    ${name}    @{args}

LPS.Remove Tags
    [Arguments]    @{tags}
    Remove Tags    @{tags}

LPS.Repeat Keyword
    [Arguments]    ${times}    ${name}    @{args}
    Repeat Keyword    ${times}    ${name}    @{args}

LPS.Replace Variables
    [Arguments]    ${string}
    ${result}=    Replace Variables    ${string}
    RETURN    ${result}

LPS.Reset Log Level
    Reset Log Level

LPS.Return From Keyword
    [Arguments]    ${value}=None
    Return From Keyword    ${value}

LPS.Return From Keyword If
    [Arguments]    ${condition}    ${value}=None
    Return From Keyword If    ${condition}    ${value}

LPS.Run Keyword
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Continue On Failure
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword And Continue On Failure    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Expect Error
    [Arguments]    ${expected_error}    ${name}    @{args}
    ${result}=    Run Keyword And Expect Error    ${expected_error}    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Ignore Error
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword And Ignore Error    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Return
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword And Return    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Return If
    [Arguments]    ${condition}    ${name}    @{args}
    ${result}=    Run Keyword And Return If    ${condition}    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Return Status
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword And Return Status    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword And Warn On Failure
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword And Warn On Failure    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword If
    [Arguments]    ${condition}    ${name}    @{args}
    ${result}=    Run Keyword If    ${condition}    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword If All Tests Passed
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword If All Tests Passed    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword If Any Tests Failed
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword If Any Tests Failed    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword If Test Failed
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword If Test Failed    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword If Test Passed
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword If Test Passed    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword If Timeout Occurred
    [Arguments]    ${name}    @{args}
    ${result}=    Run Keyword If Timeout Occurred    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keyword Unless
    [Arguments]    ${condition}    ${name}    @{args}
    ${result}=    Run Keyword Unless    ${condition}    ${name}    @{args}
    RETURN    ${result}

LPS.Run Keywords
    [Arguments]    @{keywords}
    Run Keywords    @{keywords}

LPS.Set Global Variable
    [Arguments]    ${value}    ${name}=
    ${result}=    Set Global Variable    ${value}    ${name}
    RETURN    ${result}

LPS.Set Library Search Order
    [Arguments]    @{libraries}
    Set Library Search Order    @{libraries}

LPS.Set Local Variable
    [Arguments]    ${value}    ${name}=
    ${result}=    Set Local Variable    ${value}    ${name}
    RETURN    ${result}

LPS.Set Log Level
    [Arguments]    ${level}
    Set Log Level    ${level}

LPS.Set Suite Documentation
    [Arguments]    ${documentation}
    Set Suite Documentation    ${documentation}

LPS.Set Suite Metadata
    [Arguments]    ${name}    ${value}
    Set Suite Metadata    ${name}    ${value}

LPS.Set Suite Variable
    [Arguments]    ${value}    ${name}=
    ${result}=    Set Suite Variable    ${value}    ${name}
    RETURN    ${result}

LPS.Set Tags
    [Arguments]    @{tags}
    Set Tags    @{tags}

LPS.Set Task Variable
    [Arguments]    ${value}    ${name}=
    ${result}=    Set Task Variable    ${value}    ${name}
    RETURN    ${result}

LPS.Set Test Documentation
    [Arguments]    ${documentation}
    Set Test Documentation    ${documentation}

LPS.Set Test Message
    [Arguments]    ${message}    ${level}=FAIL
    Set Test Message    ${message}    ${level}

LPS.Set Test Variable
    [Arguments]    ${value}    ${name}=
    ${result}=    Set Test Variable    ${value}    ${name}
    RETURN    ${result}

LPS.Set Variable
    [Arguments]    ${value}    ${name}=
    ${result}=    Set Variable    ${value}    ${name}
    RETURN    ${result}

LPS.Set Variable If
    [Arguments]    ${condition}    ${true_value}    ${false_value}    ${name}=
    ${result}=    Set Variable If    ${condition}    ${true_value}    ${false_value}    ${name}
    RETURN    ${result}

LPS.Should Be Empty
    [Arguments]    ${item}    ${msg}=
    Should Be Empty    ${item}    ${msg}

LPS.Should Be Equal
    [Arguments]    ${first}    ${second}    ${msg}=    ${values}=True
    Should Be Equal    ${first}    ${second}    ${msg}    ${values}

LPS.Should Be Equal As Integers
    [Arguments]    ${first}    ${second}    ${msg}=
    Should Be Equal As Integers    ${first}    ${second}    ${msg}

LPS.Should Be Equal As Numbers
    [Arguments]    ${first}    ${second}    ${msg}=    ${precision}=1e-6
    Should Be Equal As Numbers    ${first}    ${second}    ${msg}    ${precision}

LPS.Should Be Equal As Strings
    [Arguments]    ${first}    ${second}    ${msg}=    ${ignore_case}=False
    Should Be Equal As Strings    ${first}    ${second}    ${msg}    ${ignore_case}

LPS.Should Be True
    [Arguments]    ${condition}    ${msg}=
    Should Be True    ${condition}    ${msg}

LPS.Should Contain
    [Arguments]    ${container}    ${item}    ${msg}=    ${values}=True
    Should Contain    ${container}    ${item}    ${msg}    ${values}

LPS.Should Contain Any
    [Arguments]    ${container}    @{items}
    Should Contain Any    ${container}    @{items}

LPS.Should Contain X Times
    [Arguments]    ${container}    ${item}    ${count}    ${msg}=    ${values}=True
    Should Contain X Times    ${container}    ${item}    ${count}    ${msg}    ${values}

LPS.Should End With
    [Arguments]    ${string}    ${suffix}    ${msg}=    ${ignore_case}=False
    Should End With    ${string}    ${suffix}    ${msg}    ${ignore_case}

LPS.Should Match
    [Arguments]    ${string}    ${pattern}    ${msg}=    ${ignore_case}=False
    Should Match    ${string}    ${pattern}    ${msg}    ${ignore_case}

LPS.Should Match Regexp
    [Arguments]    ${string}    ${pattern}    ${msg}=
    Should Match Regexp    ${string}    ${pattern}    ${msg}

LPS.Should Not Be Empty
    [Arguments]    ${item}    ${msg}=
    Should Not Be Empty    ${item}    ${msg}

LPS.Should Not Be Equal
    [Arguments]    ${first}    ${second}    ${msg}=    ${values}=True
    Should Not Be Equal    ${first}    ${second}    ${msg}    ${values}

LPS.Should Not Be Equal As Integers
    [Arguments]    ${first}    ${second}    ${msg}=
    Should Not Be Equal As Integers    ${first}    ${second}    ${msg}

LPS.Should Not Be Equal As Numbers
    [Arguments]    ${first}    ${second}    ${msg}=    ${precision}=1e-6
    Should Not Be Equal As Numbers    ${first}    ${second}    ${msg}    ${precision}

LPS.Should Not Be Equal As Strings
    [Arguments]    ${first}    ${second}    ${msg}=    ${ignore_case}=False
    Should Not Be Equal As Strings    ${first}    ${second}    ${msg}    ${ignore_case}

LPS.Should Not Be True
    [Arguments]    ${condition}    ${msg}=
    Should Not Be True    ${condition}    ${msg}

LPS.Should Not Contain
    [Arguments]    ${container}    ${item}    ${msg}=    ${values}=True
    Should Not Contain    ${container}    ${item}    ${msg}    ${values}

LPS.Should Not Contain Any
    [Arguments]    ${container}    @{items}
    Should Not Contain Any    ${container}    @{items}

LPS.Should Not End With
    [Arguments]    ${string}    ${suffix}    ${msg}=    ${ignore_case}=False
    Should Not End With    ${string}    ${suffix}    ${msg}    ${ignore_case}

LPS.Should Not Match
    [Arguments]    ${string}    ${pattern}    ${msg}=    ${ignore_case}=False
    Should Not Match    ${string}    ${pattern}    ${msg}    ${ignore_case}

LPS.Should Not Match Regexp
    [Arguments]    ${string}    ${pattern}    ${msg}=
    Should Not Match Regexp    ${string}    ${pattern}    ${msg}

LPS.Should Not Start With
    [Arguments]    ${string}    ${prefix}    ${msg}=    ${ignore_case}=False
    Should Not Start With    ${string}    ${prefix}    ${msg}    ${ignore_case}

LPS.Should Start With
    [Arguments]    ${string}    ${prefix}    ${msg}=    ${ignore_case}=False
    Should Start With    ${string}    ${prefix}    ${msg}    ${ignore_case}

LPS.Skip
    [Arguments]    ${message}=Skipped in LPS
    Skip    ${message}

LPS.Skip If
    [Arguments]    ${condition}    ${message}=Skipped in LPS
    Skip If    ${condition}    ${message}

LPS.Sleep
    [Arguments]    ${seconds}    ${reason}=
    Sleep    ${seconds}    ${reason}

LPS.Variable Should Exist
    [Arguments]    ${name}    ${msg}=
    Variable Should Exist    ${name}    ${msg}

LPS.Variable Should Not Exist
    [Arguments]    ${name}    ${msg}=
    Variable Should Not Exist    ${name}    ${msg}

LPS.Wait Until Keyword Succeeds
    [Arguments]    ${retry_interval}    ${timeout}    ${name}    @{args}
    Wait Until Keyword Succeeds    ${retry_interval}    ${timeout}    ${name}    @{args}
