; ------------------------------------------------------------
; Instalador Backup MySQL Pro - Inno Setup
; Autor: ChatGPT
; ------------------------------------------------------------

[Setup]
AppName=Backup MySQL Pro
AppVersion=1.0
AppPublisher=TuNombre
AppPublisherURL=https://tusitio.com
DefaultDirName={pf}\BackupMySQLPro
DefaultGroupName=Backup MySQL Pro
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=dist_installer
OutputBaseFilename=BackupMySQLPro_Installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; (Opcional) Ícono del instalador
; SetupIconFile=icon.ico

[Files]
; === ARCHIVO PRINCIPAL EXE (GENERADO CON PYINSTALLER) ===
Source: "C:\Users\mauri\OneDrive\Escritorio\miproyecto\dist\backup_app.exe"; DestDir: "{app}"; Flags: ignoreversion

; === ARCHIVO copias.json PARA GUARDAR EL HISTORIAL ===
Source: "C:\Users\mauri\OneDrive\Escritorio\miproyecto\copias.json"; DestDir: "{app}"; Flags: ignoreversion

; (Opcional) Ícono del programa
; Source: "C:\Users\mauri\OneDrive\Escritorio\miproyecto\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Icono en el escritorio
Name: "{userdesktop}\Backup MySQL Pro"; Filename: "{app}\backup_app.exe"

; Icono en el menú inicio
Name: "{group}\Backup MySQL Pro"; Filename: "{app}\backup_app.exe"

; Icono para desinstalar
Name: "{group}\Desinstalar Backup MySQL Pro"; Filename: "{uninstallexe}"
