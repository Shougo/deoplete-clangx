# C/C++ Completion for deoplete using clang


## Install

* Install the latest deoplete.nvim
* Make sure you already have clang(`clang` command)


## Customization

```vim
" Change clang binary path
call deoplete#custom#var('clangx', 'clang_binary', '/usr/local/bin/clang')

" Change clang options
call deoplete#custom#var('clangx', 'default_c_options', '')
call deoplete#custom#var('clangx', 'default_cpp_options', '')
```


### neoinclude

deoplete-clangx supports neoinclude plugin

https://github.com/Shougo/neoinclude.vim/

neoinclude adds include directory options(-I) automatically for clang.


### ".clang" or ".clang_complete" file

You can configure compiler options using the file.

https://github.com/Rip-Rip/clang_complete#minimum-configuration


## Todo

* compile_commands.json file support
