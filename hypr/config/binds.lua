local mainMod = "SUPER"
local ipc = "noctalia msg "

-- MX Master 3S Host Change Button
hl.bind(mainMod .. " + F3", hl.dsp.exec_cmd('solaar config "MX Master 3S" change-host 2'))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Core Applications                         │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + RETURN", hl.dsp.exec_cmd("alacritty"))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("nautilus"))
hl.bind(mainMod .. " + F", hl.dsp.exec_cmd("google-chrome-stable"))
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.exec_cmd("google-chrome-stable --private-window"))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd("code"))
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("Telegram"))
hl.bind(mainMod .. " + O", hl.dsp.exec_cmd("obs"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("spotify"))
hl.bind(mainMod .. " + Z", hl.dsp.exec_cmd("datagrip"))

hl.bind(mainMod .. " + ALT + R", hl.dsp.exec_cmd("sh ~/.config/hypr/scripts/voxtype-toggle.sh")) -- toggle voxtype daemon on/off

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                          Menus                                  │
-- ╰─────────────────────────────────────────────────────────────────╯
-- Noctalia v5 IPC: `noctalia msg <command>` replaces the old, no-longer-working
-- `qs -c noctalia-shell ipc call <namespace> <action>` (the `qs` binary doesn't
-- exist anymore — Noctalia v5 is a standalone binary with its own IPC).
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd(ipc .. "panel-toggle launcher"))
hl.bind(mainMod .. " + X", hl.dsp.exec_cmd(ipc .. "panel-toggle session")) -- was sessionMenu
hl.bind(mainMod .. " + SHIFT + X", hl.dsp.exec_cmd(ipc .. "settings-toggle"))
hl.bind(mainMod .. " + comma", hl.dsp.exec_cmd(ipc .. "panel-toggle launcher /emo")) -- emoji picker
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd(ipc .. "panel-toggle clipboard")) -- dedicated clipboard panel now

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                        Screenshots                             │
-- ╰─────────────────────────────────────────────────────────────────╯
-- Region screenshot
hl.bind("ALT + SHIFT + 1", hl.dsp.exec_cmd(
  'mkdir -p ~/Pictures/Screenshots && FILE="$HOME/Pictures/Screenshots/Screenshot-$(date +%F_%H-%M-%S).png" && grim -g "$(slurp)" - | tee >(wl-copy) > "$FILE" && [ -s "$FILE" ] && notify-send -i "$FILE" "Screenshot" "Selected area copied to clipboard and saved"'
))

-- Full screen screenshot
hl.bind("ALT + SHIFT + 2", hl.dsp.exec_cmd(
  'mkdir -p ~/Pictures/Screenshots && FILE="$HOME/Pictures/Screenshots/Screenshot-$(date +%F_%H-%M-%S).png" && grim - | tee >(wl-copy) > "$FILE" && [ -s "$FILE" ] && notify-send -i "$FILE" "Screenshot" "Full screen copied to clipboard and saved"'
))

-- Full screen screenshot and save to clipboard
hl.bind("Print", hl.dsp.exec_cmd(
  'grim - | wl-copy && wl-paste > ~/Pictures/Screenshots/Screenshot-$(date +%F_%T).png | dunstify -i ~/Pictures/Screenshots/Screenshot-$(date +%F_%T).png "Screenshot of whole screen taken" -t 1000'
))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                        Wallpaper                               │
-- ╰─────────────────────────────────────────────────────────────────╯
-- wallcards plugin's IPC is currently dead under Noctalia v5 (it still uses a raw
-- Quickshell IpcHandler from v4, and no qs-compatible socket exists anymore — only
-- noctalia-wayland-1.sock, confirmed via `ss -xl`). Falling back to the built-in
-- wallpaper panel until wallcards is updated for v5's plugin dispatch system.
hl.bind(mainMod .. " + CTRL + W", hl.dsp.exec_cmd(ipc .. "panel-toggle wallpaper"))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Window Management                         │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + Q", hl.dsp.window.close())
hl.bind("ALT + F4", hl.dsp.window.close())
hl.bind(mainMod .. " + F11", hl.dsp.window.fullscreen({ action = "toggle" }))
hl.bind(mainMod .. " + S", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo()) -- dwindle

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                         Focus Movement                         │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + left", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down", hl.dsp.focus({ direction = "down" }))

