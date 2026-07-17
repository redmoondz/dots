if status is-interactive
# Commands to run in interactive sessions can go here
  fastfetch

  alias "ls" "lsd"
  alias "cat" "bat"



end
export PATH="$HOME/.local/bin:$PATH"

# Added by LM Studio CLI (lms)
set -gx PATH $PATH /home/redmoon/.lmstudio/bin
# End of LM Studio CLI section

