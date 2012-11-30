import specs
import tools
from cases.generic_cases import PBESCase
from cases.generic_cases import Case
import os.path
import logging
import tempfile
import re
import sys
import multiprocessing
import traceback

class Property(PBESCase):
  def __init__(self, name, description, lps, mcf, temppath):
    PBESCase.__init__(self)
    self._name = name
    self.__desc = description
    self._temppath = temppath
    self._prefix = self.__desc + '_' + os.path.splitext(os.path.split(mcf)[1])[0]
    self.lps = lps
    self.mcffile = mcf
  
  def __str__(self):
    return os.path.splitext(os.path.split(self.mcffile)[1])[0]
  
  def _makePBES(self, log):
    '''Generate a PBES out of self.lps and self.mcffile, and apply pbesconstelm
       to it.'''
    try:
      pbesdata = [{},{}]
      pbesdata[0]["tool"] = "lps2pbes"
      pbesdata[0]["arguments"] = ['-f']
      pbesdata[0]["times"] = "unknown"
      pbesdata[0]["memory"] = "unknown"
      (pbes, pbesdata[0]["times"]) = tools.lps2pbes('-f', self.mcffile, stdin=self.lps, timed=True)
      
      pbesdata[1]["tool"] = "lps2pbes"
      pbesdata[1]["arguments"] = []
      pbesdata[1]["times"] = "unknown"
      pbesdata[1]["memory"] = "unknown"
      (pbes, pbesdata[1]["times"]) = tools.pbesrewr(stdin=pbes, timed=True)
      self.data += pbesdata
    except tools.ToolException as e:
      log.error("One of the tools 'lps2pbes' or 'pbesrewr' failed with error {0}".format(e))
      raise e
    return pbes
  
  def phase0(self, log):
    try:
      pbes = self._makePBES(log)
      self.subtasks.append(Solve(self._name, self._prefix, pbes, self._temppath, "-pquantifier-all"))
      self.subtasks.append(Solve(self._name, self._prefix, pbes, self._temppath, "-pquantifier-all", "-rjittyc"))
    except tools.ToolException:
      pass # handled in called function
      
    
  def phase1(self, log):
    for result in self.results:
      self.data += result.data     
    

class Linearise(Case):
  def __init__(self, name, description, mcrl2, temppath, *args):
    Case.__init__(self, name)
    self.__desc = description
    self._temppath = temppath
    self._prefix = self.__desc
    self._mcrl2 = mcrl2
    self.args = args
    assert(len(self.data) == 0)
    self.data = [{}]
    self.data[0]["tool"] = "mcrl22lps"
    self.data[0]["arguments"] = list(self.args)
    self.data[0]["times"] = "unknown"
    self.data[0]["memory"] = "unknown"
  
  def _makeLPS(self, log):
    '''Generate an LPS out of self._mcrl2.'''
    try:
      (lps, self.data[0]["times"]) = tools.mcrl22lps(*self.args, stdin=self._mcrl2, timed=True)
    except tools.ToolException as e:
      log.error("Tool execution failed with error {0}".format(e))
    return lps
  
  def run(self, log):
    self._makeLPS(log)
    
class Instantiate(Case):
  def __init__(self, name, description, lps, temppath, *args):
    Case.__init__(self, name)
    self.__desc = description
    self._temppath = temppath
    self._prefix = self.__desc
    self._lps = lps
    self.args = args
    assert(len(self.data) == 0)
    self.data = [{}]
    self.data[0]["tool"] = "lps2lts"
    self.data[0]["arguments"] = list(self.args)
    self.data[0]["times"] = "unknown"
    self.data[0]["memory"] = "unknown"
  
  def _makeLTS(self, log):
    '''Generate an LTS out of self._lps.'''
    try:
      (dummy, self.data[0]["times"]) = tools.lps2lts(*self.args, stdin=self._lps, timed=True)
    except tools.ToolException as e:
      log.error("Tool execution failed with error {0}".format(e))
    
  def run(self, log):
    self._makeLTS(log)

class Solve(Case):
  def __init__(self, name, description, pbes, temppath, *args):
    Case.__init__(self, name)
    self.__desc = description
    self._temppath = temppath
    self._prefix = self.__desc
    self._pbes = pbes
    self.args = args
    assert(len(self.data) == 0)
    self.data = [{}]
    self.data[0]["tool"] = "pbes2bool"
    self.data[0]["arguments"] = list(self.args)
    self.data[0]["times"] = "unknown"
    self.data[0]["memory"] = "unknown"
    self.data[0]["solution"] = "unknown"
  
  def _solve(self, log):
    '''Generate an LTS out of self._lps.'''
    try:
      (solution, self.data[0]["times"]) = tools.pbes2bool(*self.args, stdin=self._pbes, timed=True)
      self.data[0]["solution"] = solution.strip()
    except tools.ToolException as e:
      log.error("Tool execution failed with error {0}".format(e))
  
  def run(self, log):
    self._solve(log)

