#!/usr/bin/python
import os
def sanitizeFile(filename):
  print "  file: %s" % filename
  f = open(filename, 'r')
  sanitized = ""
  for line in f:
    if(line.strip() <> "" and line.strip()[0] <> '-'):
      sanitized += line
  print sanitized
  f.close()
  f = open(filename, 'w')
  f.write(sanitized)
  f.close()
def main():
  pwd = os.cwd()
  os.chdir("data")
  for root, dirs, files in os.walk(os.getcwd()):
    print root
    for f in files:
      sanitizeFile("%s/%s" % (root,f))
  os.chdir(pwd)
if __name__ == "__main__":
  main()
