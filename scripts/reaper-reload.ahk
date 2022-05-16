; contain WinTitle anywhere inside it to be a match
SetTitleMatchMode 2

SearchTitle := "REAPER v6.57"

; make Reaper active
WinActivate, %SearchTitle%

; wait for Reaper to be active for real
WinWaitActive %SearchTitle%, , 0.2
if ErrorLevel
{
  MsgBox Unable to activate window '%SearchTitle%'. Stopping script...
  Exit 1
}

Send ^{F5}{Alt Down}{Tab}{Alt Up}
