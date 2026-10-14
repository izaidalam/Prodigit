Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\Zaid alam\Projects\Prodigit"
WshShell.Run """C:\Python313\pythonw.exe"" ""c:\Users\Zaid alam\Projects\Prodigit\main.py""", 0, False
