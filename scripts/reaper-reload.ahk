; set title matching behaviour
; 2 = title contains the text anywhere inside it
SetTitleMatchMode 2

; find the Reaper window, using the following criteria:
; - title contains "REAPER"
; - process name is "reaper.exe"
; - window class is "REAPERwnd" (found with AHK Window Spy)
hwnd := WinGetID("REAPER ahk_exe reaper.exe ahk_class REAPERwnd")
if !hwnd {
  throw Error("Reaper window not found")
}

; send Ctrl+F5 to Reaper
ControlSend "^{F5}", hwnd
