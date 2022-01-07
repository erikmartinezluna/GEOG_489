import os, sys
import arcpy 
import multiprocessing 
from multicode_A import worker

import time 
start_time = time.time() 
 
# Input parameters
#clipper = r"C:\Users\marti\Desktop\graduate_doc\GEOG_489\lesson1\USA.gdb\States"
clipper = arcpy.GetParameterAsText(0) 

#tobeclipped = r"C:\Users\marti\Desktop\graduate_doc\GEOG_489\lesson1\USA.gdb\Roads"
tobeclipped = arcpy.GetParameterAsText(1)

#outputeFolder = r"C:\Users\marti\Desktop\graduate_doc\GEOG_489\lesson1\test_folder"
outputeFolder = arcpy.GetParameterAsText(2)
 
def get_install_path():
    ''' Return 64bit python install path from registry (if installed and registered),
        otherwise fall back to current 32bit process install path.
    '''
    if sys.maxsize > 2**32: return sys.exec_prefix #We're running in a 64bit process
  
    #We're 32 bit so see if there's a 64bit install
    path = r'SOFTWARE\Python\PythonCore\2.7'
  
    from _winreg import OpenKey, QueryValue
    from _winreg import HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_64KEY
  
    try:
        with OpenKey(HKEY_LOCAL_MACHINE, path, 0, KEY_READ | KEY_WOW64_64KEY) as key:
            return QueryValue(key, "InstallPath").strip(os.sep) #We have a 64bit install, so return that.
    except: return sys.exec_prefix #No 64bit, so return 32bit path 
    
def mp_handler():
 
    try: 
        # Create a list of object IDs for clipper polygons 
         
        arcpy.AddMessage("Creating Polygon OID list...") 
        print("Creating Polygon OID list...") 
        clipperDescObj = arcpy.Describe(clipper) 
        field = clipperDescObj.OIDFieldName 
      
        idList = [] 
        with arcpy.da.SearchCursor(clipper, [field]) as cursor: 
            for row in cursor: 
                id = row[0] 
                idList.append(id)
 
        arcpy.AddMessage("There are " + str(len(idList)) + " object IDs (polygons) to process.") 
        print("There are " + str(len(idList)) + " object IDs (polygons) to process.") 
 
        # Create a task list with parameter tuples for each call of the worker function. Tuples consist of the clippper, tobeclipped, field, and oid values.
        
        jobs = []
     
        for id in idList:
            jobs.append((clipper,tobeclipped, outputeFolder, field,id)) # adds tuples of the parameters that need to be given to the worker function to the jobs list
 
        arcpy.AddMessage("Job list has " + str(len(jobs)) + " elements.") 
        print("Job list has " + str(len(jobs)) + " elements.") 
 
        # Create and run multiprocessing pool.

        multiprocessing.set_executable(os.path.join(get_install_path(), 'pythonw.exe')) # make sure Python environment is used for running processes, even when this is run as a script tool
 
        arcpy.AddMessage("Sending to pool") 
        print("Sending to pool") 
 
        cpuNum = multiprocessing.cpu_count()  # determine number of cores to use
        print("there are: " + str(cpuNum) + " cpu cores on this machine") 
  
        with multiprocessing.Pool(processes=cpuNum) as pool: # Create the pool object 
            res = pool.starmap(worker, jobs)  # run jobs in job list; res is a list with return values of the worker function
 
        # If an error has occurred report it 
         
        failed = res.count(False) # count how many times False appears in the list with the return values
        if failed > 0:
            arcpy.AddError("{} workers failed!".format(failed)) 
            print("{} workers failed!".format(failed)) 
         
        arcpy.AddMessage("Finished multiprocessing!") 
        print("Finished multiprocessing!") 
 
    except arcpy.ExecuteError:
        # Geoprocessor threw an error 
        arcpy.AddError(arcpy.GetMessages(2)) 
        print("Execute Error:", arcpy.ExecuteError) 
    except Exception as e: 
        # Capture all other errors 
        arcpy.AddError(str(e)) 
        print("Exception:", e)
 
if __name__ == '__main__':   
    mp_handler() 
    print ("--- %s seconds ---" % (time.time() - start_time)) 
    arcpy.AddMessage("--- %s seconds ---" % (time.time() - start_time))