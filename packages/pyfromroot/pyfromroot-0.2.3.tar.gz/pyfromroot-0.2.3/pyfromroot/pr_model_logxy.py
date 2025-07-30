
# ------------------------- MINUIT PART ----------------
#  pip3 install iminout  numba_stats numpy
#
from iminuit import cost, Minuit
import iminuit
from numba_stats import norm, uniform # faster replacements for scipy.stats functions
import numpy as np

#from termcolor import colored
from console import fg,fx
import re

#
# NONONO.... I need to go to chebyshev
#




def main(x,y,dy, polorder = 1):
    print("__________________________________________________ logxy ")
    #global bin1 # trick for better convergence
    #bin1 = x[0]






    def print_errors(m2, chi2dof):
        """
        I allow a,b,c,d,...  I have longer decimal places
        """
        WID =65
        print
        print("_"*WID)
        zn = ""

        form = " np.exp( "
        xpol = len(m2.parameters)
        xpolm = len(m2.parameters)

        if chi2dof>1:    zn = "*"
        print(f" name              value     error{zn}       error%   remark")
        print("_"*WID)
        for key in m2.parameters:
            #if len(key)==1:
            #    continue

            err = m2.errors[key]
            val = m2.values[key]
            #if val<0:val=-val # WHY THIS?

            if chi2dof>1:
                err = err * np.sqrt(chi2dof)

            print(f"| {key:7} | {val:12.9f} | {err:9.9f}  |  {100*err/val:6.1f}% |", end="")

            xpol-=1
            form=f"{form} {val:.9f}{'*np.log(x)'*xpol}"
            if xpol!=0: form+=" +"


            if key=="area":
                print(f" {100/np.sqrt(val):5.2f}%  (sqrt)|")
            elif key=="fwhm":
                print(f" {100*m2.values['fwhm']/m2.values['channel']:5.2f}%  (reso)|")
            else:
                print(f"               |")


        print("_"*WID)
        if chi2dof>1: print(f"*... errors WERE scaled up  {np.sqrt(chi2dof):.1f}x     for chi2={chi2dof:.1f} !")
        form = form+" )"
        print("\n",form,"\n") # FORMULA
        form1 = re.sub("\(x\)", f"({x[0]})", form)
        form2 = re.sub("\(x\)", f"({x[-1]})", form)

        print( eval(form1) ,"=", form1)

        print( eval(form2) ,"=", form2)









    def model_chi20(x,   a):
        f = a
        return f
    def model_chi21(x,   a,b):
        #print(a,b)
        f = np.exp(a* np.log(x) + b)
        return f
    def model_chi22(x,   a,b,c):
        f = np.exp( a*np.log(x)*np.log(x) + b*np.log(x) +c)
        return f
    def model_chi23(x,   a,b,c,d):
        f = np.exp( a*np.log(x)*np.log(x)*np.log(x) + b*np.log(x)*np.log(x) +c*np.log(x) +d)
        return f
    def model_chi24(x,   a,b,c,d,e):
        f = np.exp( a*np.log(x)*np.log(x)*np.log(x)*np.log(x) + b*np.log(x)*np.log(x)*np.log(x) +c*np.log(x)*np.log(x)+d*np.log(x)+e)
        return f
    def model_chi25(x,   a,b,c,d,e,f):
        f = np.exp( a*np.log(x)*np.log(x)*np.log(x)*np.log(x)*np.log(x) + b*np.log(x)*np.log(x)*np.log(x)*np.log(x) +c*np.log(x)*np.log(x)*np.log(x)+d*np.log(x)*np.log(x)+e*np.log(x)+f)
        return f


    # ---- for histograms, use cx...
    print(".............iminuit.............> logxy")
    c2 = cost.LeastSquares(x, y, dy, locals()["model_chi2"+str(polorder)] )


    #estimates
    if y[0]>y[-1]:
        esa = -0.1
    else:
        esa = 0.1

    if min(y)<=0:
        print("X... I CANNOT FIT y values less than 0" )
        return None


    if polorder==0:

        m2 = Minuit(c2,
                    a=y.mean()  )
    elif polorder==1:

        m2 = Minuit(c2,
                    a=esa, b = np.log(y.mean())  )
    elif polorder==2:

        m2 = Minuit(c2,
                    a=0.1**2, b=0.1, c=np.log(y.mean()  ) )
    elif polorder==3:

        m2 = Minuit(c2,
                    a=0.1**3,b=0.1**2,c=0.1,d=np.log(y.mean()  ) )
    elif polorder==4:

        m2 = Minuit(c2,
                    a=0.1**4,b=0.1**3,c=0.1**2,d=0.1,e=np.log(y.mean() ) )
    elif polorder==5:

        m2 = Minuit(c2,
                    a=0.1**5,b=0.1**4,c=0.1**3, d=0.1**2, e=0.1, f=np.log(y.mean() ) )
    else:
        print("X...  unknown polynomial order to me ")
        return None




    # m2.limits["a", "b", "c"] = (0, None)

    m2.migrad()       # DO MINIMIZATION <<<<<<<<<<
    #print(m2.errors) # error view
    #print(m2.values) # value view

    print(m2.fmin)   #NICE table
    print(m2.params) # NICE table



    # ------ create parameter list on the fly
    paramnames = [ chr(ord('a')+i) for i in  range(0,polorder+1)]
    #paramnames =  list("abce")
    params =  [ m2.values[i] for i in paramnames ]



    yf = locals()["model_chi2"+str(polorder)]( x, *params )

    xf10 = np.arange( x[0],x[-1], (x[-1]-x[0])/100 )
    yf10 = locals()["model_chi2"+str(polorder)]( xf10, *params )


    chi2dof=m2.fval/(len(x) - m2.nfit)
    if False:
        print("   FCN =",m2.fval)
        print(" points=",len(x))
        print("   par = ",m2.nfit)
        print("  Chi2 = ", chi2dof)
    print_errors(m2, chi2dof) # my nice table at end

    print()
    print(f"i... FIT IS valid ... {m2.valid} ")
    print(f" ... and accurate ... {m2.accurate}")
    #print(f" ... and all ok   ... {NOError}")



    if not(m2.valid):
        print( "f{fg.red}X... ____________FIT SEEMS NOT  VALID___________ {fg.default}" )
    elif  not(m2.accurate):
        print( "f{fg.yellow}X... ____________VALID BUT NOT ACCURATE___________ {fg.default}" )
    else:
        print( "f{fg.green}i...    fit seems OK to me {fg.default}" )


    res = {}
    res['yf'] = yf
    res['yf10'] = yf10
    res['xf10'] = xf10

    res['chi2dof'] = chi2dof

    res['valid'] = m2.valid
    res['accurate'] = m2.accurate

    res['noerror'] = True
    #------------ the last one is OR ALL
    if not(m2.valid) or not(m2.accurate):
        res['noerror'] = False

    res['logx']       = False
    res['logy']       = False


    res['range']    = ( x[0], x[-1] )

    for i in paramnames:
        res[i] = m2.values[i]
        res[f"d{i}"] = m2.errors[i]







    print("_________________________________________________logxy")
    return res
