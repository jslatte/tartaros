; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{44AD0631-36FF-4A3D-926D-DD17B9138AEA}
AppName=Hekate
AppVersion=1.0.16
;AppVerName=Hekate
AppPublisher=Apollo Video Technology, LLC.
AppPublisherURL=www.apollovideo.com
AppSupportURL=www.apollovideo.com
AppUpdatesURL=www.apollovideo.com
DefaultDirName={pf}\Tartaros\Hekate
DefaultGroupName=Tartaros\Hekate
AllowNoIcons=yes
OutputBaseFilename=Install Hekate
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Temp52\Tartaros\artifacts\Hekate\dist\hekate.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Temp52\Tartaros\artifacts\Hekate\dist\hekate.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Temp52\Tartaros\artifacts\Hekate\build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Temp52\Tartaros\artifacts\Hekate\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Hekate"; Filename: "{app}\hekate.bat"; IconFilename: "{app}\hekate.ico"
Name: "{group}\{cm:UninstallProgram,Hekate}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Hekate"; Filename: "{app}\hekate.bat"; Tasks: desktopicon; IconFilename: "{app}\hekate.ico"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Hekate"; Filename: "{app}\hekate.bat"; Tasks: quicklaunchicon; IconFilename: "{app}\hekate.ico"

[Run]
Filename: "{app}\hekate.bat"; Description: "{cm:LaunchProgram,Hekate}"; Flags: nowait postinstall skipifsilent runascurrentuser shellexec

