-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                        Autostart Applications                    ║
-- ╚═══════════════════════════════════════════════════════════════════╝

hl.on("hyprland.start", function()
  hl.exec_cmd("solaar -ddd --window=hide") -- MX Master 3 mouse support
  
  hl.exec_cmd("Telegram -ddd --window=hide") -- Telegram
  hl.exec_cmd("steam -ddd --window=hide") -- Steam
  hl.exec_cmd("discord -ddd --window=hide") -- Discord

  hl.exec_cmd("voxtype") -- Speech recognition server
  hl.exec_cmd("noctalia") -- Quickshell
  -- hl.exec_cmd("hyprpaper") -- Wallpaper daemon
  hl.exec_cmd("wl-paste --watch cliphist store") -- Clipboard manager
  hl.exec_cmd("easyeffects --gapplication-service") -- Audio effects
  hl.exec_cmd("hypridle") -- Idle manager
  -- hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1") -- Authentication agent
  hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP") -- Screen sharing support
end)

-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                       Environment Variables                      ║
-- ╚═══════════════════════════════════════════════════════════════════╝
-- See https://wiki.hypr.land/Configuring/Environment-variables/

-- Cursor settings
hl.env("XCURSOR_SIZE", "22")
hl.env("WLR_NO_HARDWARE_CURSORS", "1")

-- Wayland specific
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- Qt specific
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

-- GTK specific
hl.env("GDK_BACKEND", "wayland,x11")

-- Nvidia specific
hl.env("GBM_BACKEND", "nvidia-drm")
hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")

-- Wayland native support for games (including Wine/Proton)
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")
hl.env("WINEWAYLAND", "1")

-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                        Monitor Configuration                     ║
-- ╚═══════════════════════════════════════════════════════════════════╝
-- See https://wiki.hypr.land/Configuring/Monitors/

-- Primary laptop display
hl.monitor(
  { 
    output = "DP-1", 
    mode = "1920x1080@60", 
    position = "0x0", 
    scale = 1
  }
)

hl.config({
  misc = {
    disable_hyprland_logo = true,
    disable_splash_rendering = true,
    vrr = 0,
    animate_manual_resizes = false,
    animate_mouse_windowdragging = false,
    enable_swallow = false,
    swallow_regex = "(foot|kitty|allacritty|Alacritty)",
    allow_session_lock_restore = true,
    initial_workspace_tracking = false,
    focus_on_activate = false,
  },
  binds = {
    scroll_event_delay = 0,
    hide_special_on_workspace_change = true,
  },
})
