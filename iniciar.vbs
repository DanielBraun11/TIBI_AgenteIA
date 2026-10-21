' MasOrange TV Agent (TIBI) — Lanzador silencioso
' Arranca el servidor en segundo plano y abre el navegador automaticamente.

Dim shell, scriptDir, batPath

Set shell = CreateObject("WScript.Shell")

' Directorio donde esta este script
scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
batPath    = scriptDir & "iniciar.bat"

' Verificar que el entorno virtual existe
If Not CreateObject("Scripting.FileSystemObject").FolderExists(scriptDir & ".venv") Then
    MsgBox "El entorno virtual no existe." & vbCrLf & vbCrLf & _
           "Ejecuta primero 'instalar.bat' para configurar el agente.", _
           vbExclamation, "MasOrange TV Agent — TIBI"
    WScript.Quit 1
End If

' Arrancar el servidor (ventana minimizada, sin bloquear)
shell.Run "cmd /c """ & batPath & """", 2, False

' Esperar unos segundos a que el servidor arranque
WScript.Sleep 4000

' Abrir el navegador
shell.Run "http://127.0.0.1:8000", 1, False
