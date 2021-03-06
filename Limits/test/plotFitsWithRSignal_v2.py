import sys
region = sys.argv[-1]

import ROOT as rt
import random
rt.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
rt.gStyle.SetOptStat(111111)
rt.gStyle.SetOptFit(1011)
rt.gStyle.SetStatH(0.30)
rt.gStyle.SetStatW(0.20)
import math
import numpy as np
from array import array
from scipy.special import gammaln

# plot dataObs + r*Sig for atleast r = 0 and r = min(deltaNLL)

#regions = ["lowCut","lowSVJ2","highCut","highSVJ2"]
regions = [region]

# disable root garbage collection
def ngc(obj):
    rt.SetOwnership(obj,False)

def NLL(r,s,b,d):
    # L_s+b/L_b
#    return r*s - d*math.log(1+r*s/b)
    # L_s+b
    if r*s+b<=0: return 0
#    return (r*s+b)-d*math.log(r*s+b)-gammaln(d+1)
    return (r*s+b)-d*math.log(r*s+b)

def makeRHist(r,region,mass,hist_data,hist_sig,ybounds,draw=False,hist0=None):
        rStr = "{:.3f}".format(r).replace(".","p").replace("-","n")
        hist_R = hist_data.Clone("data + "+(str(r) if hist0 is not None else "")+"*signal"); ngc(hist_R)

        hist_R.Add(hist_data, hist_sig, 1, r)
        hist_R.SetMarkerStyle(20)
        hist_R.SetMarkerColor(rt.kBlack)
        hist_R.SetLineColor(rt.kBlack)

        # remove negative bins (and bins w/ very small # events from signal)
        for iBin in range(hist_R.GetNbinsX()+1):
            if hist_R.GetBinContent(iBin)<0.9:
                hist_R.SetBinContent(iBin,0)
                hist_R.SetBinError(iBin,0)

        # remove overflow
        hist_R.SetBinContent(hist_R.GetNbinsX()+1,0)

        for iBin in range(1,hist_R.GetNbinsX()+1):
            # use poisson errors on actual counts in histogram
            binc = hist_R.GetBinContent(iBin)
            if binc==0.: continue
            hist_R.SetBinError(iBin,rt.Math.gamma_quantile_c((1-0.6827)/2.,binc+1,1)-binc)

        #if hist_R.GetMinimum() < 0:
        #    print("NEGATIVE BIN: {} {} {} {}".format(region, mass, r, hist_R.GetMinimum()))
        #    continue
        hist_R.SetTitle(region+" "+mass+" "+rStr)
        hist_R.GetYaxis().SetRangeUser(ybounds[0],ybounds[1])
        hist_NLL = hist_R.Clone("NLL "+hist_R.GetName()); ngc(hist_NLL)
        
        if "high" in region:
            fitFunc = rt.TF1("fitFunc","[0]*pow(x/13000, -[1])",1500,6000); ngc(fitFunc)
            if "SVJ" in region:
                fitFunc.SetParameter(0,4.3e-6)
                fitFunc.SetParameter(1,7.3)
            else:
                fitFunc.SetParameter(0,0.0018)
                fitFunc.SetParameter(1,6.4)
            fitFunc.SetParLimits(0, 0.5e-6, 0.5)
            fitFunc.SetParLimits(1, 1, 30)
        elif "low" in region:
            fitFunc = rt.TF1("fitFunc","[0]*pow(1 - x/13000, [2]) * pow(x/13000, -[1])",1500,6000); ngc(fitFunc)
            if "SVJ" in region:
                fitFunc.SetParameter(0,4.4e-5)
                fitFunc.SetParameter(1,7.5)
                fitFunc.SetParameter(2,4.2)
            else:
                fitFunc.SetParameter(0,0.08)
                fitFunc.SetParameter(1,6.0)
                fitFunc.SetParameter(2,6.7)
            fitFunc.SetParLimits(0, 0.5e-6, 0.5)
            fitFunc.SetParLimits(1, 1, 30)
            fitFunc.SetParLimits(2, 1, 16)
        else:
            exit(0)
        hist_R.Fit(fitFunc,"Q0")

        #hist_NLL.Reset()
        hist_NLL.SetName("hist_NLL")
        hist_NLL.SetTitle(";m_{T};deltaNLL")
        hist_NLL.SetStats(0)
        for iBin in range(hist_NLL.GetNbinsX()+1):
            x = hist_NLL.GetXaxis().GetBinCenter(iBin)
            d = hist_data.GetBinContent(iBin)
            s = hist_sig.GetBinContent(iBin)
            b = fitFunc.Eval(x)
            hist_NLL.SetBinContent(iBin, NLL(r,s,b,d))
            hist_NLL.SetBinError(iBin, 0)
        if hist0 is not None:
            hist_NLL.Add(hist0,-1)
        nll = hist_NLL.Integral(1,hist_NLL.GetNbinsX())
        hist_NLL.GetYaxis().SetRangeUser(-5,10)
