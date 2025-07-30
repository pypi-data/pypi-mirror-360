
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
# I need to go to chebyshev -no good for calibrations....
#

# def print_errors(m2, chi2dof):
#     """
#     I allow a,b,c,d,...  I have longer decimal places
#     """
#     WID =65
#     print
#     print("_"*WID)
#     zn = ""
#     if chi2dof>1:    zn = "*"
#     print(f" name              value     error{zn}       error%   remark")
#     print("_"*WID)
#     for key in m2.parameters:
#         #if len(key)==1:
#         #    continue

#         err = m2.errors[key]
#         val = m2.values[key]
#         #if val<0:val=-val # why the hell this?

#         if chi2dof>1:
#             err = err * np.sqrt(chi2dof)

#         print(f"| {key:7} | {val:11.4f} | {err:9.4f}  |  {100*err/val:6.1f}% |", end="")
#         if key=="area":
#             print(f" {100/np.sqrt(val):5.2f}%  (sqrt)|")
#         elif key=="fwhm":
#             print(f" {100*m2.values['fwhm']/m2.values['channel']:5.2f}%  (reso)|")
#         else:
#             print(f"               |")


#     print("_"*WID)
#     if chi2dof>1: print(f"*... errors WERE scaled up  {np.sqrt(chi2dof):.1f}x     for chi2={chi2dof:.1f} !")
#     print(f"i... Chebyshev parameters are not real! they are for shifted X")




def main(x,y,dy, polorder = None):
    print("__________________________________________________ chebypol")

    global bin1 # trick for better convergence
    bin1 = x[0]






    def print_errors(m2, chi2dof):
        """
        I allow a,b,c,d,...  I have longer decimal places
        """
        WID =65
        print
        print("_"*WID)
        zn = ""

        form = "  "
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
            # if val<0:val=-val #why the hell this?

            if chi2dof>1:
                err = err * np.sqrt(chi2dof)

            print(f"| {key:7} | {val:12.6f} | {err:9.6f}  |  {100*err/val:6.1f}% |", end="")

            xpol-=1
            form=f"{form} {val:.6f}{'*x'*xpol}"
            if xpol!=0: form+=" +"


            if key=="area":
                print(f" {100/np.sqrt(val):5.2f}%  (sqrt)|")
            elif key=="fwhm":
                print(f" {100*m2.values['fwhm']/m2.values['channel']:5.2f}%  (reso)|")
            else:
                print(f"               |")


        print("_"*WID)
        if chi2dof>1: print(f"*... errors WERE scaled up  {np.sqrt(chi2dof):.1f}x     for chi2={chi2dof:.1f} !")
        #print("\n",form) # FORMULA
        # form1 = re.sub("x", f"{x[0]}", form)
        # form2 = re.sub("x", f"{x[-1]}", form)
        # print(form1)
        # print( eval(form1) )
        # print(form2)
        # print( eval(form2) )
        print(f"i... Chebyshev parameters are not real! they are for shifted X")





    def model_chi20(x,   a):
        f = np.polynomial.Chebyshev( [a] )(x-bin1)
        return f
    def model_chi21(x,   a,b):
        f = np.polynomial.Chebyshev( [a,b] )(x-bin1)
        return f
    def model_chi22(x,   a,b,c):
        f = np.polynomial.Chebyshev( [a,b,c] )(x-bin1)
        return f
    def model_chi23(x,   a,b,c,d):
        f = np.polynomial.Chebyshev( [a,b,c,d] )(x-bin1)
        return f
    def model_chi24(x,   a,b,c,d,e):
        f = np.polynomial.Chebyshev( [a,b,c,d,e] )(x-bin1)
        return f
    def model_chi25(x,   a,b,c,d,e,f):
        f = np.polynomial.Chebyshev( [a,b,c,d,e,f] )(x-bin1)
        return f



    # ---- for histograms, use cx...
    print(".............iminuit.............>")
    c2 = cost.LeastSquares(x, y, dy, locals()["model_chi2"+str(polorder)] )

    if polorder==0:

        m2 = Minuit(c2,
                    a=y.mean()  )
    elif polorder==1:

        m2 = Minuit(c2,
                    a=y[-1]-y[0], b=y.mean()  )
    elif polorder==2:

        m2 = Minuit(c2,
                    a=0.1**2, b=0.1, c=y.mean()  )
    elif polorder==3:

        m2 = Minuit(c2,
                    a=0.1**3,b=0.1**2,c=0.1,d=y.mean()  )
    elif polorder==4:

        m2 = Minuit(c2,
                    a=0.1**4,b=0.1**3,c=0.1**2,d=0.1,e=y.mean() )
    elif polorder==5:

        m2 = Minuit(c2,
                    a=0.1**5,b=0.1**4,c=0.1**3, d=0.1**2, e=0.1, f=y.mean() )
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
        print( f"{fg.red}X... ____________FIT SEEMS NOT  VALID___________ {fg.default}" )
    elif  not(m2.accurate):
        print( f"{fg.yellow}X... ____________VALID BUT NOT ACCURATE___________ {fg.default}" )
    else:
        print( f"{fg.green}i...    fit seems OK to me {fg.default}" )



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





    print(f"i... Chebyshev parameters are not real! they are for shifted X")
    print("_________________________________________________pocall")
    return yf
