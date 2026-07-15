-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                         Window Rules                             ║
-- ║            (imported from dots-hyprland + user rules)            ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- Keybindings overlay (user)
hl.window_rule({
  match = { class = "^(com\\.hypr\\.keybindsviewer)$" },
  float = true,
  center = true,
  size = {1100, 660},
  pin = true,
  no_focus = true,
  border_size = 0,
  rounding = 12,
  opacity = "1.0 1.0",
})

-- Global opacity (user)
hl.window_rule({ match = { class = "^.*$" }, opacity = "1 0.9" })

-- ######## Window rules (dots-hyprland) ########

-- Disable blur for xwayland context menus
hl.window_rule({ match = { class = "^()$", title = "^()$" }, no_blur = true })

-- Disable blur for every window
hl.window_rule({ match = { class = ".*" }, no_blur = true })

-- Floating dialogs
hl.window_rule({ match = { title = "^(Open File)(.*)$" }, center = true, float = true })
hl.window_rule({ match = { title = "^(Select a File)(.*)$" }, center = true, float = true })
hl.window_rule({
  match = { title = "^(Choose wallpaper)(.*)$" },
  center = true,
  float = true,
  size = {"monitor_w*.60", "monitor_h*.65"},
})
hl.window_rule({ match = { title = "^(Open Folder)(.*)$" }, center = true, float = true })
hl.window_rule({ match = { title = "^(Save As)(.*)$" }, center = true, float = true })
hl.window_rule({ match = { title = "^(Library)(.*)$" }, center = true, float = true })
hl.window_rule({ match = { title = "^(File Upload)(.*)$" }, center = true, float = true })
hl.window_rule({ match = { title = "^(.*)(wants to save)$" }, center = true, float = true })
hl.window_rule({ match = { title = "^(.*)(wants to open)$" }, center = true, float = true })
hl.window_rule({ match = { class = "^(blueberry\\.py)$" }, float = true })
hl.window_rule({ match = { class = "^(guifetch)$" }, float = true })
hl.window_rule({
  match = { class = "^(pavucontrol)$" },
  float = true,
  size = {"monitor_w*.45", "monitor_h*.45"},
  center = true,
})
hl.window_rule({
  match = { class = "^(org.pulseaudio.pavucontrol)$" },
  float = true,
  size = {"monitor_w*.45", "monitor_h*.45"},
  center = true,
})
hl.window_rule({
  match = { class = "^(nm-connection-editor)$" },
  float = true,
  size = {"monitor_w*.45", "monitor_h*.45"},
  center = true,
})
hl.window_rule({ match = { class = ".*plasmawindowed.*" }, float = true })
hl.window_rule({ match = { class = "kcm_.*" }, float = true })
hl.window_rule({ match = { class = ".*bluedevilwizard" }, float = true })
hl.window_rule({ match = { title = ".*Welcome" }, float = true })
hl.window_rule({ match = { title = "^(illogical-impulse Settings)$" }, float = true })
hl.window_rule({ match = { title = ".*Shell conflicts.*" }, float = true })
hl.window_rule({
  match = { class = "org.freedesktop.impl.portal.desktop.kde" },
  float = true,
  size = {"monitor_w*.60", "monitor_h*.65"},
})
hl.window_rule({
  match = { class = "^(Zotero)$" },
  float = true,
  size = {"monitor_w*.45", "monitor_h*.45"},
})

-- Move — prevent interfering windows
hl.window_rule({
  match = { class = "^(plasma-changeicons)$" },
  float = true,
  no_initial_focus = true,
  move = {999999, 999999},
})
hl.window_rule({ match = { title = "^(Copying — Dolphin)$" }, move = {40, 80} })

-- Tiling
hl.window_rule({ match = { class = "^dev\\.warp\\.Warp$" }, tile = true })

-- Picture-in-Picture
hl.window_rule({
  match = { title = "^([Pp]icture[-\\s]?[Ii]n[-\\s]?[Pp]icture)(.*)$" },
  float = true,
  keep_aspect_ratio = true,
  move = {"monitor_w*.73", "monitor_h*.72"},
  size = {"monitor_w*.25", "monitor_h*.25"},
  pin = true,
})

-- Tearing
hl.window_rule({ match = { title = ".*\\.exe" }, immediate = true })
hl.window_rule({ match = { title = ".*minecraft.*" }, immediate = true })
hl.window_rule({ match = { class = "^(steam_app).*" }, immediate = true })

-- Fix Jetbrain IDEs focus/rerendering problem
hl.window_rule({
  match = { class = "^jetbrains-.*$", float = true, title = "^$|^\\s$|^win\\d+$" },
  no_initial_focus = true,
})

-- No shadow for tiled windows
hl.window_rule({ match = { float = false }, no_shadow = true })

-- ######## Workspace rules ########
hl.workspace_rule({ workspace = "special:special", gaps_out = 30 })
