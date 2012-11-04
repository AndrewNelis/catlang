# time
# Note: with access to Python's time, date and calendar modules nearly nothing
# is needed in this category. Just a few convenience functions

from cat.namespace import *
import datetime
ns = NameSpace()

@define(ns, 'now')
def now( cat ) :
    '''
    now : ( -> date_time:dtm)
    
    desc:
        Pushes a datetime.datetime instance representing the current date and time onto the cat.stack
        dtm: the current date and time as a datetime.datetime instance
        
        Example: now => <datetime.datetime instance>
    tags:
        datetime,now
    '''
    cat.stack.push( datetime.datetime.now() )

@define(ns, 'to_msec')
def to_msec( cat ) :
    '''
    to_msec : (datetime:dtm -> int:msec)
    
    desc:
        Computes the length of a time span in milliseconds
        dtm: a datetime instance
        msec: the time in milliseconds
        
        Example: now to_ms => <a big integer>
    tags:
        datetime,time,millisecond
    '''
    ts = cat.stack.pop()
    ts = ts.hour * 3600000.0 + ts.minute * 60000.0 + ts.second * 1000 + ts.microsecond / 1000.0
    cat.stack.push( ts )

@define(ns, 'iso_format')
def iso_format( cat ) :
    '''
    iso_format : (datetime:dtm -> string:iso_date)
    
    descr:
        Returns the ISO formatted date and time string of the datetime on top of the cat.stack
        dtm: the datetime.datetime instance
        iso_date: the date and time in ISO format: yyyy-mm-dd hh:mm:ss (utc_offset)?
        
        Example now iso_format => <formatted datetime string>
    tags:
        datetime,iso,format,date
    '''
    dt = cat.stack.pop()
    cat.stack.push( dt.isoformat() )

@define(ns, 'time')
def getTimeModule( cat ) :
    '''
    time : (-- -> --)
    
    desc:
        Imports the Python time module
        
        Example: time
    tags:
        time,import
    '''
    cat.eval( "'time import" )

def _returnNS() :
    return ns
