# pexit

> This is a CLI tool to exit any process with arbitrary exit code.

Instead of killing a process, do you ever want to "exit" it? `pexit` comes to the rescue!

With some prerequisites (see below), you can force any process to exit, even with your specified exit code!

## Why would you want to use `pexit`?

* For fun.
* In the case of running a pipelined job `foo && bar`, simply killing `foo` will cause it to exit with error and `bar` is not executed. Using `pexit`, however, can make `foo` exit with success so that `bar` continues to be executed.

## Install
```
pip install pexit
```

## Usage
```
pexit <pid> [<exit_code>]
# The default value for <exit_code> is 0 (meaning success)
```

## Limitations
* `pexit` relies on the system call `ptrace`, which does not exit in some systems (like Windows).
* To be able to `ptrace` any process, you may need root privilege (`sudo pexit ...`) or allow this in system setting (`sudo sysctl kernel.yama.ptrace_scope=0`).

## Acknowledgements
This project refers to the following sources:
* A great example showcasing how to use `ptrace` to run `printf`: https://github.com/eklitzke/ptrace-call-userspace/blob/master/call_fprintf.c
