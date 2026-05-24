if status is-interactive
  # Commands to run in interactive sessions can go here
  fastfetch
  set -U fish_greeting ""


  alias "ls" "lsd"
  alias "cat" "bat"
  alias "pacman" "sudo pacman -S"

end
