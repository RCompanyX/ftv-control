# ftv

Control your Amazon Fire TV from the terminal via ADB.

`ftv` is a single bash script that wraps `adb` commands to provide a clean,
git-style CLI for navigating the Fire TV UI, managing apps, capturing
screenshots, streaming local video, and more — all from your Mac or Linux
terminal over WiFi.

## Features

- Remote control: directional, OK, back, home, menu
- Media keys: play/pause, seek, next/prev, volume
- Type text from your keyboard
- Power on/off/sleep/wake
- Take screenshots to your Desktop (or custom path)
- Install, uninstall, list, and launch apps (APK sideloading supported)
- Stream local video files to VLC on the Fire TV (no storage used on device)
- Auto-reconnect: re-establishes the ADB connection if it drops
- No dependencies beyond `bash`, `adb`, and `python3` (only for `stream`)
- Config stored in `~/.config/ftv/config` (no shell profile pollution)

## Requirements

- [`adb`](https://developer.android.com/tools/releases/platform-tools) (Android Platform Tools)
- An Amazon Fire TV (Stick / Cube / Edition TV) with **ADB Debugging** enabled
- Both devices on the **same WiFi network**
- `bash`, `adb`, and `python3` (only needed for `ftv stream`)

## Installation

1. Place the `ftv` script in a directory on your `PATH` (e.g. `~/bin`):

   ```sh
   mkdir -p ~/bin
   cp ftv ~/bin/ftv
   chmod +x ~/bin/ftv
   ```

2. Add `~/bin` to your `PATH` (in `~/.zshrc` or `~/.bashrc`):

   ```sh
   export PATH="$HOME/bin:$PATH"
   ```

3. Reload your shell:

   ```sh
   source ~/.zshrc   # or source ~/.bashrc
   ```

4. Verify:

   ```sh
   ftv help
   ```

### Installing adb (macOS with Homebrew)

```sh
brew install --cask android-platform-tools
```

## Fire TV setup

These steps are performed with the Fire TV remote.

1. Go to **Settings → My Fire TV** (or *Device / System*).
2. Open **About** and press **7 times** on *Build number* until
   "You are now a developer" appears.
3. Go back; **Developer Options** now appears — open it.
4. Enable **ADB Debugging**.
5. Enable **Install unknown apps** (required for sideloading APKs).
6. On a Fire TV Stick, also enable **Network ADB** (sometimes called
   *Debug over network*) in the same Developer Options screen.
7. Get the Fire TV's IP: **Settings → Network → About** → note the IPv4 address.

## Configuration

Store your Fire TV's IP once (persists across sessions):

```sh
ftv set-ip 192.0.2.10
```

Then connect for the first time:

```sh
ftv connect
```

> On the first connection, the Fire TV shows an **"Allow USB debugging?"**
> dialog. Select **"Always allow from this computer"** and confirm with OK.

Check the connection:

```sh
ftv status
```

## Usage

```
ftv <subcommand> [arguments]
```

### Connection

| Command | Description |
|---------|-------------|
| `ftv connect` | Connect to the Fire TV |
| `ftv disconnect` | Disconnect |
| `ftv status` | Show connection status (`adb devices -l`) |
| `ftv set-ip <IP>` | Save the Fire TV IP to config |
| `ftv ip` | Show the configured IP |

### Navigation (remote control)

| Command | Description |
|---------|-------------|
| `ftv up` / `down` / `left` / `right` | D-pad directions |
| `ftv ok` | Center / OK button |
| `ftv back` | Back |
| `ftv home` | Home |
| `ftv menu` | Menu |

### Media

| Command | Description |
|---------|-------------|
| `ftv play` | Play / pause |
| `ftv fwd` | Fast forward |
| `ftv rew` | Rewind |
| `ftv next` | Next track |
| `ftv prev` | Previous track |
| `ftv volup` | Volume up |
| `ftv voldown` | Volume down |
| `ftv mute` | Mute |

### Keyboard

| Command | Description |
|---------|-------------|
| `ftv type "<text>"` | Type text |
| `ftv enter` | Enter |
| `ftv del` | Delete |

### Power

| Command | Description |
|---------|-------------|
| `ftv on` | Wake up |
| `ftv off` | Sleep |
| `ftv toggle` | Toggle power |

### Screenshot

| Command | Description |
|---------|-------------|
| `ftv screenshot [path]` | Capture the screen (defaults to `~/Desktop/firetv_<timestamp>.png`) |

### Apps

| Command | Description |
|---------|-------------|
| `ftv launch <package>` | Open an app by package name |
| `ftv list [--third]` | List installed apps (`--third` for third-party only) |
| `ftv install <apk>` | Install an APK |
| `ftv reinstall <apk>` | Reinstall an APK, keeping data |
| `ftv uninstall <package>` | Uninstall an app |

### Streaming

| Command | Description |
|---------|-------------|
| `ftv stream <video-file>` | Stream a local video file to VLC on the Fire TV |

`ftv stream` starts a temporary HTTP server on your machine and opens the file
in VLC on the Fire TV, so the video plays over the network without copying it
to the device's limited storage. VLC must be installed on the Fire TV. Stop the
server with `Ctrl+C` when you're done watching.

### Other

| Command | Description |
|---------|-------------|
| `ftv help` | Show help |

## Examples

Open an app on the Fire TV by its package name:

```sh
ftv launch com.example.app
```

Find the package name of an installed app:

```sh
ftv list --third | grep example
```

Install an APK from your Mac:

```sh
ftv install ~/Downloads/app.apk
```

Type a search query on the Fire TV:

```sh
ftv type "documentaries"
ftv enter
```

Take a screenshot to a custom location:

```sh
ftv screenshot ~/Pictures/firetv.png
```

## Auto-reconnect

If a command is run while the ADB connection has dropped, `ftv` automatically
attempts to reconnect before sending the command — so you don't need to run
`ftv connect` manually after the Fire TV reboots or the WiFi blips.

## Notes

- If your Fire TV's IP changes (e.g. due to DHCP), update it with
  `ftv set-ip <new-IP>`.
- Screen mirroring is not included in this script. For that, consider
  an alternative screen-mirroring/casting app.
  For playing local video files, use `ftv stream` (requires VLC on the Fire TV).
- `ftv launch` tries the standard `monkey` launcher first; if that fails
  (some Fire TV apps don't expose a LAUNCHER category), it automatically
  resolves the app's MAIN activity and launches it via `am start`.

## License

[MIT](LICENSE)
