-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                     Hyprland Configuration                       ║
-- ║                         Entry Point (Lua)                        ║
-- ╚═══════════════════════════════════════════════════════════════════╝
-- See https://wiki.hypr.land/Configuring/

require("config.system")
require("config.input")
require("config.visual")
require("config.layouts")
require("config.rules")
require("config.binds")

-- For Noctalia Color templates
require("noctalia").apply_theme()
