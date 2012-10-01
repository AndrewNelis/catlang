# input/output

# Help on function 'colored' in module 'termcolor':
# 
# colored(text, color=None, on_color=None, attrs=None)
#     Colorize text. (Not all colors work on all terminals on all platforms.)
#     
#     Available text colors:
#         red, green, yellow, blue, magenta, cyan, white.
#     
#     Available text highlights:
#         on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.
#     
#     Available attributes:
#         bold, dark, underline, blink, reverse, concealed.
#     
#     Example:
#         colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
#         colored('Hello, World!', 'green')

from cat.namespace import *
ns = NameSpace()

@define(ns, 'write')
def write( cat ) :
    '''
    write : (string:text string:color -> --)
    
    desc:
        outputs the text representation of a value to the console in the specified color
        text: the text to be output to the console
        color: the color the text should be. One of:
                'blue':
                'cyan'
                'green'
                'grey'
                'magenta'
                'red'
                'white'
                'yellow'
              If the color string is empty (i.e. "") then 'black' is assumed
        
        Example: "Two letter country code: " 'magenta write
    tags:
        console,text,color,output,write,prompt
    '''
    color, obj = cat.stack.pop_2()
    
    if not color :
        color = None
    
    if isinstance(obj, (list, tuple)) :
        cat.output( cat.ns._formatList(obj, 4), color, comma=True )
    
    elif isinstance(obj, dict) :
        cat.output( repr(obj), color, comma=True )
    
    else :
        if not isinstance(obj, basestring) :
            obj = str( obj )
        
        lines = obj.split( "\\n" )  # this is curious but it works
        
        for line in lines:
            cat.output( line, color, comma=True )

@define(ns, 'writeln,print')
def writeln( cat ) :
    '''
    writeln : (string:text string:color -> --)
    print   : (string:text string:color -> --)
    
    desc:
        Outputs the text representation of a value to the console in the
        requested color. The line is automatically terminated with a linefeed
        text: the text to output
        color: the color to use:
                'blue':
                'cyan'
                'green'
                'grey'
                'magenta'
                'red'
                'white'
                'yellow'
              If the color string is empty (i.e. "") then 'black' is assumed
        
        Example: "Hello, world!" 'cyan writeln
                 "Hello, dolly!" 'grey print
    tags:
        console,display,text,color,output
    '''
    color, obj = cat.stack.pop_2()
    
    if not color :
        color = None
    
    if isinstance(obj, (list, tuple)) :
        cat.output( cat.ns._formatList( obj, 4 ), color )
    
    elif isinstance(obj, dict) :
        cat.output( repr(obj), color )
    
    else :
        if not isinstance(obj, basestring)  :
            obj = str( obj )
        
        lines = obj.split( "\\n" )  # this is curious but it works
        
        for line in lines:
            cat.output( line, color )

@define(ns, 'readln')
def readln( cat ) :
    '''
    readln : (-> string:input_line)
    
    desc:
        Inputs a string from the console
        no conversion of any sort is done
        for a prompt, use write first e.g. "date: " write readln
        input_line: the string received from the user
        
        Example: "Two letter country code: " 'magenta write readln => <user's response>
    tags:
        console,input,user
    '''
    line = raw_input( "" )
    cat.stack.push( line )

@define(ns, 'file_reader')
def file_reader( cat ) :
    '''
    file_reader : (string:filePath -> file_descriptor:istream)
    
    desc:
        Creates an input stream from a file name
        filePath: the file path to the input file
        istream: file descriptor for the input file
        
        Example: 'catlang.cfg file_reader => <file descriptor>
    tags:
        streams,input,file,descriptor
    '''
    fName = cat.stack.pop()
    
    if isinstance(fName, basestring) :
        cat.stack.push( open(fName, 'r') )
    
    else :
        raise ValueError, "file_reader: File name must be a string"

@define(ns, 'file_writer')
def file_writer( cat ) :
    '''
    file_writer : (string:filePath -> file_descriptor:ostream)
    
    desc:
        creates an output stream from a file name
        filePath: the file path to the target file (for output)
        ostream: file descriptor for the file
        
        Example: 'work.txt file_writer => <file descriptor>
    tags:
        streams,output,file,write
    '''
    fName = cat.stack.pop()
    
    if isinstance(fName, basestring) :
        cat.stack.push( open(fName, 'w') )
    
    else :
        raise ValueError, "file_writer: File name must be a string"

@define(ns, 'file_exists')
def file_exists( cat ) :
    '''
    file_exists : (string:filePath -> bool:TF)
    
    desc:
        Returns a boolean value indicating whether a file or directory exists
        filePath: the path to the file
        TF: True if the file exists, False otherwise
        
        Example: 'Cat/catlang.cfg file_exists => True
    tags:
        streams,file,exist
    '''
    from os import path
    
    name = cat.stack.pop()
    
    if isinstance(name, basestring) :
        cat.stack.push( path.exists(name) )
    
    else :
        raise ValueError, "file_exists: File name must be a string"

@define(ns,'show_path')
def show_path( cat ) :
    '''
    show_path : (string:fileName -> --)
    
    desc:
        Displays the absolute path to the file
        fileName: the file name
        
        Example: 'Cat/catlang.cfg show_path
    tags:
        streams,file,path,display
    '''
    from os import path
    
    name = cat.stack.pop()
    
    if isinstance(name, basestring) :
        cat.output( path.abspath(name), cat.ns.info_colour )
    
    else :
        raise ValueError, "show_path: File name must be a string"

