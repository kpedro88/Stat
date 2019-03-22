import ROOT
from ROOT import RooRealVar, RooDataHist, RooArgList, RooGenericPdf, RooExtendPdf, RooWorkspace, RooFit
import os, sys
from Stat.Limits.settings import *
from fits import *

#*******************************************************#
#                                                       #
#   getRate(process, ifile)                             #
#                                                       #
#   getCard(sig, ch, ifilename, outdir)                 #
#                                                       #
#*******************************************************#


#*******************************************************#
#                                                       #
#                     Utility Functions                 #
#                                                       #
#*******************************************************#



def getRate(ch, process, ifile):
       hName = ch + "/"+ process
       h = ifile.Get(hName)
       return h.Integral()

def getHist(ch, process, ifile):
       hName = ch + "/"+ process
       #print "Histo Name ", hName
       h = ifile.Get(hName)
       return h




#*******************************************************#
#                                                       #
#                      Datacard                         #
#                                                       #
#*******************************************************#

def getCard(sig, ch, ifilename, outdir, mode = "histo", unblind = False):

       print "Fit Params", fitParam

       try:
              ifile = ROOT.TFile.Open(ifilename)
       except IOError:
              print "Cannot open ", ifilename
       else:
              print "Opening file ",  ifilename
              ifile.cd()


       r = ROOT.gDirectory.GetListOfKeys()[0]
       year = r.ReadObj().GetName()[-4:]
       print "YEAR: ", year

       ch += "_"
       ch += year
       
       workdir_ = ifilename.split("/")[:-1]
       WORKDIR = "/".join(workdir_) + "/"
       carddir = outdir+  "/"  + sig + "/"



       #*******************************************************#
       #                                                       #
       #                   Generate workspace                  #
       #                                                       #
       #*******************************************************#


    
       if(mode == "template"):


              histBkgData = getHist(ch, "Bkg", ifile)
              histData = histBkgData
              if (unblind):  
                     print "BE CAREFULL: YOU ARE UNBLINDING"
                     histData = getHist(ch, "data_obs", ifile)
                     print "*********Number of data ", histData.Integral()
              histSig = getHist(ch, sig, ifile)
