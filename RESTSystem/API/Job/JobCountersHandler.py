
import types
import os
import shutil
import json
from tornado import web, gen
from RESTDIRAC.RESTSystem.Base.RESTHandler import WErr, WOK, TmpDir, RESTHandler
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.WorkloadManagementSystem.Client.SandboxStoreClient import SandboxStoreClient
from DIRAC.Core.Utilities import List, CFG
from DIRAC.Core.Utilities.JDL import loadJDLAsCFG, dumpCFGAsJDL

class JobCountersHandler( RESTHandler ):

  ROUTE = "/jobs/summary"

  @web.asynchronous
  @gen.engine
  def get( self ):
    selDict = {}
    args = self.request.arguments
    if 'allOwners' not in args:
      selDict[ 'Owner' ] = self.getUserName()
    rpc = RPCClient( "WorkloadManagement/JobMonitoring" )
    if 'group' not in args:
      group = [ 'Status' ]
    else:
      group = args[ 'group' ]
    result = yield self.threadTask( rpc.getCounters, group, selDict )
    if not result[ 'OK' ]:
      self.log.error( "Could not retrieve job counters", result[ 'Message' ] )
      raise WErr( 500 )
    data = {}
    for cDict, count in result[ 'Value' ]:
      cKey = "|".join( [ cDict[ k ] for k in group ] )
      data[ cKey ] = count
    self.finish( data )
