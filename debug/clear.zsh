#!/bin/zsh
echo $(tput clear && printf "\033[3J" && printf "\033[0;0H") >> /tmp/kitty_debug
