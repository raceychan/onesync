Help me to write a function that sync .zshrc file, you might ask me for more details if quired,
ask the question before writing the function.

while writing the function, you might further ask me any question to improve the quality of the function.

in my zshrc, there is a variable named ONEDRIVE_DIR, which points to the onedrive dir in my computer.
ONEDRIVE_DIR="${ONEDRIVE_DIR:=/mnt/d/OneDrive}"

and in the ONEDRIVE_DIR, there is a /Config/linux/dotfiles folder,
now, I would like to ask you to write a function named sync_zsh, which does the following:

1. when there is no .zshrc files in the /mnt/d/OneDrive/Config/linux/dotfiles folder, sync the current .zshrc file to it.
2. when there is already a .zshrc file in the folder, do following:
   compare the last modified time of the current .zshrc file with the existing one,
   if the last modified time of the local .zshrc file is newer, make a copy of the .zshrc file in the dotfiles folder, save it as remote.zshrc.copy
   then replace the .zshrc file in the dotfiles folder with current .zshrc to the dotfiles folder,
   otherwise, make a copy of the local .zshrc file, save it as local.zshrc.copy, then replace t he local .zshrc file with the one in dotfiles folder.
