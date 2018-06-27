#!/usr/bin/env python

from compiler import Compiler


def main():
    comp = Compiler()
    comp.parseText("test.c")


if __name__ == '__main__':
    main()
