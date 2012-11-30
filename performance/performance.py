#!/usr/bin/python
#
# +-------------------------------------------------------+
# | performance   -- runs deadlock check on several       |
# |                  example files to detect compilation  |
# |                  errors and performance issues        |
# +-------------------------------------------------------+
# | 25-02-08 TW   -- Inception                            |
# | 26-03-08 TW   -- Added Memory measurements,           |
# |                  performed additional reworking       |
# | 09-04-08 TW   -- Saving measurements only when all    |
# |                  measurements are available           |
# |                  Made reading of version info more    |
# |                  robust                               |
# +-------------------------------------------------------+
# |               -- assumes the existence of a subdir    |
# |                  named 'cases' in which the example   |
# |                  files can be found                   |
# +-------------------------------------------------------+
#


import sys,os, subprocess, glob

class Specification:

  def __init__(self, name, dir):
    self. id = name
    self. mcrl2 = dir+name+".mcrl2"
    self. lps = dir+name+".lps"
    self. pbes = dir+name+".pbes"
    self. performance = {}
    self. memory = {}

  def print_memory (self):
    print >> sys. stderr, '\nMemory summary for', self.id + ':'
    print >> sys.stderr, 72*'-'
    self. print_measurement (self. memory)
    print >> sys.stderr, 72*'-'

  def print_performance (self):
    print >> sys. stderr, '\nTime summary for', self.id + ':'
    print >> sys.stderr, 72*'-'
    self. print_measurement (self. performance)
    print >> sys.stderr, 72*'-'

  def store_performance (self, v):
    self. store_measurement (self. performance, v, '.perf')

  def store_memory (self, v):
    self. store_measurement (self. memory, v, '.mem')

  def add_measurements (self, t):
    if t. record_time:
      if not (t. tool in self. performance. keys () ):
        self. performance [t. tool] = [(t. args[0], float (t. time))]
      else:
        self. performance [t. tool]. append ( (t. args[0], float (t. time)) )

    if t. record_memory:
      if not (t. tool in self. memory. keys () ):
        self. memory [t. tool] = [(t. args[0], float (t. memory))]
      else:
        self. memory [t. tool]. append ( (t. args[0], float (t. memory)) )


  #######################
  # LOW LEVEL FUNCTIONS #
  #  AVOID USING THESE  #
  #      DIRECTLY       #
  #######################

  def print_measurement (self, m):
  # prints m to screen
    for tool in m.keys ():
      for measurement in m[tool]:
        print >> sys.stderr, tool, measurement[0], ':', round(measurement[1],2)


  def store_measurement (self, m, version, s):
  # writes dictionary m to disk
  # uses the key in m as a directory
  # uses the first argument of the tuple of m [key]
  # as a sub-subdir, unless this argument is the empty string
  # writes a file named after the second argument of the tuple of
  # m [key] and adds suffix s

    if not(os. path. isdir ('./data')):
      os. mkdir ('./data')

    for tool in m. keys ():

      for measurement in m [tool]:
        
        location = './data/'+tool+'/'
        if not(os. path. isdir (location)):
          os. mkdir (location)
        args = measurement [0]
        if args == '':
          args = 'default'
        location = location + args.replace(' ','__') + '/'
        if not(os. path. isdir (location)):
          os. mkdir (location)
        f = open (location+self.id+s,'a')
        f. write (str(version)+'\t'+str(round(measurement[1],2))+'\n')
        f. close ()

class Tool:

  def __init__ (self, tool, args, recs, lim):
    self. tool = tool
    self. args = args
    self. time = -1.0
    self. memory = -1.0
    self. record_time = False
    self. record_memory = False
    if 'time' in recs: self. record_time = True
    if 'memory' in recs: self. record_memory = True
    self. time_limit = lim
    self. successful = True

  def process (self):
    self. run ()
    self. read_measurements ()

  def run (self):

    print >> sys. stderr, '\nExecuting:', self. tool, ' '. join(self.args)
    if self. record_time:
      print >> sys. stderr, '  Recording Time'
    if self. record_memory:
      print >> sys. stderr, '  Recording Memory'
    print >> sys. stderr, '  Time limit is:', self.time_limit, 'seconds'

    com_list = ['( ulimit -S -t %s ; LANG="" ' %(self.time_limit)]
    if (self. record_memory): com_list. append ('./memusage --progname='+self.tool)
    if (self. record_time): com_list. append ('time -f "TIME: %U %S"')
    com_list. extend ([self. tool])
    com_list. extend (self. args)
    com_list. append (' )')
    if (self. record_time or self. record_memory): 
      com_list. append (' 2> measurements')
    com = ' '. join (com_list)
    #print >> sys. stderr, com
    # ACTUALLY RUN THE TOOL
    try:
      retcode = subprocess. call (com, shell=True)
      print >> sys.stderr, "  Execution",
      if retcode < 0:
        print >> sys.stderr, "FAILED with signal", -retcode
        self. successful = False
      elif retcode > 0:
        extra_info = ""
        if retcode == 24 or retcode == 152 :
          extra_info = "(Time limit exceeded)"
        print >> sys.stderr, "FAILED with code" , retcode, extra_info
        self. successful = False
      else:
        print >> sys.stderr, 'SUCCEEDED'
        self. successful = True
    except OSError, e:
      print >> sys.stderr, "FAILED with error:\n ", e
      self. successful = False


  def read_measurements (self):
    # PRE: self. record_time or self. record_memory
    #      measurements file contains memory and/or time information ordered
    #      by memory first and time second.
    self. time = -1.0
    self. memory = -1.0
    if (os. path. isfile('measurements')) and self. successful:
      f = open ('measurements',"r")
      l = f. readline ()
      while l != '':
        if ('heap' in l) and (self. record_memory):
          a = l. split (' ')
          i = a. index ('peak:') +1
          # DIVISION BY 1024*1024 TO GET MEGABYTES
          self. memory = float(a[i][0:len(a[i])-1])/(1024*1024)
        if ('TIME' in l) and (self. record_time):
          a = l. split (' ')
          i = a. index ('TIME:') +1
          self. time = float(a[i]) + float(a[i+1])
        l = f. readline ()
      f. close ()
  
  def read_version (self):
  # Read the version information from the file "measurements"
    if (os. path. isfile('measurements')):
      f = open ('measurements',"r")
      i = f.readlines()
      f. close ()
      os. remove ('measurements')
      if (len(i) > 0 and 'mCRL2 toolset' in i[0]):
        s = i[0].strip().rsplit(".",1)[1].split(" ", 1)[0]
        return s
    return -1

  
    

