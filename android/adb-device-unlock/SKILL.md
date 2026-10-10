---
name: adb-device-unlock
description: >-
  Unlock an authorized Android phone with a user-supplied PIN over adb. Use when
  a connected Android device is locked, sleeps before PIN entry, or adb UI work
  cannot start until the device is awake and unlocked.
---

# Android ADB Device Unlock

Use only after the user authorizes unlocking the selected Android device. This
workflow was verified on a vivo phone with OriginOS; OEM screens and commands
can differ. Load the `agent-device` skill separately for app automation.

## Bind one device

Run `adb devices -l`, identify the intended device serial, and pass
`-s "$SERIAL"` to every adb command. Never use a command that can act on every
connected device. The serial and PIN are session inputs: never save them in a
file, screenshot, Skill, Git commit, or status message.

## Check the lock state

Inspect:

```bash
adb -s "$SERIAL" shell dumpsys window policy
```

Look for `showing=true`, `SCREEN_STATE_OFF`, or
`INTERACTIVE_STATE_SLEEP`. An adb command returning exit code 0 does not prove
that the device is unlocked.

## Unlock before the screen sleeps

Some OEM lock screens sleep within seconds. Keep wake, swipe, PIN entry, and
confirmation in one short adb shell invocation rather than separate commands:

```bash
adb -s "$SERIAL" shell 'input keyevent KEYCODE_WAKEUP && input swipe 540 1900 540 600 250 && input text <USER_SUPPLIED_PIN> && input keyevent KEYCODE_ENTER'
```

Replace the placeholder only at execution time. Coordinates above are for a
1080x2358 portrait screen; inspect the device and adapt the swipe for another
layout. Do not repeat the PIN blindly. After one failed attempt, stop and ask
the user to unlock manually to avoid a lockout.

Verify all of the following with `dumpsys window policy`:

- `showing=false`
- `screenState=SCREEN_STATE_ON`
- `interactiveState=INTERACTIVE_STATE_AWAKE`

Only report the unlock step complete when those observable states are present.
Leave the device awake for the next operation or hand it back to the user.