#              mT = RooRealVar(  "m_T",    "m_{T}",          1500., 3900., "GeV")
              bkgData = RooDataHist("bkgdata", "Data (MC Bkg)",  RooArgList(mT), histBkgData, 1.)
              obsData = RooDataHist("data_obs", "(pseudo) Data",  RooArgList(mT), histData, 1.)
              sigData = RooDataHist("sigdata", "Data (MC sig)",  RooArgList(mT), histSig, 1.)
              print "Bkg Integral: ", histData.Integral() 
              #nBkgEvts = bkgData.sumEntries()
              nBkgEvts = histBkgData.Integral() 
              print "Bkg Events: ", nBkgEvts

    
              # build the pdf(s), in this case, with 4 parameters
             # p1 = RooRealVar("CMS2016_"+ch+"_p1", "p1", 0.001742, -1000., 1000.)
             # p2 = RooRealVar("CMS2016_"+ch+"_p2", "p2", 14.21, -1000., 1000.)
             # p3 = RooRealVar("CMS2016_"+ch+"_p3", "p3", 7.225, -10., 10.)
             # p4 = RooRealVar("CMS2016_"+ch+"_p4", "p4", 0.7731, -10., 10.)
             #              modelBkg = RooGenericPdf("Bkg", "Bkg. fit (3 par.)", "pow(1 - @0/8000, @1) / pow(@0/8000, @2+@3*log(@0/8000))", RooArgList(mT, p2, p3, p4))
              

              print "Channel: ", ch
              modelBkg = fitParam[ch].modelBkg
              normzBkg = RooRealVar(modelBkg.GetName()+"_norm", "Number of background events", nBkgEvts, 0., 1.e3)
              print "NormBkg ", nBkgEvts
              modelExt = RooExtendPdf(modelBkg.GetName()+"_ext", modelBkg.GetTitle(), modelBkg, normzBkg)
              # fit them to data to provide a good starting point to the fit in the combine
              #              fitRes4 = modelExt4.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
              #              fitRes4.Print()
              # set the normalization to CONSTANT. There will be dedicated flat uncertainties in the datacard to make the background free
              #normzBkg1.setConstant(True)
              #normzBkg2.setConstant(True)
              #normzBkg3.setConstant(True)
              #normzBkg4.setConstant(True)

              # create workspace
              w = RooWorkspace("SVJ", "workspace")
              # Dataset
              # ATT: include isData
              getattr(w, "import")(bkgData, RooFit.Rename("Bkg"))
              getattr(w, "import")(obsData, RooFit.Rename("data_obs"))
              getattr(w, "import")(sigData, RooFit.Rename(sig))
              #else: getattr(w, "import")(setToys, RooFit.Rename("data_obs"))
              getattr(w, "import")(modelBkg, RooFit.Rename(modelBkg.GetName()))
              #getattr(w, "import")(modelAlt, RooFit.Rename(modelAlt.GetName()))
              getattr(w, "import")(normzBkg, RooFit.Rename(normzBkg.GetName()))
              w.writeToFile("%sws_%s_%s_%s.root" % (carddir, sig, ch, mode), True)

              print "Workspace", "%sws_%s_%s_%s.root" % (carddir, sig, ch, mode) , "saved successfully"
                 
              workfile = "./ws_%s_%s_%s.root" % ( sig, ch, mode)
              # ======   END MODEL GENERATION   ======       



       rates = {}
       procLine = ""
       procNumbLine = ""
       rateLine = ""
       binString = ""

       if(mode == "template"):       

              processes.append("Bkg")
              processes[:-1] = []
              rates["Bkg"] = nBkgEvts
              procLine += ("%-43s") % ("Bkg")
              rateLine += ("%-43s") % (rates["Bkg"])
              binString += (("%-43s") % (ch) ) * (2)
              procNumbLine = 1 
              
       else:
              i = 1
              bkgrate = 0
              for p in processes:
                     rates[p] = getRate(ch, p, ifile)
                     bkgrate =  rates[p]
                     procNumbLine += ("%-43s") % (i)
                     procLine += ("%-43s") % (p)
                     rateLine += ("%-43.1f") % (bkgrate)
                     i+=1
              binString += (("%-43s") % (ch) ) * (len(processes)+1)


       if ((not unblind) and (mode == "template")): 
              print "N.B: We are in blind mode. Using MC bkg data for data_obs"
              rates["data_obs"] = getRate(ch, "Bkg", ifile)
              print "Pseudo data rate: ", rates["data_obs"]
       else: rates["data_obs"] = getRate(ch, "data_obs", ifile)
        
       rates[sig] = getRate(ch, sig, ifile)



       card  = "imax 1 number of channels \n"
       card += "jmax * number of backgrounds \n"
       card += "kmax * number of nuisance parameters\n"
       card += "-----------------------------------------------------------------------------------\n"

       if(mode == "template"):
              #              card += "shapes   %s  %s    %s    %s    %s\n" % (sig, ch, ifilename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_SYSTEMATIC")
              #              card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (sig, ch, WORKDIR, ch, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s\n" % (modelBkg.GetName(), ch, workfile, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s\n" % (sig, ch, workfile, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s\n" % ("data_obs", ch, workfile, "SVJ:$PROCESS")

       else:  
              card += "shapes   *      *   %s    %s    %s\n" % (ifilename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_SYSTEMATIC")
              card += "shapes   data_obs      *   %s    %s\n" % (ifilename, "$CHANNEL/$PROCESS")
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin               %s\n" % ch
       print "===> Observed data: ", rates["data_obs"]
       card += "observation       %0.d\n" % (rates["data_obs"])
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin                                     %-43s\n" % (binString)
       card += "process                                 %-43s%-43s\n" % (sig, procLine) #"roomultipdf"
       card += "process                                 %-43s%-43s\n" % ("0", procNumbLine)
       card += "rate                                    %-43.6f%-43s\n" % (rates[sig], rateLine) #signalYield[m].getVal(), nevents
       card += "-----------------------------------------------------------------------------------\n"

       for sysName,sysValue  in syst.iteritems():

              if(sysValue[0]=="lnN"): 
                     card += "%-20s%-20s" % (sysName, sysValue[0])
                     if(sysValue[1]=="all"):
                            if(mode == "template"): card += "%-20s" % (sysValue[2]) * (2)
                            else: card += "%-20s" % (sysValue[2]) * (len(processes) + 1)

                     else:
                            hsysName =  "_" + sysName  
                            hsysNameUp = "_" + sysName + "UP"  
                            hsysNameDown = "_" + sysName + "DOWN" 
                            sigSys = (getRate(ch, sig+hsysNameUp, ifile) - getRate(ch, sig+hsysNameDown, ifile))/ getRate(ch, sig+hsysName, ifile)
                            card += "%-20s" % (sigSys)
                            for p in processes:
                                   bkgSys = (getRate(ch, p+hsysNameUp, ifile) - getRate(ch, p+hsysNameDown, ifile))/ getRate(ch, p+hsysName, ifile)
                                   card += "%-20s" % (bkgSys)
              elif(sysValue[0]=="shape"):
                     if("mcstat" not in sysName):
                            card += "shape      %-20s" % (sysName)
                            if ("sig" in sysValue[1]): card += "%-20s" % ( "1") 
                            else: card += "%-20s" % ( "-") 
                            for p in processes:
                                   if (p in sysValue[1]): card += "%-20s" % ( "1") 
                                   else: card += "%-20s" % ( "-") 
              

                     else:
                            # CAMBIARE NOME DELLA SYST                     
                            for samp in sysValue[1]:
                                   if (samp == "sig" or samp == "Sig"): 
                                          card += "shape      %-20s" % (sysName)
                                          card += "%-20s" % ( "1") 
                                          card += "%-20s" % ("-") * (len(processes)) 
                                   else:
                                          card += "shape      %-20s" % (sysName)
                                          card += "%-20s" % ( "-") 
                                          line = ["%-20s" % ( "-") for x in xrange (len(processes))]

                                          if samp not in processes and mode == "template":
                                                 samp = "Bkg"
                                          if samp in processes: 
                                                 index = processes.index(samp)  
                                                 line[index] = "1"
                                                 
                                          line = "         ".join(line)
                                          card += line
                                   card += "\n"        
              card += "\n"



#       card += "%-20s%-20s%-20d\n " % (ch, "autoMCStats", 0)

       if not os.path.isdir(outdir): os.system('mkdir ' +outdir)
       if not os.path.isdir(outdir + "/" + sig): os.system('mkdir ' +outdir + "/" + sig)


       outname =  "%s%s_%s_%s.txt" % (carddir, sig, ch, mode)
       cardfile = open(outname, 'w')
       cardfile.write(card)
       cardfile.close()


    

       print card
       return card




