---
layout:       post
title:        >
    Keys get "stuck" randomly and type endless line of a particular letter/command
site:         Ask Ubuntu
stack_url:    https://askubuntu.com/q/1029791
type:         Answer
tags:         keyboard 18.04
created_date: 2018-04-29 17:39:09
edit_date:    
votes:        "11 "
favorites:    
views:        "10,599 "
accepted:     Accepted
uploaded:     2023-01-03 19:49:43
git_md_url:   https://github.com/pippim/pippim.github.io/blob/main/_posts/2018/2018-04-29-Keys-get-_stuck_-randomly-and-type-endless-line-of-a-particular-letter_command.md
toc:          false
navigation:   false
clipboard:    false
---

In Ubuntu 18.04 issue this command:

``` 
$ gsettings get org.gnome.desktop.peripherals.keyboard repeat
true
```

If the result is `true` then turn off keyboard repeat using this command:

``` 
$ gsettings set org.gnome.desktop.peripherals.keyboard repeat false
```

The other related commands you can use are:

``` 
$ gsettings get org.gnome.desktop.peripherals.keyboard delay
uint32 500
$ gsettings get org.gnome.desktop.peripherals.keyboard repeat-interval
uint32 30
```

