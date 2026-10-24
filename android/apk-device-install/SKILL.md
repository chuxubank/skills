---
name: apk-device-install
description: >-
  Install and verify an Android APK on one authorized device. Use when adb
  install is rejected, an APK transfer times out, package signatures do not
  match, a USB install confirm counts down and auto-rejects, or a device-side
  installer prompt must be completed before QA.
---

# Android APK Device Install

Use after the target Android device is awake and unlocked. For a locked device,
load `adb-device-unlock` first. For a prompt that stays on screen, follow the
available device automation tool. Classify the live installer by its controls,
not by the phone's brand.

## Bind the package and device

Run `adb devices -l`, select one intended serial, and pass `-s "$SERIAL"` to
every adb command. Confirm the APK path, package identity, and expected build
before installation. Use `install -r` to preserve app data. Uninstall only
when the user explicitly authorizes data removal. Do not run a helper that
installs to every connected device.

## Install and retain the result

For a large APK, use a direct serial-pinned adb install to avoid automation
wrapper timeouts:

```bash
adb -s "$SERIAL" install -r "$APK" > "$INSTALL_LOG" 2>&1 &
INSTALL_PID=$!
```

Keep the device awake. Read the installer before waiting out a confirm. Then
read `$INSTALL_LOG` for `Success` or the exact `INSTALL_FAILED_*` reason.

Installation is complete only when the log contains `Success` and this returns
a path:

```bash
adb -s "$SERIAL" shell pm path "$PACKAGE"
```

A screenshot, a tap, or a focused installer is not that proof.

## Signature mismatch

`INSTALL_FAILED_UPDATE_INCOMPATIBLE` means the installed package was signed
with a different key. Stop and ask. After the user authorizes removal:

```bash
adb -s "$SERIAL" uninstall "$PACKAGE"
adb -s "$SERIAL" install -r "$APK"
```

App data is gone. A later empty home screen is that result, not a launch
failure. The replacement install can still raise a USB confirm.

## Read the confirm

Poll `adb -s "$SERIAL" shell dumpsys window` until `mCurrentFocus` leaves the
app under install. Dump once while that installer is focused:

```bash
adb -s "$SERIAL" exec-out uiautomator dump /dev/tty
```

Record each control's text, resource id, and bounds. Match the displayed app
name to the package before any tap. From those labels, classify the prompt:

- **Countdown**: the reject control's text includes a remaining count, or the
  log becomes `INSTALL_FAILED_USER_RESTRICTED` / `Install canceled by user`
  when that count ends. One Redmi showed `拒绝（8）` on
  `AdbInstallActivity`; the same shape is the count, whatever the vendor names
  the activity.
- **Staying**: the prompt remains, and continue depends on an acknowledgement
  of the risk notice. One vivo OriginOS prompt showed the app name, version,
  size, that notice, a checkbox, and Continue installation.
- **Unexpected**: the name does not match, or the notice is not the authorized
  USB install. Stop and ask.

A future-prompt control is neither acknowledgement nor continue. Its label is
about later prompts, such as `拒绝后下次安装不再提示`. Leave it unchanged.
Continue can already be enabled.

## Countdown confirm

Opening an automation session spends the count: device resolution and a
screenshot that needs a session both miss the dialog. A second element query
after it closes only shows the launcher.

Tap the center of the continue control recorded above if the installer is
still focused. If the log already says canceled, start the install again and,
as soon as the same installer activity is focused, tap those saved
coordinates. Skip another dump.

One retry with coordinates from this device's dump is the recovery. A second
cancel without those coordinates means stop and ask. Coordinates from another
screen, resolution, or phone are not a substitute.

## Staying confirm

Use the available device automation tool on the same device. Prefer its
structured UI elements and element-based actions, using current refs or
id/label/role selectors as supported. Continue from the action's returned UI
state or diff when available; request a fresh element tree only when needed
to identify the next target.

If the tool cannot expose the installer, use the dump already taken. Capture a
screenshot only when that structured UI is unavailable, sparse, or insufficient
to identify the prompt; inspect the image before using coordinates. Return to
element-based actions once structured UI is usable. Full-screen screenshots
are not a routine step.

Select the acknowledgement only when the user has authorized this install and
continue depends on it. Tap continue. Check the resulting UI for another
permission dialog and use its current elements. Then apply the same `Success`
plus `pm path` check.

## Launch and consent boundaries

After `pm path` succeeds, launch the package on the selected device using the
available automation tool or a serial-pinned adb launcher command. Inspect the
initial UI with the same element-first flow. Treat OS media permissions, app
service agreements, and privacy policies as separate decisions from APK
installation. Grant only the minimum permission needed for the requested QA
flow. Leave legal and privacy agreement acceptance to the user. Report
installation, launch, and in-app verification as separate outcomes.
