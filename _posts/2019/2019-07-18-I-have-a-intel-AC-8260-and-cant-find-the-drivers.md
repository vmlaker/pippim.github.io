---
layout:       post
title:        >
    I have a intel AC 8260 and cant find the drivers
site:         Ask Ubuntu
stack_url:    https://askubuntu.com/q/1159338
type:         Answer
tags:         drivers nic
created_date: 2019-07-18 22:31:57
edit_date:    
votes:        "2 "
favorites:    
views:        "1,650 "
accepted:     Accepted
uploaded:     2023-01-03 19:49:43
git_md_url:   https://github.com/pippim/pippim.github.io/blob/main/_posts/2019/2019-07-18-I-have-a-intel-AC-8260-and-cant-find-the-drivers.md
toc:          false
navigation:   false
clipboard:    false
---

The Intel Wifi drivers are built into the Linux kernel already. To see them use:

``` 
lsmod | grep iwlwifi
```

Firmware for Linux Intel WiFi drivers by card model and Kernel version are [here][1]:

[![Linux Wifi Firmware.png][2]][2]

For general questions about Intel Wi-Fi on Linux, email linuxwifi@intel.com.

  [1]: https://www.intel.ca/content/www/ca/en/support/articles/000005511/network-and-i-o/wireless-networking.html
  [2]: https://i.stack.imgur.com/EuQoM.png
