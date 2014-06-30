; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{F715EF54-D289-4853-A0F5-5D4477AE8EC9}
AppName=Erinyes
AppVersion=1.1.1
;AppVerName=Erinyes 1.0.0
AppPublisher=Apollo Video Technology, LLC.
DefaultDirName={pf}\Tartaros\Erinyes
DefaultGroupName=Erinyes
AllowNoIcons=yes
OutputDir=C:\Temp52\Tartaros\Output
OutputBaseFilename=Install Erinyes
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Temp52\Tartaros\artifacts\Erinyes\dist\Erinyes.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Temp52\Tartaros\artifacts\Erinyes\build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Temp52\Tartaros\artifacts\Erinyes\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Erinyes"; Filename: "{app}\Erinyes.exe"; IconFilename: "{app}\erinyes.ico"
Name: "{group}\{cm:UninstallProgram,Erinyes}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Erinyes"; Filename: "{app}\Erinyes.exe"; Tasks: desktopicon; IconFilename: "{app}\erinyes.ico"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Erinyes"; Filename: "{app}\Erinyes.exe"; Tasks: quicklaunchicon; IconFilename: "{app}\erinyes.ico"

[Run]
Filename: "{app}\Erinyes.exe"; Description: "{cm:LaunchProgram,Erinyes}"; Flags: nowait postinstall skipifsilent

