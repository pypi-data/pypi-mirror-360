
# ------------------------- MINUIT PART ----------------
#  pip3 install iminout  numba_stats numpy
from iminuit import cost, Minuit
import iminuit
from numba_stats import norm, uniform # faster replacements for scipy.stats functions
import numpy as np
from scipy.integrate import quad

#-----------------------------------------------


def print_errors(m2, chi2dof):
    WID =65
    zn = ""
    if chi2dof>1:    zn = "*"
    print("_"*WID)
    print(f" T1/2[minutes]   value     error{zn}       error%        remark")
    print("_"*WID)

    for key in m2.parameters:
        if len(key)==1:
            continue

        err = m2.errors[key]
        val = m2.values[key]
        if val<0:val=-val

        if chi2dof>1:
            err = err * np.sqrt(chi2dof)

        print(f"| {key:7} | {val:11.2f} | {err:9.2f}  |  {100*err/val:6.1f}% |", end="")
        if key=="area":
            print(f" {100/np.sqrt(val):5.2f}%  (sqrt)|")
        # elif key=="fwhm":
        #     print(f" {100*m2.values['fwhm']/m2.values['channel']:5.2f}%  (reso)|")
        else:
            print(f"               |")


    print("_"*WID)
    #if chi2dof>1: print(f"i... errors WERE scaled up  {np.sqrt(chi2dof):.1f}x     for chi2={chi2dof:.1f} !")
    if chi2dof>1: print(f"*... errors WERE scaled up  {np.sqrt(chi2dof):.1f}x     for chi2={chi2dof:.1f} !")


#
# I need to go to chebyshev
#


#------------------------------------------------------------------------
def main(x,y,dy, polorder = None):
    print("__________________________________________________ model entered")


    #    global bin1 # trick for better convergence
    #    bin1 = x[0]





    # --++++++++++++++++++++++++++++------------chi2
    def model_chi2(x,   a,t12):
        global bin1
        f = a * np.exp(-x/t12/60/np.log(2))
        return f






    # ---- for histograms, use cx...
    print(".............iminuit.............>")
    if len(x)<3:
        return None
    c2 = cost.LeastSquares(x, y, dy, model_chi2)


    m2 = Minuit(c2,
                a = 1,
                t12 = 100)

    print_errors(m2, 0) # my nice table at end

    # m2.limits["a", "b", "c"] = (0, None)

    m2.migrad()       # DO MINIMIZATION <<<<<<<<<<
    #m2.minos()
    print(m2.errors) # error view
    print(m2.values) # value view

    print(m2.fmin)   #NICE table
    print("--- parameters in the table are not exact the values -----")
    print(m2.params) # NICE table

    # -------------------- it is important to keep same x vector:
    #                      chebyshev  parametrization uses  -x[0] !
    yf = model_chi2( x,
                     m2.values['a'],
                     m2.values['t12']
    )



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

    print("_________________________________________________")

    # ----- super return"
    res = {}
    res['yf'] = yf

    res['chi2dof'] = chi2dof

    res['valid'] = m2.valid
    res['accurate'] = m2.accurate

    res['noerror'] = True
    #------------ the last one is OR ALL
    if not(m2.valid) or not(m2.accurate):
        res['noerror'] = False

    res['x']       = x
    res['y']       = y

    res['range']    = ( x[0], x[-1] )

    res['t12']  = m2.values['t12']
    res['dt12'] = m2.errors['t12']
    if chi2dof>1:
            res['dt12'] = res['dt12'] * np.sqrt(chi2dof)

    return res
