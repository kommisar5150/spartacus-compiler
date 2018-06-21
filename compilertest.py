#!/usr/bin/env python

from compilerBeta import CompilerTest


def main():
    compiler = CompilerTest()
    compiler.parseText("test.c")


if __name__ == '__main__':
    main()