-- Alt+Tab functionality
hl.bind("ALT + Tab", hl.dsp.window.cycle_next({ next = true }))
hl.bind(mainMod .. " + Tab", hl.dsp.window.swap({ next = true }))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                         Window Movement                        │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.swap({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + left", hl.dsp.window.swap({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + up", hl.dsp.window.swap({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + down", hl.dsp.window.swap({ direction = "down" }))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                         Window Resizing                        │
-- ╰─────────────────────────────────────────────────────────────────╯
-- Resize active window with Super +/-
hl.bind(mainMod .. " + equal", hl.dsp.window.resize({ x = 45, y = 45, relative = true }), { repeating = true })
hl.bind(mainMod .. " + minus", hl.dsp.window.resize({ x = -45, y = -45, relative = true }), { repeating = true })

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Mouse Window Actions                      │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Volume Controls                           │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd(ipc .. "volume-up"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd(ipc .. "volume-down"), { locked = true, repeating = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd(ipc .. "volume-mute"), { locked = true })

-- Volume control with GUI
hl.bind(mainMod .. " + SHIFT + V", hl.dsp.exec_cmd("pavucontrol"))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                    Brightness Controls                         │
-- ╰─────────────────────────────────────────────────────────────────╯
-- For laptop brightness keys, use the following binds. Make sure to have brillo installed and configured properly.
-- hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd(ipc .. "brightness-up"), { locked = true, repeating = true })
-- hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(ipc .. "brightness-down"), { locked = true, repeating = true })

-- For external monitor brightness control using DDC/CI, use the following binds.
-- Change notification method, adapt to quickshell
hl.bind(mainMod .. " + F1", hl.dsp.exec_cmd(
  'ddcutil setvcp 10 - 10  && bri=$(ddcutil getvcp 10 --terse | awk \'{print $4}\') && dunstify -h int:value:"$bri" -i ~/.config/dunst/assets/brightness.svg -t 500 -r 2594 "Monitor Brightness: $bri"'
), { locked = true, repeating = true })
hl.bind(mainMod .. " + F2", hl.dsp.exec_cmd(
  'ddcutil setvcp 10 + 10 && bri=$(ddcutil getvcp 10 --terse | awk \'{print $4}\') && dunstify -h int:value:"$bri" -i ~/.config/dunst/assets/brightness.svg -t 500 -r 2594 "Monitor Brightness: $bri"'
), { locked = true, repeating = true })

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Media Player Controls                     │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"))
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"))
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"))
hl.bind("XF86AudioStop", hl.dsp.exec_cmd("playerctl stop"))

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Screen Control                            │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + SHIFT + ALT + S", hl.dsp.exec_cmd("sleep 1 && hyprctl dispatch dpms off")) -- turn off screen
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("sleep 1 && hyprctl dispatch dpms on")) -- turn on screen

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Lock Screen                               │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd(ipc .. "session lock")) -- was lockScreen lock

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                    Configuration Management                     │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + SHIFT + R", hl.dsp.exec_cmd("sh ~/.config/hypr/scripts/reload.sh")) -- reload hyprland config

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                      Switch Workspaces                         │
-- ╰─────────────────────────────────────────────────────────────────╯
-- ╭─────────────────────────────────────────────────────────────────╮
-- │                    Move Window to Workspace                    │
-- ╰─────────────────────────────────────────────────────────────────╯
-- follow = false preserves the old `movetoworkspacesilent` behavior (move without switching focus)
for i = 1, 9 do
  hl.bind(mainMod .. " + " .. i, hl.dsp.focus({ workspace = i }))
  hl.bind(mainMod .. " + SHIFT + " .. i, hl.dsp.window.move({ workspace = i, follow = false }))
end

-- ╭─────────────────────────────────────────────────────────────────╮
-- │                    Scroll Through Workspaces                   │
-- ╰─────────────────────────────────────────────────────────────────╯
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))
