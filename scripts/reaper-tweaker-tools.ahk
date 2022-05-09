SetDefaultMouseSpeed, 0

ChangeNextValue()
; on the Reaper Theme Tweak window, modify the next field, then return a code
; 0 - changed the field successfully
; 1 - stayed in main window, might not have changed a value
; 2 - some error happened
{
    WinGetActiveTitle, CurrentTitle
    if (!InStr(CurrentTitle, "Theme development/tweaker", false))
    {
        return 2
    }

    Send {Down}
    WinWaitNotActive, Theme development/tweaker, , 0.5
    WinGetActiveTitle, CurrentTitle
    if ErrorLevel
    {
        ; on the theme development window
        ; reset the error level
        ErrorLevel = 0
        return 1
    }
    else
    {
        ; on a new window
        if InStr(CurrentTitle, "Colour", false)
        {
            Click 20 170
            Click 40 307
        }
        else if InStr(CurrentTitle, "Theme Blend", false)
        {
            Click 205 46 2
            Send, 0.123
            Click 120 210
        }
        else if InStr(CurrentTitle, "Font", false)
        {
            Send, Comic Sans MS{Enter}
        }
        else
        {
            MsgBox, Unrecognised title: %CurrentTitle%
            return 2
        }

        ; wait for return to main window
        WinWaitActive, Theme development/tweaker, , 1
        if ErrorLevel
        {
            ErrorLevel = 0
            return 2
        }
        else
        {
            return 0
        }
    }
}

SaveTheme()
; on the Reaper Theme Tweak window, save the current theme
{
    WinGetActiveTitle, CurrentTitle
    if (!InStr(CurrentTitle, "Theme development/tweaker", false))
    {
        ErrorLevel = 1
        return
    }

    Click 435 45

    WinWaitActive, Save Theme as:, , 0.5

    Send, {Enter}
    Send, y

    WinWaitActive, Theme development/tweaker, , 0.5
    Send +{tab}
    Send +{tab}
}

#IfWinActive Theme development/tweaker
NumpadSub::
Loop
{
    rv := ChangeNextValue()
    if (rv = 1)
        break
    SaveTheme()
}
return

#IfWinActive Theme development/tweaker
NumpadAdd::
SaveTheme()
return

#IfWinActive
NumpadMult::
Reload
return