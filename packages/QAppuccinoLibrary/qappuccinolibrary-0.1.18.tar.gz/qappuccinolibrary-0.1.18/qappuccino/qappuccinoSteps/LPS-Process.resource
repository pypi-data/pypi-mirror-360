*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic Process Steps
# ---------------------------------------------

*** Settings ***
Library    Process

*** Keywords ***
LPS.Get Process Id
    [Arguments]    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    ${pid}=    Get Process Id    ${handle}
    RETURN    ${pid}

LPS.Get Process Object
    [Arguments]    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    ${object}=    Get Process Object    ${handle}
    RETURN    ${object}

LPS.Get Process Result
    [Arguments]    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    ${result}=    Get Process Result    ${handle}
    RETURN    ${result}

LPS.Is Process Running
    [Arguments]    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    ${status}=    Is Process Running    ${handle}
    RETURN    ${status}

LPS.Join Command Line
    [Arguments]    @{command}
    ${joined}=    Join Command Line    @{command}
    RETURN    ${joined}

LPS.Process Should Be Running
    [Arguments]    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    Process Should Be Running    ${handle}

LPS.Process Should Be Stopped
    [Arguments]    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    Process Should Be Stopped    ${handle}

LPS.Run Process
    [Arguments]    ${command}    ${arguments}=None    ${cwd}=None    ${env}=None    ${timeout}=None
    ${arguments}=    Run Keyword If    '${arguments}'=='None'    Create List    ELSE    Set Variable    ${arguments}
    ${cwd}=         Run Keyword If    '${cwd}'=='None'         Set Variable    ${None}    ELSE    Set Variable    ${cwd}
    ${env}=         Run Keyword If    '${env}'=='None'         Set Variable    ${None}    ELSE    Set Variable    ${env}
    ${timeout}=     Run Keyword If    '${timeout}'=='None'     Set Variable    ${None}    ELSE    Set Variable    ${timeout}
    ${result}=    Run Process    ${command}    ${arguments}    cwd=${cwd}    env=${env}    timeout=${timeout}    shell=True
    RETURN    ${result}

LPS.Send Signal To Process
    [Arguments]    ${signal}    ${handle}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    Send Signal To Process    ${signal}    ${handle}

LPS.Split Command Line
    [Arguments]    ${command}
    ${split}=    Split Command Line    ${command}
    RETURN    ${split}

LPS.Start Process
    [Arguments]    ${command}    ${arguments}=None    ${cwd}=None    ${env}=None    ${alias}=None    ${stdout}=None    ${stderr}=None    ${shell}=True
    ${arguments}=    Run Keyword If    '${arguments}'=='None'    Create List    ELSE    Set Variable    ${arguments}
    ${cwd}=         Run Keyword If    '${cwd}'=='None'         Set Variable    ${None}    ELSE    Set Variable    ${cwd}
    ${env}=         Run Keyword If    '${env}'=='None'         Set Variable    ${None}    ELSE    Set Variable    ${env}
    ${alias}=       Run Keyword If    '${alias}'=='None'       Set Variable    ${None}    ELSE    Set Variable    ${alias}
    ${stdout}=      Run Keyword If    '${stdout}'=='None'      Set Variable    ${None}    ELSE    Set Variable    ${stdout}
    ${stderr}=      Run Keyword If    '${stderr}'=='None'      Set Variable    ${None}    ELSE    Set Variable    ${stderr}
    ${handle}=    Start Process    ${command}    ${arguments}    cwd=${cwd}    env=${env}    alias=${alias}    stdout=${stdout}    stderr=${stderr}    shell=${shell}
    RETURN    ${handle}

LPS.Switch Process
    [Arguments]    ${handle}
    Switch Process    ${handle}

LPS.Terminate All Processes
    Terminate All Processes

LPS.Terminate Process
    [Arguments]    ${handle}=None    ${graceful}=False
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    Terminate Process    ${handle}    ${graceful}

LPS.Wait For Process
    [Arguments]    ${handle}=None    ${timeout}=None
    ${handle}=    Run Keyword If    '${handle}'=='None'    Set Variable    ${None}    ELSE    Set Variable    ${handle}
    ${timeout}=   Run Keyword If    '${timeout}'=='None'   Set Variable    ${None}    ELSE    Set Variable    ${timeout}
    ${result}=    Wait For Process    ${handle}    ${timeout}
    RETURN    ${result}