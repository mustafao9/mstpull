; MstPull - Dynamic & Legally Compliant Inno Setup Script
#ifndef MyAppVersion
  #define MyAppVersion "1.1.4"
#endif

[Setup]
AppName=MstPull
AppVersion={#MyAppVersion}
DefaultDirName={autopf64}\MstPull
DefaultGroupName=MstPull
UninstallDisplayIcon={app}\MstPull.exe
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=build_out
OutputBaseFilename=MstPull_Setup_v{#MyAppVersion}
SetupIconFile=icon.ico
ArchitecturesInstallIn64BitMode=x64

; Çoklu Dil Desteği & Zorunlu Lisans/KVKK Sözleşmesi
[Languages]
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"; LicenseFile: "license_tr.txt"
Name: "en"; MessagesFile: "compiler:Default.isl"; LicenseFile: "license_en.txt"

[Messages]
tr.WelcomeLabel2=Bu sihirbaz, MstPull Video ve MP3 İndirme uygulamasını bilgisayarınıza kuracaktır.%n%nÖne Çıkan Özellikler & Yapılandırma:%n- Yüksek Hızlı Multi-Stream İndirme Motoru%n- Dahili FFmpeg ile Kayıpsız MP3 / Ses Dönüştürme%n- Standart Windows Sistem Dizinleri (%APPDATA%\mstpull)%n- 64-Bit Mimarisine Uygun Doğrudan Program Files Kurulumu
en.WelcomeLabel2=This wizard will install MstPull Video and MP3 Downloader on your computer.%n%nKey Features & Configuration:%n- High-Speed Multi-Stream Download Engine%n- Lossless Audio Conversion with Embedded FFmpeg%n- Standard Windows System Directories (%APPDATA%\mstpull)%n- Direct Native 64-Bit Program Files Installation

[Files]
Source: "dist\MstPull\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "dist\mstpull.exe"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "locales\*"; DestDir: "{app}\locales"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\MstPull"; Filename: "{app}\MstPull.exe"; IconFilename: "{app}\MstPull.exe"; IconIndex: 0
Name: "{autodesktop}\MstPull"; Filename: "{app}\MstPull.exe"; Tasks: desktopicon; IconFilename: "{app}\MstPull.exe"; IconIndex: 0

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\mstpull"
