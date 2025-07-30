*** Settings ***
Documentation       Test robotframework-rzsbc PrintText functions

Library             robotframework_rzsbc.PrintText.PrintText


*** Test Cases ***
Test Echo Hello World
    [Documentation]    Test the echo_hello_world function
    ${result}=    Echo Hello World
    Should Be Equal    ${result}    Hello World
    Log    Function returned: ${result}

Test Print Text
    [Documentation]    Test the print_text function
    ${result}=    Print Text    Testing custom message
    Should Be Equal    ${result}    Testing custom message
    Log    Function returned: ${result}

Test Get Current Time
    [Documentation]    Test the get_current_time function
    ${time}=    Get Current Time
    Should Not Be Empty    ${time}
    Should Contain    ${time}    T
    Log    Current time: ${time}

Test Add Numbers
    [Documentation]    Test the add_numbers function
    ${sum}=    Add Numbers    5    3
    Should Be Equal As Numbers    ${sum}    8
    Log    Addition result: ${sum}

Test Multiply Text
    [Documentation]    Test the multiply_text function
    ${repeated}=    Multiply Text    Hello    3
    Should Be Equal    ${repeated}    HelloHelloHello
    Log    Repeated text: ${repeated}

Test Format Message
    [Documentation]    Test the format_message function
    ${message}=    Format Message    Hello {} from {}    World    RZSBC
    Should Be Equal    ${message}    Hello World from RZSBC
    Log    Formatted message: ${message}
