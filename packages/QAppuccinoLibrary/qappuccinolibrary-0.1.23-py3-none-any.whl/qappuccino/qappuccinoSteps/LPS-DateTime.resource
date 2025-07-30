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
Library    DateTime

*** Keywords ***
LPS.Get Current Date
    [Arguments]    ${result_format}=%Y-%m-%d    ${increment}=0 days
    ${date}=    Get Current Date    result_format=${result_format}    increment=${increment}
    RETURN    ${date}

LPS.Add Time To Date
    [Arguments]    ${date}    ${increment}=0 days    ${result_format}=%Y-%m-%d
    ${new_date}=    Add Time To Date    ${date}    ${increment}    result_format=${result_format}
    RETURN    ${new_date}

LPS.Add Time To Time
    [Arguments]    ${time}    ${increment}=0 seconds    ${result_format}=%H:%M:%S
    ${new_time}=    Add Time To Time    ${time}    ${increment}    result_format=${result_format}
    RETURN    ${new_time}

LPS.Convert Date
    [Arguments]    ${date}    ${date_format_from}=%Y-%m-%d    ${date_format_to}=%d-%m-%Y
    ${converted}=    Convert Date    ${date}    ${date_format_from}=${date_format_from}    ${date_format_to}=${date_format_to}
    RETURN    ${converted}

LPS.Convert Time
    [Arguments]    ${time}    ${time_format_from}=%H:%M:%S    ${time_format_to}=%I:%M %p
    ${converted}=    Convert Time    ${time}    ${time_format_from}=${time_format_from}    ${time_format_to}=${time_format_to}
    RETURN    ${converted}

LPS.Subtract Date From Date
    [Arguments]    ${date1}    ${date2}    ${date_format}=%Y-%m-%d
    ${diff}=    Subtract Date From Date    ${date1}    ${date2}    date_format=${date_format}
    RETURN    ${diff}

LPS.Subtract Time From Date
    [Arguments]    ${date}    ${time}    ${result_format}=%Y-%m-%d %H:%M:%S
    ${result}=    Subtract Time From Date    ${date}    ${time}    result_format=${result_format}
    RETURN    ${result}

LPS.Subtract Time From Time
    [Arguments]    ${time1}    ${time2}    ${result_format}=%H:%M:%S
    ${diff}=    Subtract Time From Time    ${time1}    ${time2}    result_format=${result_format}
    RETURN    ${diff}
