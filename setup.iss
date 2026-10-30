[Setup]
AppName=MstPull
AppVersion=1.0.9
DefaultDirName={autopf}\MstPull
DefaultGroupName=MstPull
UninstallDisplayIcon={app}\mstpull.exe
Compression=lzma2/max
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=MstPull_Setup_v1.0.9

[Files]
Source: "dist\mstpull.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MstPull"; Filename: "{app}\mstpull.exe"
Name: "{autodesktop}\MstPull"; Filename: "{app}\mstpull.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
