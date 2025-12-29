!define APP_NAME "DumbyDraw"
!define APP_VERSION "1.4.1"
!define COMPANY "ShanghaiTech University"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"

OutFile "DumbyDraw_Setup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Install"

  SetOutPath "$INSTDIR"

  ; Copy files
  File DumbyDraw_env.tar.gz
  File run_DumbyDraw.bat
  File icon.ico

  ; Create env directory
  CreateDirectory "$INSTDIR\env"

  ; Extract conda environment using Windows native tar
  nsExec::ExecToLog '"$SYSDIR\tar.exe" -xzf "$INSTDIR\DumbyDraw_env.tar.gz" -C "$INSTDIR\env"'

  ; Fix conda paths
  nsExec::ExecToLog '"$INSTDIR\env\Scripts\conda-unpack.exe"'

  ; Desktop shortcut
  CreateShortCut "$DESKTOP\DumbyDraw.lnk" "$INSTDIR\run_DumbyDraw.bat" "" "$INSTDIR\icon.ico"

  ; Start menu shortcut
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\DumbyDraw.lnk" "$INSTDIR\run_DumbyDraw.bat"

  ; Registry entry for uninstall
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${COMPANY}"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "Uninstall"

  ; Remove shortcuts
  Delete "$DESKTOP\DumbyDraw.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\DumbyDraw.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

  ; Remove installed files
  RMDir /r "$INSTDIR"

  ; Remove registry key
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd
