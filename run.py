import optparse
import logging
import yaml
import sys
import os
from pool import TaskPool
import cases
from cases.generic_cases import Case 

def run(poolsize, resultsfile):
  log = logging.getLogger('experiments')

  casesdone = []
  if resultsfile is not None:
    if os.path.exists(resultsfile):
      log.info('Found results file ({0}), parsing.'.format(resultsfile))
      try:
        casesdone = yaml.load(open(resultsfile).read()).keys()
        if casesdone:
          log.info('Skipping the following cases because results for them were found:')
      except AttributeError:
        pass
    resultsfile = open(resultsfile, 'a+')
  else:
    resultsfile = sys.stdout

  log.info('Creating taskpool of size {0}'.format(poolsize))
  pool = TaskPool(poolsize)
  try:
    tasks = []
    for task in cases.getcases():
      log.info('Adding task {0}'.format(task))
      if str(task) in casesdone:
        log.info('- ' + str(task))
      else:
        tasks.append(task)
    log.info('Submitting cases and waiting for results.')
    for case in pool.run(*tasks):
      if isinstance(case, (Case)):
        log.info('Got result for {0}'.format(case))
        #resultsfile.write(yaml.dump({str(case): {'sizes': case.sizes, 'times': case.times, 'solutions': case.solutions}}))
        resultsfile.write(yaml.dump({str(case): case.data}))
        resultsfile.flush()
    log.info('Done.')

    pool.close()
    pool.join()
  except KeyboardInterrupt:
    pool.terminate()     
    pool.join()

def runCmdLine():
  parser = optparse.OptionParser(usage='usage: %prog [options] [outfile]')
  parser.add_option('-j', '--jobs', action='store', type='int', dest='poolsize',
                    help='Run N jobs simultaneously.', metavar='N', default=4)
  parser.add_option('-v', action='count', dest='verbosity',
                    help='Be more verbose. Use more than once to increase verbosity even more.')
  options, args = parser.parse_args()
  if not args:
    args = (None,)

  logging.basicConfig()
  if options.verbosity > 0:
    logging.getLogger('experiments').setLevel(logging.INFO)
  if options.verbosity > 1:
    logging.getLogger('taskpool').setLevel(logging.INFO)
  if options.verbosity > 2:
    logging.getLogger('taskpool').setLevel(logging.DEBUG)
    logging.getLogger('experiments').setLevel(logging.DEBUG)
    logging.getLogger('tools').setLevel(logging.INFO)

  run(options.poolsize, args[0])

if __name__ == '__main__':
  runCmdLine()