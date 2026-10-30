# Bangla Voice Typing — Cloud Build Kit

This repository builds a Windows `.exe` using GitHub Actions. It does **not** contain a prebuilt installer.

## Features
- Record Bengali speech from the selected/default microphone.
- Convert speech to Bengali text using Google's online speech recognition service (`bn-BD`).
- Copy or clear the resulting text.

## Build on GitHub
1. Upload the **contents** of this folder to the root of your GitHub repository (not the ZIP file itself).
2. Commit the files to the `main` branch.
3. Open the repository's **Actions** tab.
4. Select **Build Windows App** and click **Run workflow** if it did not start automatically.
5. Wait for the workflow to finish successfully.
6. Open the completed run and download the `BanglaVoiceTyping-Windows` artifact.
7. Extract the downloaded artifact ZIP. Run `BanglaVoiceTyping.exe` on Windows.

## Notes
- An internet connection is required for speech recognition.
- Microphone permission must be enabled in Windows.
- Speech is sent to Google's online recognition service. Do not dictate confidential information.
- This is an initial test build, not a signed installer. Windows SmartScreen may show a warning.
- The app currently creates a portable `.exe`, not a Setup installer.