class Benchmarks:

  def __init__(self, d):
    # bail out if directory 'd' does not exist

    self. error =  not(os. path. isdir (d))
    self. specs = []
    if not(self. error):
      for file in os. listdir (d):
        if file [-6:] == ".mcrl2": self. specs. append (file[:-6])
    self. specs. sort()
    self. error &= self. specs == []

  def Print (self):
    print >> sys.stderr, "Running the following benchmarks: ", ', '.join (self. specs)

########
#
# Auxiliary function to get the version of the toolsuite
#
########

def get_version ():

  t = Tool ('mcrl22lps', ['--version', ' 2>&1 | grep "mCRL2 toolset" > measurements'], [], 5)
  t. run ()
  return t. read_version ()

#######
#
# MAIN PROGRAM
# 
#######

v = get_version ()
i = ['-1']
if (os. path. isfile('revision')):
  f = open('revision','r')
  i = f. readlines ()
  f. close ()

print >> sys.stderr, "Previous version of the tool suite :", i[-1], "\n"
print >> sys.stderr, "Current version of the tool suite :", v, "\n"

if int(i[-1]) != v:

#  print >> sys.stderr, "Current version of the tool suite :", v, "\n"
  dir_cases = './cases/'
  E = Benchmarks (dir_cases)
  E. Print ()


  p = []
  for spec in E. specs:
    s = Specification (spec, dir_cases)
    f = dir_cases+'nodeadlock.mcf'
    # DEFINE LIST OF TOOLS

    tool_list =\
     [\
     ['mcrl22lps',['', s.mcrl2, s.lps], ['time','memory'], 300],\
     ['mcrl22lps',['-fD', s.mcrl2, s.lps], ['time','memory'], 300],\
     ['mcrl22lps',['-nfD', s.mcrl2, s.lps], ['time','memory'], 300],\
     ['mcrl22lps',['-fD', s.mcrl2, ' | lpsconstelm | lpsparelm | lpssuminst >', s.lps], [], 300],\
     ['lps2pbes',['-f'+str(f), s.lps, ' | pbesrewr > ', s.pbes],[], 300],\
     ['lps2lts',['', s.lps],['time','memory'], 5400],\
     ['lps2lts',['-rjittyc', s.lps],['time','memory'], 300],\
     #['lps2lts',['-rjittyc --alternative', s.lps],['time','memory'], 300],\
     ['lps2lts',['-rjittyc --cached --prune', s.lps],['time','memory'], 300],\
     ['pbes2bool', ['-pquantifier-all', s.pbes],['time','memory'], 14400],\
     ['pbes2bool', ['-pquantifier-all -rjittyc', s.pbes],['time','memory'], 1800] ]

    print >> sys.stderr, "\nStarting experiments for case:", s.id
    for tool in tool_list:
      t = Tool (tool[0], tool[1], tool[2], tool[3])
      t. process ()
      #if t. successful: s. add_measurements (t)
      s. add_measurements (t)

    s.print_performance()
    s.print_memory()

    # add processed specification to the list of processed specs
    p.append(s)

    # remove the above produced artefacts to keep directory clean
    # (not strictly necessary)
    os.remove(s.lps)
    os.remove(s.pbes)
    cfiles = glob.glob("innerc_*") + glob.glob("jittyc_*")
    for cfile in cfiles :
      os.remove(cfile)

  print >> sys. stderr, '\n\nSuccessfully finished measurements.'
  print >> sys. stderr, 'Writing measurements to file ... ',

  for s in p:
    s. store_performance (v)
    s. store_memory (v)

  print >> sys. stderr, 'done'
  print >> sys. stderr, 'Updating revision tag ... ',

  f = open ('revision','w')
  f. write (str(v)+'\n')
  f. close ()
  print >> sys. stderr, 'done'
