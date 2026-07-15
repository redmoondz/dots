-- --- dwindle.lua ---
-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                         Dwindle Layout                           ║
-- ╚═══════════════════════════════════════════════════════════════════╝
-- Configuration for the dwindle tiling layout

-- --- master.lua ---
-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║                          Master Layout                           ║
-- ╚═══════════════════════════════════════════════════════════════════╝
-- Configuration for the master layout

hl.config({
  dwindle = {
    -- Preserve split ratio when moving windows
    preserve_split = true,
    -- Smart splitting based on cursor position
    smart_split = false,
    -- Disable smart resizing for consistent behavior
    smart_resizing = false,
  },
  master = {
    -- New windows become master
    new_status = "master",
    -- New windows appear on top
    new_on_top = true,
    -- Allow small split ratio
    allow_small_split = false,
  },
})
