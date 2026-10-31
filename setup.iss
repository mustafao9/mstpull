; Eğer dışarıdan MyAppVersion tanımlanmamışsa varsayılan olarak bu değeri kullanır
#ifndef MyAppVersion
  #define MyAppVersion "1.1.2"
#endif

[Setup]
AppName=MstPull
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\MstPull
DefaultGroupName=MstPull
UninstallDisplayIcon={app}\mstpull.exe
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=.
OutputBaseFilename=MstPull_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico

[Files]
Source: "dist\mstpull.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\MstPull"; Filename: "{app}\mstpull.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\MstPull"; Filename: "{app}\mstpull.exe"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
