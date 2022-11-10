; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "PyPigPlayer"
#define MyAppVersion "v2.5"
#define MyAppPublisher "ganpig"
#define MyAppURL "https://github.com/PyPigStudio/PyPigPlayer"
#define MyAppExeName "PyPigPlayer.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{4AE433AA-330B-49F0-8328-303DBE515F22}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputDir=D:\Programs\Python\PyPigPlayer\Archives\{#MyAppVersion}
OutputBaseFilename=PyPigPlayer-{#MyAppVersion}-windows-setup
SetupIconFile=D:\Programs\Python\PyPigPlayer\Resources\logo.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone

[Files]
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\PyPigPlayer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\PyPigPlayer.pyz"; DestDir: "{app}"; Flags: ignoreversion    
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\config.ini"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\Fonts\*"; DestDir: "{app}\Fonts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\Python\*"; DestDir: "{app}\Python"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\Themes\*"; DestDir: "{app}\Themes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\Programs\Python\PyPigPlayer\Building\PyPigPlayer\Tools\*"; DestDir: "{app}\Tools"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

