---
name: apk-device-install
description: >-
  Install and verify an Android APK on one authorized device, including OEM USB
  installer risk prompts and agent-device snapshot-helper failures. Use when
  adb install is rejected, a large APK times out through agent-device, or a
  device-side install confirmation must be completed before QA.
---

# Android APK Device Install

Use after the target Android device is awake and unlocked. For a locked device,
load `adb-device-unlock` first. Load `agent-device` separately for its
current app-driving rules. This workflow was verified on a vivo phone with
OriginOS; OEM screens and commands can differ.

## Bind the package and device

Run `adb devices -l`, select one intended serial, and pass `-s "$SERIAL"` to
every adb command. Confirm the APK path, package identity, and expected build
before installation. Use `install -r` to preserve app data; uninstall only when
the user explicitly authorizes data removal. Do not run a helper that installs
to every connected device.

## Install and retain the result

For a large APK, a direct serial-pinned adb install can be more reliable than an
`agent-device install` daemon request:

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
bring the device installer to the foreground, capture a screenshot, and inspect
the actual prompt. Do not infer coordinates from another screen.

## Complete the OEM installer prompt

Start or resume an `agent-device` session on the same device. Use
`snapshot -i` for current refs. If the snapshot helper cannot install because
the OEM rejects its APK, use `agent-device screenshot` and inspect the visible
system UI; `adb shell uiautomator dump` can provide text and bounds as a
fallback.

On the observed vivo flow, the installer showed the verified app name, version,
size, an external-source risk notice, an acknowledgement checkbox, and a
Continue installation button. Before tapping, check that the app identity and
risk notice match the intended debug or release artifact. Then:

1. Select the acknowledgement checkbox if the user has authorized this debug
   installation and the notice is expected.
2. Tap Continue installation.
3. Re-observe after every tap because Android may open a new permission dialog.
4. Wait for the install process to finish and verify the package path and log.

If the risk is unexpected, stop and ask the user. Never treat a screenshot or a
successful tap as proof that installation completed.

## Launch and handle consent boundaries

Open the package with:

```text
agent-device open "$PACKAGE" --foreground --device <device-name>
```

Inspect the initial UI. Treat OS media permissions, app service agreements,
and privacy policies as separate decisions from APK installation. Grant only
the minimum permission needed for the requested QA flow. Leave legal and
privacy agreement acceptance to the user. Report installation, launch, and
in-app verification as separate outcomes.
