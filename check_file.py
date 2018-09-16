#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import errno
import os
import sys

import mistune
import requests

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[%sm"
BOLD_SEQ = "\033[1m"

RED = "1;91"
YELLOW = "1;33"
GREEN = "1;32"
WHITE = "1"


class Result(enum.Enum):
    Skipped = -1
    Success = 1
    Failed = 0


def make_result(bool_res):
    return Result.Success if bool_res else Result.Failed


class FakeRenderer(mistune.Renderer):
    files_to_check = None

    def __init__(self, **kwargs):
        super(FakeRenderer, self).__init__(**kwargs)
        self.files_to_check = []

    def link(self, link, title, text):
        self.files_to_check.append(link)
        return super(FakeRenderer, self).link(link, title, text)

    def image(self, src, title, text):
        self.files_to_check.append(src)
        return super(FakeRenderer, self).link(src, title, text)


def check_file(base_dir, link):
    if link.startswith("http://") or link.startswith("https://"):
        try:
            return make_result(requests.head(link, timeout=1).ok)
        except requests.exceptions.RequestException as e:
            print(e)
            return Result.Failed
    else:
        link = link.split("#", 1)[0]
        if not link:
            return Result.Skipped
        return make_result(os.path.exists(os.path.join(base_dir, link)))


def test_files():
    bad_files = 0
    total_files = 0
    bad_links = 0
    total_links = 0
    for fname in sys.argv[1:]:
        print("**** Checking:", COLOR_SEQ % WHITE, fname, RESET_SEQ, "****")
        with open(fname, "r", encoding="utf-8") as f:
            base_dir = os.path.dirname(fname)
            data = f.read()
            renderer = FakeRenderer()
            parser = mistune.Markdown(renderer)
            parser(data)
            file_bad_links = 0
            for i in renderer.files_to_check:
                total_links += 1
                result = check_file(base_dir, i)
                if result == Result.Failed:
                    file_bad_links += 1
                    print(COLOR_SEQ % RED, "    Failed:", RESET_SEQ, i)
                elif result == Result.Success:
                    print(COLOR_SEQ % GREEN, "    Success:", RESET_SEQ, i)
                elif result == Result.Skipped:
                    print(COLOR_SEQ % YELLOW, "    Skipped:", RESET_SEQ, i)
            total_files += 1
            if file_bad_links:
                bad_files += 1
                bad_links += file_bad_links
    print()
    print("Check finished, checked %s files with %s links" % (total_files, total_links), sep="")
    if bad_files:
        print(COLOR_SEQ % RED, "Errors detected: %s bad files with %s bad links" % (bad_files, bad_links), RESET_SEQ,
              sep="")
        return errno.ENOENT
    else:
        print(COLOR_SEQ % WHITE, "No errors detected", RESET_SEQ, sep="")
        return 0


sys.exit(test_files())
