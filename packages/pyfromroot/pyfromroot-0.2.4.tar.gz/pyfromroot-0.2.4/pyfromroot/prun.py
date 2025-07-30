import ROOT
import glob
import os

import importlib # dynamic import
import sys # to unimport
#import importlib.util

#
#  THIS FILE CANNOT BE EDITED without exiting ROOT everytime
#
#---------------------------------------- functions called from pr_*.py


def register(obj, NAME ):
    """
    For plotting on current canvas or access from CLING,
 each object has to be registered
    """
    #NAME = "fit"
    obj.SetName(NAME)

    # obj.SetTitle(NAME)
    oldg = ROOT.gROOT.GetListOfSpecials().FindObject(NAME)
    if oldg:
        #print(f"i...    removing existing object {NAME}", end="\r"))
        ROOT.gROOT.GetListOfSpecials().Remove(oldg)
    ROOT.gROOT.GetListOfSpecials().Add(obj)
    #print(f"i... object NAME={NAME} registered")
    #ROOT.gROOT.GetListOfSpecials().ls()
    return



#========================================== functions called from C++

# ---------------------------------------------------------------
def import_pr_input():
    """
    get the input from TText object and  eventual arguments
    """
    # 1/ get input
    lin = ROOT.gROOT.GetListOfSpecials().FindObject("pr_input")

    # for a case if called from python code
    if ROOT.addressof(lin)==0:
        print("D... no TText present ... called from python")
        return None,None
    print(f"P... input function found - see: {lin}", lin.Print() )

    inname = lin.GetName()
    intit = lin.GetTitle()

    # print(f"P...    title={intit},  name={inname} " )
    params = []
    if intit.find(" ")>0: # space means parameters follow
        params = intit.split()
        intit = params[0]
        params.pop(0)
        print("i... ARGUMENTS:", params)

    return intit,params # ModName, list



# ---------------------------------------------------------------
def listpy():
    """
    return all pr_*.py files (in the current directory) (in repo dir)
    """
    dirnow = os.getcwd()

    # GO TO repo
    tgt2 = os.path.dirname(os.path.abspath(__file__))
    os.chdir( tgt2 )
    files = glob.glob("pr_*.py")
    if len(files)==0:
        print("X... NO python FILES available (listpy)")
        return None
    # files = [x for x in files if x.find("pr_model_")!=0] # models- I exclude?
    #print("REPO:",tgt2) # I forgot to link inside the repo
    #print("REPO",files)
    corenames = [ os.path.splitext(x)[0].split("pr_")[1] for x in files]
    #print(f"i... modules available in REPO:\n          {corenames}")
    files = [ tgt2+"/"+x for x in files ]
    #- GO back from repo
    os.chdir( dirnow )

    #print("D... looking current dir")
    filescur = glob.glob("pr_*.py")
    #print(f"i... curdir: {filescur}")
    if len(filescur)==0:
        asdqwe541 = 1
        #print("D... NO python FILES available in current directory (listpy)")
        # return None
        #files = filescur
    else:
        corenames = [ os.path.splitext(x)[0].split("pr_")[1] for x in filescur]
        #print(f"i... modules available in CURR:\n          {corenames}")
        # files = [x for x in files if x.find("pr_model_")!=0] # models- I exclude?
        files =  files + filescur





    # print(f"i... modules available: \n{files}\n")
    return files


