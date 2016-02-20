# deoplete-d

Adds auto-complete support for the `D` programming language to Vim

## Installation

Using your favorite package manager or whatever (idk, you probably know vim
better than I do):

```
Plug 'landaire/deoplete-d'
```

## Configuration

Default configuration:

`let g:deoplete#sources#d#dcd_client_binary = ''` location of the `dcd-client`
on your system. This is optional and will be found in your `$PATH` if not set

`let g:deoplete#sources#d#dcd_server_binary = ''` location of the `dcd-server`
on your system. This is optional and will be found in your `$PATH` if not set

`let g:deoplete#sources#d#dcd_server_autostart = 1` - whether or not `dcd-server`
should be auto-started

## Preview

![deoplete-d preview](http://i.imgur.com/8UH5SxS.gif)
