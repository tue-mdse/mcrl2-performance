import os

from TempObj import TempObj

class Case(TempObj):
  def __init__(self, name, **kwargs):
    TempObj.__init__(self)
    self._name = name
    self._kwargs = kwargs
    self._temppath = os.path.join(os.path.split(__file__)[0], 'temp')
    self._prefix = '{0}{1}'.format(self._name, ('_'.join('{0}={1}'.format(k,v) for k,v in self._kwargs.items())))
    self.times = {}
    self.results = []
    self.data = []
  
  def __str__(self):
    argstr = ', '.join(['{0}={1}'.format(k, v) for k, v in self._kwargs.items()])
    return '{0}{1}'.format(self._name, ' [{0}]'.format(argstr) if argstr else '')

class PBESCase(TempObj):
  def __init__(self):
    super(PBESCase, self).__init__()
    self.data = []
  
  def _makePBES(self):
    raise NotImplementedError()
