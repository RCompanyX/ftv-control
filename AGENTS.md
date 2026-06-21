# AGENTS.md

Guidance for OpenCode sessions working in this repo.

## What this repo is

A single bash script (`ftv`) that controls an Amazon Fire TV via ADB over WiFi.
No build system, no tests, no lint, no dependencies beyond `bash`, `adb`, and
`python3` (the latter only used by `ftv stream` to serve the file over HTTP).
The script is the only artifact.

## Verification

There is no test suite. Verify changes in two steps:

1. **Syntax check:** `bash -n ftv`
2. **Manual test against a live Fire TV:** copy the script to the working
   location and run a subcommand:
   ```sh
   cp ftv ~/bin/ftv && ~/bin/ftv status
   ```

A Fire TV with ADB Debugging enabled must be on the same network. The Fire TV's
IP is stored in `~/.config/ftv/config` (not in the repo).

## Gotchas

- **Two copies of the script:** the repo copy (`./ftv`) and the live copy
  (`~/bin/ftv`). Edit the repo copy, then sync with `cp ftv ~/bin/ftv` to test
  against a real device.
- **No copyrighted references:** examples in `README.md` and code comments must
  not name real apps, movies, or brands. Use generic placeholders
  (e.g. `com.example.app`).

## Script architecture

`ftv` uses subcommand dispatch in `main()` (bottom of file, a `case` statement).
Most subcommands call `ftv_keyevent` which wraps `adb shell input keyevent`.

`ftv launch` has a two-stage fallback: it tries `monkey` with the LAUNCHER
category first, then falls back to resolving the app's MAIN activity via
`dumpsys` and launching with `am start`. This fallback exists because some
Fire TV apps (e.g. streaming apps) don't expose a LAUNCHER category.

`ftv stream` deduces the host's LAN IP with a no-send UDP socket trick
(`ftv_get_host_ip`), launches VLC on the Fire TV with an `am start VIEW`
intent pointing at an `http.server` it runs on port 8765, and blocks serving
the file until interrupted. Port is fixed; raise as an arg if it ever clashes.

## Repo

Default branch is `main`.
