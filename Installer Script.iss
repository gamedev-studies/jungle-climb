; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Jungle Climb"
#define MyAppVersion "1.0"
#define MyAppPublisher "Elijah Lopez"
#define MyAppURL "https://elijahlopez.herokuapp.com/"
#define MyAppExeName "main.exe"
#define MyAppNewName "Jungle Climb.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{46078D58-2849-4CDD-9A51-A2C5F06F2B87}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; The [Icons] "quicklaunchicon" entry uses {userappdata} but its [Tasks] entry has a proper IsAdminInstallMode Check.
UsedUserAreasWarning=no
; Remove the following line to run in administrative install mode (install for all users.)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
OutputDir={#SourcePath}\dist
OutputBaseFilename=Jungle Climb Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile="Resources\Jungle Climb Icon.ico"
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "{#SourcePath}\build\exe.win-amd64-3.6\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\api-ms-win-crt-heap-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\api-ms-win-crt-locale-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\api-ms-win-crt-math-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\api-ms-win-crt-runtime-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\api-ms-win-crt-stdio-l1-1-0.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\jungle tileset.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\python36.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\build\exe.win-amd64-3.6\Character\*"; DestDir: "{app}\Character"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\build\exe.win-amd64-3.6\Fonts\*"; DestDir: "{app}\Fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\build\exe.win-amd64-3.6\Jungle Asset Pack\*"; DestDir: "{app}\Jungle Asset Pack"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\build\exe.win-amd64-3.6\lib\*"; DestDir: "{app}\lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\build\exe.win-amd64-3.6\sprites\*"; DestDir: "{app}\sprites"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\build\exe.win-amd64-3.6\tcl\*"; DestDir: "{app}\tcl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#SourcePath}\build\exe.win-amd64-3.6\tk\*"; DestDir: "{app}\tk"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