class ModelCheckingCase(Case):
  def __init__(self, name, **kwargs):
    Case.__init__(self, name, **kwargs)
    spec = specs.get(name)
    self._mcrl2 = spec.mcrl2(**kwargs)
    self._lps = None
    self.proppaths = []
    self.proppaths += [os.path.join(os.path.split(__file__)[0], 'properties')]
    self.proppaths += [os.path.join(os.path.split(__file__)[0], 'properties', spec.TEMPLATE)]
  
  def __str__(self):
    argstr = ', '.join(['{0}={1}'.format(k, v) for k, v in self._kwargs.items()])
    return '{0}{1}'.format(self._name, ' [{0}]'.format(argstr) if argstr else '')

  def _makeLPS(self, log):
    '''Linearises the specification in self._mcrl2.'''
    log.debug('Linearising {0}'.format(self))
    lpsdata = [{},{},{},{}]
    lpsdata[0]["tool"] = "mcrl22lps"
    lpsdata[0]["arguments"] = ['-nfD']
    lpsdata[0]["times"] = "unknown"
    lpsdata[0]["memory"] = "unknown"
    (lps, lpsdata[0]["times"]) = tools.mcrl22lps('-nfD', stdin=self._mcrl2, timed=True)
    
    lpsdata[1]["tool"] = "lpsconstelm"
    lpsdata[1]["arguments"] = []
    lpsdata[1]["times"] = "unknown"
    lpsdata[1]["memory"] = "unknown"
    (lps, lpsdata[1]["times"]) = tools.lpsconstelm(stdin=lps, timed=True)
    
    lpsdata[2]["tool"] = "lpsparelm"
    lpsdata[2]["arguments"] = []
    lpsdata[2]["times"] = "unknown"
    lpsdata[2]["memory"] = "unknown"
    (lps, lpsdata[2]["times"]) = tools.lpsparelm(stdin=lps, timed=True)
    
    lpsdata[3]["tool"] = "lpssuminst"
    lpsdata[3]["arguments"] = []
    lpsdata[3]["times"] = "unknown"
    lpsdata[3]["memory"] = "unknown"
    (lps, lpsdata[3]["times"]) = tools.lpssuminst(stdin=lps, timed=True)
    self.data += lpsdata
    return lps

  def phase0(self, log):
    '''Generates an LPS and creates subtasks for every property that should be
    verified.'''
    
    # Synchronously generate the LPS that we use for lps2lts and lps2pbes
    try:
      self._lps = self._makeLPS(log)
      
      # Linearisation
      self.subtasks.append(Linearise(self._name, self._prefix, self._mcrl2, self._temppath, ""))
      self.subtasks.append(Linearise(self._name, self._prefix, self._mcrl2, self._temppath, "-fD"))
      
      # State space generation
      self.subtasks.append(Instantiate(self._name, self._prefix, self._lps, self._temppath))
      self.subtasks.append(Instantiate(self._name, self._prefix, self._lps, self._temppath, "-rjittyc"))
      self.subtasks.append(Instantiate(self._name, self._prefix, self._lps, self._temppath, "-rjittyc", "--cached", "--prune"))
      
      # mu-Calculus verification
      for proppath in self.proppaths:
        if os.path.exists(proppath):
          for prop in os.listdir(proppath):
            if not prop.endswith('.mcf'):
              continue
            self.subtasks.append(Property(self._name, self._prefix, self._lps, os.path.join(proppath, prop), 
                                          self._temppath))
        else:
          log.warning("Directory {0} does not exist".format(proppath))
        
    except tools.ToolException as e:
      log.error("One or more tools in the toolchain failed with error {0}".format(e))
    
  def phase1(self, log):
    log.debug('Finalising {0}'.format(self))
    for result in self.results:
      if hasattr(result, "mcffile"):
        # Mu-calculus verification; store in dictionary      
        self.data += [{result.mcffile: result.data}]
      else:
        self.data += result.data

def getcases():
  return \
    [ModelCheckingCase('1394'),
     ModelCheckingCase('ABP', datasize=2),
     ModelCheckingCase('Allow'),
     ModelCheckingCase('Block'),
     ModelCheckingCase('BRP', datasize=3),
     ModelCheckingCase('CABP', datasize=2),
     ModelCheckingCase('Chatbox'),
     ModelCheckingCase('Clobber'),
     ModelCheckingCase('Dining', nphilosophers=8),
     ModelCheckingCase('Domineering'),
     ModelCheckingCase('Lift (Correct)', nlifts=3),
     ModelCheckingCase('Lift (Incorrect)', nlifts=3),
     ModelCheckingCase('Magic square'),
     ModelCheckingCase('Othello')]
    