#        hist_NLL.Print("all")
        
        if draw:
            print("data: {}, sig: {}, d+s: {}, r: {}, chi2/ndf: {}, nll: {}".format(hist_data.Integral(),hist_sig.Integral(),hist_R.Integral(),r,fitFunc.GetChisquare()/fitFunc.GetNDF(),nll))

            c1 = rt.TCanvas("c1","c1",1000,1000)
            p1 = rt.TPad("p1",region+" "+mass+" r_{inj}="+str(r),0.0,0.35,1.0,1.0)
            p2 = rt.TPad("p2","NLL",0.0,0.0,1.0,0.35)
            p1.SetBottomMargin(0.0001)
            p1.SetBorderMode(0)
            p1.SetLogy(1)
            p2.SetTopMargin(0.0001)
            p2.SetBorderMode(0)
            p1.cd()
            # get y bounds on first try
            if hist0 is None:
                hist_data.Draw()
                hist_R.Draw("same")
            else:
                hist_R.Draw()
                hist_data.Draw("same")
                hist_R.Draw("same")
                fitFunc.Draw("same")
            p2.cd()
            hist_NLL.Draw("p")
            c1.cd()
            p1.Draw()
            if hist0 is None:
                ybounds[0] = math.pow(10,p1.GetUymin())
                ybounds[1] = math.pow(10,p1.GetUymax())
            p2.Draw("same")
            #c1.SaveAs("plots_BestRFit_res/dataAndSigWithFits_"+region+"_"+mass+"_"+rStr+"_chi2.png")
            c1.SaveAs("plots_BestRFit_res/sigMod_dataAndSigWithFits_"+region+"_"+mass+"_"+rStr+"_chi2.png")

        return nll, hist_NLL

for region in regions:
    for mass in ["2000","3000","4000"]:
#    for mass in ["3000"]:
        print(region, mass)
        #rootFile = rt.TFile.Open("datacard2.root","r") # make sure to also change what the plots are saved as!
        rootFile = rt.TFile.Open("datacard3.root","r")

        tDirName = region+"_2018"
        
        dataName = "data_obs" # TFirectoryFile in rootFile
        sigName = "SVJ_mZprime"+mass+"_mDark20_rinv03_alphapeak" # TH1F in dataName

        hist_data = rootFile.Get(tDirName+"/"+dataName); ngc(hist_data)
        hist_sig = rootFile.Get(tDirName+"/"+sigName); ngc(hist_sig)
        #print("Signal {} {}".format(region, mass))
        #print("iBin\tval\terr\tval/err")
#        for iBin in range(1,hist_sig.GetNbinsX()+1):
#            # use poisson errors on actual counts in signal histogram
#            binc = hist_sig.GetBinContent(iBin)
#            hist_sig.SetBinError(iBin,rt.Math.gamma_quantile_c((1-0.6827)/2.,binc+1,1)-binc)

        print("nEvents Data: {} {}".format(hist_data.Integral(),hist_data.GetEntries()))
        print("nEvents Sig: {} {}".format(hist_sig.Integral(),hist_sig.GetEntries()))

        hist_data.SetMarkerStyle(24)
        hist_data.SetMarkerColor(rt.kBlue)
        hist_data.SetLineColor(rt.kBlue)

        ybounds = [-1,-1]
        nll0, hist0 = makeRHist(0,region,mass,hist_data,hist_sig,ybounds,draw=True)
        rvals = np.linspace(-3,3,99)
#        rvals = np.array([-3,0,3])
#        rvals = np.concatenate(np.linspace(-3,3,99),np.linspace(3,5,32)[1:])
        nlls = []
        for r in rvals:
#        for r in [0, -0.46, -0.11, -1.91, -0.07]:
            nll, hist = makeRHist(r,region,mass,hist_data,hist_sig,ybounds,draw=True,hist0=hist0)
            nlls.append(nll)

        ind0 = np.where(rvals==0.)[0][0]
        # compute deltaNLL
        nlls = np.array(nlls)
        nlls = nlls - nlls[ind0]
        print "min(deltaNLL) = "+str(np.min(nlls))+" at r = "+str(rvals[np.argmin(nlls)])

        # make graph
        g = rt.TGraph(len(rvals),rvals,nlls)
        g.SetTitle("")
        g.GetXaxis().SetTitle("r")
        g.GetYaxis().SetTitle("deltaNLL")
        c1 = rt.TCanvas("c1","c1",1000,700)
        p1 = rt.TPad("p1","deltaNLL "+region+" "+mass+" r_{inj}="+str(r),0.0,0.0,1.0,1.0)
        p1.SetBorderMode(0)
        p1.cd()
        g.Draw("ap")
        c1.cd()
        p1.Draw()
        c1.SaveAs("plots_BestRFit_res/deltaNLL_sigMod_dataAndSigWithFits_"+region+"_"+mass+".png")












