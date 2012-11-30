import subprocess
import logging
import tempfile
import threading
import yaml
import os
import re

__LOG = logging.getLogger('tools')

class ToolException(Exception):
  def __init__(self, tool, exitcode, out, err):
    Exception.__init__(self)
    self.__out = out
    self.__err = err
    self.__ret = exitcode
    self.__cmdline = ' '.join(tool)
  
  def __str__(self):
    return 'The commandline "{0}" failed with exit code "{1}".\nStandard error:\n{2}\nStandard output:\n{3}\n'.format(
      self.__cmdline, self.__ret, self.__err, self.__out)

class Timeout(Exception):
  def __init__(self, out, err):
    super(Timeout, self).__init__()
    self.out = out
    self.err = err

class Tool(object):
  def __init__(self, name, log, filter_=None, timed=False, timeout=None, memory=False):
    self.__name = name
    self.__log = log
    self.__timeout = timeout 
    self.__filter = filter_
    self.__timed = timed
    self.__memory = memory
    self.result = None
    self.error = None
  
  def __run(self, stdin, stdout, stderr, timeout, *args):
    cmdline = [self.__name] + [str(x) for x in args]
    self.__log.info('Running {0}'.format(' '.join(cmdline)))
    p = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=stdout, 
                         stderr=stderr)
    if timeout is not None:
      timer = threading.Timer(timeout, p.kill)
      timer.start()
      self.result, self.error = p.communicate(stdin)
      if not timer.isAlive():
        raise Timeout(self.result, self.error)
      else: 
        timer.cancel()
    else:
      self.result, self.error = p.communicate(stdin)
    if p.returncode != 0:
      raise ToolException(cmdline, p.returncode, self.result, self.error)    
  
  def __run_timed(self, stdin, stdout, stderr, timeout, *args):
    timings = tempfile.NamedTemporaryFile(suffix='.yaml', delete=False)
    timings.close()
    self.__run(stdin, stdout, stderr, timeout, '--timings='+timings.name, *args)
    t = yaml.load(open(timings.name).read())
    os.unlink(timings.name)
    self.result = [self.result, t[0]["timing"]]
    
  def __apply_filter(self, filter_):
    m = re.search(filter_, self.error, re.DOTALL)
    if m is not None:
      if isinstance(self.result, list):
        self.result.append(m.groupdict())
      else:
        self.result = [self.result, m.groupdict()]
    else:
      self.__log.error('No match!')
      self.__log.error(filter_)
      self.__log.error(self.error)
      if isinstance(self.result, list):
        self.result.append({})
      else:
        self.result = [self.result, {}]
  
  def __str__(self):
    return self.__name
  
  def __call__(self, *args, **kwargs):
    stdin = kwargs.pop('stdin', None)
    stdout = kwargs.pop('stdout', subprocess.PIPE)
    stderr = kwargs.pop('stderr', subprocess.PIPE)
    filter_ = kwargs.pop('filter', self.__filter)
    timeout = kwargs.pop('timeout', self.__timeout)
    timed = kwargs.pop('timed', self.__timed)
    memory = kwargs.pop('memory', self.__memory)
    if kwargs:
      raise TypeError('Unknown parameter(s) for Tool instance: ' + 
                      ', '.join(['{0}={1}'.format(k, v) 
                                 for k, v in kwargs.items()]))
    if timed:
      self.__run_timed(stdin, stdout, stderr, timeout, *args)
    else:
      self.__run(stdin, stdout, stderr, timeout, *args)
    self.__log.debug(self.error)
    if filter_:
      self.__apply_filter(filter_)
    return self.result

mcrl22lps = Tool('mcrl22lps', __LOG)
lpsconstelm = Tool('lpsconstelm', __LOG)
lpsparelm = Tool('lpsparelm', __LOG)
lpssuminst = Tool('lpssuminst', __LOG)
lps2pbes = Tool('lps2pbes', __LOG)
pbesrewr = Tool('pbesrewr', __LOG)
lps2lts = Tool('lps2lts', __LOG)
pbes2bool = Tool('pbes2bool', __LOG)
