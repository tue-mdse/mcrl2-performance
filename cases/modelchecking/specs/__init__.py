import string
import os.path

class Spec(object):
  def __init__(self, template=None):
    self.TEMPLATE = template
    if self.TEMPLATE is None:
      self.TEMPLATE = self.__class__.TEMPLATE
  @property
  def _template(self):
    return string.Template(open(os.path.join(os.path.split(__file__)[0], 'mcrl2', self.TEMPLATE + '.mcrl2')).read())
  def mcrl2(self):
    return self._template.substitute()

class LiftSpec(Spec):
  def mcrl2(self, nlifts):
    return self._template.substitute(
      nlifts=nlifts,
      lifts=' || '.join(['Lift0({0})'.format(i + 1) for i in range(0, nlifts)]))
    
class PhilosopherSpec(Spec):
  def mcrl2(self, nphilosophers):
    return self._template.substitute(
      nphilosophers=nphilosophers,
      philosophers=' || '.join(['ForkPhil({0})'.format(i+1) for i in range(0, nphilosophers)]))

class LeaderSpec(Spec):
  def mcrl2(self, nparticipants):
    return self._template.substitute(nparticipants=nparticipants)

class DataSpec(Spec):
  def mcrl2(self, datasize):
    return self._template.substitute(
      data='|'.join(['d' + str(i + 1) for i in range(0, datasize)])
    )

class SWPSpec(Spec):
  TEMPLATE = 'swp'
  def mcrl2(self, windowsize, datasize):
    return self._template.substitute(
      windowsize=windowsize,
      data='|'.join(['d' + str(i + 1) for i in range(0, datasize)]),
      initialwindow='[{0}]'.format(','.join(['d1'] * windowsize)),
      emptywindow='[{0}]'.format(','.join(['false'] * windowsize))
    )

__SPECS = {
    'Debug spec': Spec('debugging'),
    '1394': Spec('1394-fin'),
    'ABP':DataSpec('abp'),
    'Allow':Spec('allow'),
    'Block': Spec('block'),
    'BRP': DataSpec('brp'),
    'CABP': DataSpec('cabp'),
    'Chatbox': Spec('chatbox'),
    'Clobber': Spec('clobber'),
    'Dining': PhilosopherSpec('dining'),
    'Domineering': Spec('domineering'),
    'Lift (Correct)': LiftSpec('lift-final'),
    'Lift (Incorrect)': LiftSpec('lift-init'),
    'Magic square': Spec('magic_square'),
    'Othello': Spec('othello')
  }

def get(name):
  return __SPECS[name]
