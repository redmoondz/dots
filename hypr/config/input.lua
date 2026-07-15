-- --- keyboard.lua ---
-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                        Keyboard Configuration                    ║
-- ╚═══════════════════════════════════════════════════════════════════╝
-- Keyboard layout and input settings

hl.config({
  input = {
    -- Keyboard layouts: English, Russian, Ukrainian
    kb_layout = "us,ru,ua",
    kb_options = "",

    -- Numlock enabled by default
    numlock_by_default = true,

    -- Key repeat settings
    repeat_delay = 250,
    repeat_rate = 35,

    -- Other input settings
    special_fallthrough = true,
    follow_mouse = 1,

    accel_profile = "flat",
    force_no_accel = true,
    sensitivity = 0.0, -- Optional: -1.0 to 1.0, 0 means no modification

    touchpad = {
      natural_scroll = true,
      disable_while_typing = true,
      clickfinger_behavior = true,
      scroll_factor = 0.5,
    },
    scroll_factor = 0.2,
  },

  gestures = {
    workspace_swipe_distance = 700,
    workspace_swipe_cancel_ratio = 0.2,
    workspace_swipe_min_speed_to_force = 5,
    workspace_swipe_direction_lock = true,
    workspace_swipe_direction_lock_threshold = 10,
    workspace_swipe_create_new = true,
  },
})

hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })

-- Language switching keybinds
-- Win + Space -> English
hl.bind("SUPER + SPACE", hl.dsp.exec_cmd("hyprctl switchxkblayout main 0"))

-- Win + Space + Shift -> Russian
hl.bind("SUPER + SHIFT + SPACE", hl.dsp.exec_cmd("hyprctl switchxkblayout main 1"))

-- Win + Space + Ctrl -> Ukrainian
hl.bind("SUPER + CTRL + SPACE", hl.dsp.exec_cmd("hyprctl switchxkblayout main 2"))