# ---------------------------------------------------------------
def import_module(intit):


    files = listpy() # get all modules available

    if files is None:
        print("X... no loadable modules found....(@import_module)")
        return None

    # print(files) # all present files
    # print(intit) # module
    module = None
    for ffile in files:
        # ffile may be with a path....
        construct = ffile
        if len(ffile.split("/"))>1:
            construct = construct.split("/")[-1]
        construct =  construct.lstrip("pr_")
        # print(construct)
        construct =  construct.rstrip("py")[:-1] # prioblem w .py
        # print(construct)
        ##print(f" ... searching /{intit}/ in /{ffile}/ <={construct}")
        # this was the last searching
        #print(f" ... searching /{intit}/ in {ffile} ")

        if (intit == construct):
            #print(f"P... got {ffile}")
            #print("i... trying to importlib:", item.GetTitle() )
            # UNimport module first - case there was an error there previously
            unloadname = f"pr_{intit}"
            print(f"i... module /{unloadname}/ ... ", end="")
            try:
                sys.modules.pop( unloadname ) # ffile[:-3]     f"pr_{construct}")
                print(" unloaded successfully, loading now...")
            except:
                print(" not unloaded, loading now...")


            # IMPORT
            #print("D... importing module")
            #module = importlib.import_module( ffile[:-3] ) # older


            spec = importlib.util.spec_from_file_location( "pr_"+intit, ffile )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            #print("D... importing module DONE")
            break

    return module
# ---------------------------------------------------------------
# ---------------------------------------------------------------

#================================================================== MAIN PART

def loadpy( *args, **kwargs ):
    """
    import module - based on the TText object Title created in C++ earlier
    """
    #print("P... in fun listpy")

    intit, params = import_pr_input()
    print(f"i... imported :  intit={intit}, params={params}")

    if intit is None:
        if len(args)!=2:
            print("X... I think I am called from python, but I need two arguments")
            return
        intit = args[0]
        params = args[1].split()
        print(f"i...  module= /{intit}/; params = /{params}/")


    # files = listpy()

    # if files is None:
    #     print("X... no loadable modules found....(loadpy)")
    #     return

    # for ffile in files:
    #     # ffile may be with a path....
    #     construct = ffile
    #     if len(ffile.split("/"))>1:
    #         construct = construct.split("/")[-1]
    #     construct =  construct.lstrip("pr_")
    #     # print(construct)
    #     construct =  construct.rstrip("py")[:-1] # prioblem w .py
    #     # print(construct)
    #     print(f" ...    searching  /{intit}/ in /{ffile}/ <={construct}")
    #     if (intit== construct):
    #         #print(f"P... got {ffile}")
    #         #print("i... trying to importlib:", item.GetTitle() )
    #         # UNimport module first - case there was an error there previously
    #         try:
    #             sys.modules.pop( ffile[:-3] ) # f"pr_{construct}")
    #         except:
    #             print("D... not unloaded", ffile[:-3])


    #         # IMPORT
    #         print("i... importing module")
    #         #module = importlib.import_module( ffile[:-3] ) # older


    #         spec = importlib.util.spec_from_file_location( "pr_"+intit, ffile )
    #         module = importlib.util.module_from_spec(spec)
    #         spec.loader.exec_module(module)

    #         print("i... importing module DONE")

    module = import_module(intit)
    # AND run the modules' main()
    if len(params)>0 and len(kwargs)>0:
        print("g... params and kwargs")
        res = module.main( *params, **kwargs)
    elif len(params)>0:
        print("g... params ", intit, module) # pr_load
        res = module.main( *params)
    else:
        print("g... just main")
        res = module.main()



    # print("i... leaving prun.py")
    return res # I cant do better with adding to Specials and gDirectory
    #======================================================================== END

    print(f"X... no file like pr_{intit}.py found (loadpy)")
    return






#============================================ DO / PROCESS (same and better THAN LOADPY) ===
def do( *args, **kwargs ):
    """
    import module - based on the TText object Title created in C++ earlier
    """

    print("D... args in /DO/", args)
    intit, params = import_pr_input()  # when called from ROOT. None None when from python
    print(f" intit={intit}, params={params}")

    if intit is None: # from PYTHON
        if len(args)!=2:
            print("X... I think I am called from python, I need two arguments")
            return
        intit = args[0]
        params = args[1].split()
        print(f"fi... called from python, searching module /{intit}/; params = /{params}/")



    module = import_module(intit)
    # AND run the modules' main()
    if len(params)>0:
        res = module.main( *params, **kwargs)
    else:
        res = module.main()



    print("i... leaving /DO/")
    return res # I cant do better with adding to Specials and gDirectory
    #======================================================================== END

    print(f"X... no file like pr_{intit}.py found (loadpy)")
    return
