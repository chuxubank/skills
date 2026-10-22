---
name: apk-device-install
description: >-
  Install and verify an Android APK on one authorized device, including OEM USB
  installer risk prompts and UI automation helper failures. Use when
  adb install is rejected, an APK transfer times out, or a
  device-side install confirmation must be completed before QA.
---

# Android APK Device Install

Use after the target Android device is awake and unlocked. For a locked device,
load `adb-device-unlock` first. For UI interaction, follow the available device
automation tool's instructions. This workflow was verified on a vivo phone with
OriginOS; OEM screens and commands can differ.

## Bind the package and device

Run `adb devices -l`, select one intended serial, and pass `-s "$SERIAL"` to
every adb command. Confirm the APK path, package identity, and expected build
before installation. Use `install -r` to preserve app data; uninstall only when
the user explicitly authorizes data removal. Do not run a helper that installs
to every connected device.

## Install and retain the result

For a large APK, use a direct serial-pinned adb install to avoid automation
wrapper timeouts:

```bash
adb -s "$SERIAL" install -r "$APK" > "$INSTALL_LOG" 2>&1 &
INSTALL_PID=$!
wait "$INSTALL_PID"
```

Keep the device unlocked during the transfer. Inspect `$INSTALL_LOG` for
`Success` or the exact `INSTALL_FAILED_*` reason. Verify the package exists:

```bash
adb -s "$SERIAL" shell pm path "$PACKAGE"
```

If the install returns `INSTALL_FAILED_ABORTED: User rejected permissions`,
bring the device installer to the foreground and inspect the actual prompt
using the element-first flow below.

## Complete the OEM installer prompt

Use the available device automation tool on the same device. Prefer its
structured UI elements and element-based actions, using current refs or
id/label/role selectors as supported. Continue from the action's returned UI
state or diff when available; request a fresh element tree only when needed
to identify the next target. Use the tool's wait or completion mechanism to
allow UI transitions to settle.

If the tool cannot expose the installer UI (for example, its helper APK is
rejected), use serial-pinned `adb shell uiautomator dump` for text and bounds.
Capture a screenshot only when structured UI data is unavailable, sparse, or
insufficient to identify the prompt safely; inspect that image before using
coordinates. Return to element-based actions once structured UI data is usable.
Full-screen screenshots are not a routine step or a per-tap requirement.

On the observed vivo flow, the installer showed the verified app name, version,
size, an external-source risk notice, an acknowledgement checkbox, and a
Continue installation button. Before tapping, check that the app identity and
risk notice match the intended debug or release artifact. Then:

1. Select the acknowledgement checkbox if the user has authorized this debug
   installation and the notice is expected.
2. Tap Continue installation.
3. Check the resulting UI state for any new permission dialog and use current
   elements for the next action. Reuse returned state or diffs when available;
   otherwise query the element tree. Use the fallback above only when needed.
4. Wait for the install process to finish and verify the package path and log.

If the risk is unexpected, stop and ask the user. Never treat a screenshot or a
successful tap as proof that installation completed.

## Launch and handle consent boundaries

Launch the package on the selected device using the available automation tool
or a serial-pinned adb launcher command. Inspect the initial UI using the same
element-first flow. Treat OS media permissions, app service agreements, and
privacy policies as separate decisions from APK installation. Grant only
the minimum permission needed for the requested QA flow. Leave legal and
privacy agreement acceptance to the user. Report installation, launch, and
in-app verification as separate outcomes.
