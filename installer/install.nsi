!define APP_NAME "DumbDrawPhD"
!define APP_VERSION "1.0.0"
!define COMPANY "YourCompany"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_NAME}"

OutFile "DumbDrawPhD_Setup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Install"

  SetOutPath "$INSTDIR"

  ; Copy files
  File DumbDrawPhD_env.tar.gz
  File run_DumbDrawPhD.bat
  File icon.ico

  ; Create env directory
  CreateDirectory "$INSTDIR\env"

  ; Extract conda environment using Windows native tar
  nsExec::ExecToLog '"$SYSDIR\tar.exe" -xzf "$INSTDIR\DumbDrawPhD_env.tar.gz" -C "$INSTDIR\env"'

  ; Fix conda paths
  nsExec::ExecToLog '"$INSTDIR\env\Scripts\conda-unpack.exe"'

  ; Desktop shortcut
  CreateShortCut "$DESKTOP\DumbDrawPhD.lnk" "$INSTDIR\run_DumbDrawPhD.bat" "" "$INSTDIR\icon.ico"

  ; Start menu shortcut
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\DumbDrawPhD.lnk" "$INSTDIR\run_DumbDrawPhD.bat"

  ; Registry entry for uninstall
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${COMPANY}"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

Section "Uninstall"

  ; Remove shortcuts
  Delete "$DESKTOP\DumbDrawPhD.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\DumbDrawPhD.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"

  ; Remove installed files
  RMDir /r "$INSTDIR"

  ; Remove registry key
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

SectionEnd
