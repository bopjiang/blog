---
title: "G-Suite知识汇总"
date: 2020-06-02T07:00:30+08:00
categories:
  - tech
---


## Gmail

### open draft in new window
press **Shift** when **click**.

## Google Drive
### [Create a Symbolic Link](https://www.bustercollings.com/blog/2014/06/14/how-to-copy-a-file-or-folder-in-google-drive-create-a-symbolic-link-symlink/)
* Click to highlight the file(s) and folder(s) you want to copy
* Press **Shift-Z** to open a dialog with the “**Add here**” button
* Navigate to the destination folder
* Press “**Add here**”

## Google Docs
### New Google docs quickly
* [new Doc](https://doc.new)
* [new Sheet](https://sheet.new)
* [new Slide](https://slides.new)

### generate random string in Sheet
Add customized function as [link](https://yagisanatode.com/2018/08/23/google-sheets-random-alphabetic-random-alphanumeric-and-random-alphanumeric-character-custom-functions/)

`=RANDALPHA(2,0)&RANDALPHA(10, 2)`

## Chrome
### disable auto update
```bash
$ cat /etc/hosts

# disable chrome update
127.0.0.1 tools.google.com
```
