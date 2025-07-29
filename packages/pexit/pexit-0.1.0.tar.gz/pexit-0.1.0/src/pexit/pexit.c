#include <assert.h>
#include <ctype.h>
#include <dlfcn.h>
#include <errno.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <unistd.h>

/*
 * `poke_text` and `check_yama` is gratefully copied from
 * https://github.com/eklitzke/ptrace-call-userspace/blob/master/call_fprintf.c
 *
 * Copyright 2016, Evan Klitzke
 *
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 * REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 * INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 * LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 * OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */
int poke_text(pid_t pid, void *where, void *new_text, void *old_text,
              size_t len) {
  if (len % sizeof(void *) != 0) {
    printf("invalid len, not a multiple of %zd\n", sizeof(void *));
    return -1;
  }
  size_t poke_data;
  for (size_t copied = 0; copied < len; copied += sizeof(poke_data)) {
    memmove(&poke_data, new_text + copied, sizeof(poke_data));
    if (old_text) {
      errno = 0;
      long peek_data = ptrace(PTRACE_PEEKTEXT, pid, where + copied, NULL);
      if (peek_data == -1 && errno) {
        perror("PTRACE_PEEKTEXT");
        return -1;
      }
      memmove(old_text + copied, &peek_data, sizeof(peek_data));
    }
    if (ptrace(PTRACE_POKETEXT, pid, where + copied, (void *)poke_data) < 0) {
      perror("PTRACE_POKETEXT");
      return -1;
    }
  }
  return 0;
}

void check_yama(void) {
  FILE *yama_file = fopen("/proc/sys/kernel/yama/ptrace_scope", "r");
  if (yama_file == NULL) {
    return;
  }
  char yama_buf[8];
  memset(yama_buf, 0, sizeof(yama_buf));
  fread(yama_buf, 1, sizeof(yama_buf), yama_file);
  if (strcmp(yama_buf, "0\n") != 0) {
    printf("\nThe likely cause of this failure is that your system has "
           "kernel.yama.ptrace_scope = %s",
           yama_buf);
    printf("You can either rerun `pexit` with `sudo`, or disable Yama by `sudo "
           "sysctl kernel.yama.ptrace_scope=0`\n");
  }
  fclose(yama_file);
}

int exit_process(pid_t pid, int exit_code) {
  if (ptrace(PTRACE_ATTACH, pid, NULL, NULL)) {
    perror("PTRACE_ATTACH");
    check_yama();
    return 1;
  }
  if (waitpid(pid, 0, WSTOPPED) == -1) {
    perror("wait");
    return 1;
  }
  struct user_regs_struct regs;
  if (ptrace(PTRACE_GETREGS, pid, NULL, &regs)) {
    perror("PTRACE_GETREGS");
    goto fail;
  }
  size_t data;
  0 [(char *)&data] = 0x0f;
  1 [(char *)&data] = 0x05;
  if (poke_text(pid, (void *)regs.rip, &data, NULL, sizeof(data))) {
    goto fail;
  }
  regs.rax = 60;
  regs.rdi = exit_code;
  if (ptrace(PTRACE_SETREGS, pid, NULL, &regs)) {
    perror("PTRACE_SETREGS");
    goto fail;
  }
  if (ptrace(PTRACE_DETACH, pid, NULL, NULL)) {
    perror("PTRACE_DETACH");
    goto fail;
  }
  return 0;
fail:
  if (ptrace(PTRACE_DETACH, pid, NULL, NULL)) {
    perror("PTRACE_DETACH");
  }
  return 1;
}

int main(int argc, char **argv) {
  long pid = -1;
  int exit_code = 0;
  if (argc < 2) {
    return -1;
  }
  pid = strtol(argv[1], NULL, 10);
  if (argc >= 3) {
    exit_code = strtol(argv[2], NULL, 10);
  }
  return exit_process((pid_t)pid, exit_code);
}