@define(ns,'get_path')
def get_path( cat ) :
    '''
    get_path : (string:fileName -> --)
    
    desc:
        Returns the absolute path to the file on top of the stack
        fileName: the file name
        
        Example: 'Cat/catlang.cfg get_path => /WW/Projects/TimeStack/Cat/catlang.cfg
    tags:
        streams,file,path
    '''
    from os import path
    
    name = cat.stack.pop()
    
    if isinstance(name, basestring) :
        cat.stack.push( path.abspath(name) )
    
    else :
        raise ValueError, "get_path: File name must be a string"

@define(ns, 'read_bytes')
def read_bytes( cat ) :
    '''
    read_bytes : (int:nr_bytes file_descriptor:istream -> string:bytes)
    
    desc:
        Reads a number of bytes into a string from an input stream
        nr_bytes: number of bytes to read.
                  If < 0, all bytes in the file will be read
        istream:  input file descriptor
        bytes: the bytes read in
        
        Example: 23 fd read_bytes => <string of 23 bytes>
    tags:
        streams,string,input,file,bytes,read
    '''
    fd, n = cat.stack.pop_2()
    buf   = fd.read( n )
    cat.stack.push( buf )

@define(ns, 'write_bytes')
def write_bytes( cat ) :
    '''
    write_bytes : (string:bytes file_descriptor:ostream -> ostream)
    
    desc:
        Writes a string (byte array) to an output stream
        ostream: output file descriptor
        bytes: string to be output
        
        Example: "this is output text\n" fd write_bytes => fd
    tags:
        streams,string,output,file
    '''
    fd, buf = cat.stack.pop_2()
    fd.write( buf )
    fd.flush
    cat.stack.push( fd )

@define(ns, 'close_stream')
def close_stream( cat ) :
    '''
    close_stream : (file_descriptor: stream -> )
    
    desc:
        Closes a stream
        stream: a file descriptor
        
        Example: fd close_stream
    tags:
        streams,input,output,close
    '''
    from types import FileType
    fd = cat.stack.pop()
    
    if not isinstance(fd, file) :
        cat.stack.push( fd )
        raise ValueError, "close_stream: Expect a file descriptor on top of cat.stack"
    
    fd.close()

@define(ns, 'is_closed')
def isFileClosed( cat ) :
    '''
    is_closed : (file_descriptor:fd -> bool:TF)
    
    desc:
        Tests whether or not the file has been closed. Pushes True onto the
        stack if the file has been closed; False otherwise
        fd: file descriptor for the file to be tested
        TF: True or False
        
        Example: fd is_closed => <True or False>
    tags:
        streams,close,file,input,output
    '''
    fd = cat.stack.pop()
    cat.stack.push( fd.closed )

@define(ns, 'file_to_list')
def fileToList( cat ) :
    '''
    file_to_list : (file_descriptor:fd -> list:records)
    
    desc:
        Read the entire contents of a file to a list
        Records terminated by line-end character(s) are expected
        The file is NOT closed
        fd: the file descriptor of the file to read
        records: the records read as strings with terminal newline included
        
        Example: fd file_to_list => <list of records>
    tags:
        streams,input,read,list
    '''
    fd  = cat.stack.pop()
    cat.stack.push( fd.readlines() )

@define(ns, 'list_to_file')
def listToFile( cat ) :
    '''
    list_to_file : (list:src file_descriptor:fd -> file_descriptor:fd)
    
    desc:
        Writes the contents of the list to the output file
        Each element of the list is appended to the file
        If a list element is to be a 'record' it must be terminated with a newline
        The output file is NOT closed
        src: the list to be output
        fd: the file descriptor for the output file
        
        Example: ["item 1" "item 2"] list fd list_to_file => fd
    tags:
        streams,output,write,list
    '''
    fd, lst = cat.stack.pop_2()
    
    if not isinstance(lst, (list,tuple)) :
        lst = [lst]
    
    fd.writelines( lst )
    fd.flush()
    cat.stack.push( fd )

@define(ns, 'records_to_file')
def recordsToFile( cat ) :
    '''
    records_to_file : (list:src file_descriptor:fd -> file_descriptor:fd)
    
    desc:
        Writes each element of the list to the output file as a string
        terminated by a newline. If the string has no terminal newline, one is
        appended before writing it to the output file.
        The output file is NOT closed
        src: the list of records to be written to the file
        fd: the output file descriptor
        
        Example: ["record 1" "record 2"] list fd records_to_file => fd
    tags:
        streams,output,write,list
    '''
    fd, lst = cat.stack.pop_2()
    
    if not isinstance(lst, (list, tuple)) :
        lst = [lst]
    
    lst    = [str(x) for x in lst]
    newLst = [ ]
    
    for item in lst:
        if item.endswith("\n") :
            newLst.append( item )
        
        else :
            newLst.append( item + "\n" )
    
    fd.writelines( newLst )
    fd.flush()
    cat.stack.push( fd )

# much more i/o and file stuff available through: 'os.path import

def _returnNS() :
    return ns
