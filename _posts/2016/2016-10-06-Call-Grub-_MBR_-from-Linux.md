---
layout:       post
title:        >
    Call Grub (MBR) from Linux
site:         Stack Overflow
stack_url:    https://stackoverflow.com/q/39887196
type:         Question
tags:         assemblies mbr grub2
created_date: 2016-10-06 03:46:20
edit_date:    
votes:        "2 "
favorites:    0
views:        "70 "
accepted:     
uploaded:     2023-01-03 19:49:43
git_md_url:   https://github.com/pippim/pippim.github.io/blob/main/_posts/2016/2016-10-06-Call-Grub-_MBR_-from-Linux.md
toc:          false
navigation:   false
clipboard:    false
---

I need an ASSEMBLER tool.

I need to switch processor from protected mode to real mode.

I need to copy the first 512 bytes of First Sector of first drive (it's an SSD now) to 0000:07c0 and JMP to that location.

In effect I need to boot Grub2 from Linux by-passing BIOS POST to save a few seconds in `sudo reboot`.

Any ideas?
