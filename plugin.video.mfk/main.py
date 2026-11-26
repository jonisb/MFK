import sys

import xbmcplugin


HANDLE = int(sys.argv[1])


def show_main():
  xbmcplugin.endOfDirectory(HANDLE)

def main():
  show_main()


if __name__ == "__main__":
  main()
