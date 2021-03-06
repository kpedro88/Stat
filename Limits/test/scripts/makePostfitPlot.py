import os,sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import OrderedDict
from getParamsTracked import getParamsTracked, getFname

input_template = """INPUT
input/input_svj_stack_dijetmtdetahad_2017.txt
input/input_svj_mt_postfit_options.txt
input/input_svj_mt_hist_full.txt
"""

options_template = """OPTION
string+:printsuffix[{psuff}]
vstring:extra_text[{etxt}]
vstring:fits[{fitlist}]
vstring+:chosensets[{signames}]
vstring+:numers[{signames}]
string:rootfile[{ofile}]
"""

fit_template = "{fitname}\ts:fn[{fnname}]\tvd:pars[1,{pvals}]\td:yield[{yieldval}]\ts:legname[{legname}]\tin:input[input/input_svj_mt_fit_opt.txt]\tb:legpars[0]\tc:linecolor[{fitcol}]"

set_template = """hist\tmc\t{signamefull}\ts:legname[{legname}]\tc:color[{sigcol}]\ti:linestyle[7]\ti:panel[0]\tvs:fits[]\t{signorm}
\tbase\text\t{signamefull}\ts:extfilename[{sigfile}]\ts:exthisto_dir[{hdir}]\tvs:exthisto_in[{signamesafe}]\tvs:exthisto_out[MTAK8]"""

# todo: handle signal-injection toys in legname (& psuff)
data_template = """hist\tdata\tdata\ti:panel[1]\ts:legname[toy data {inj}]\tb:yieldnorm[0]
\tbase\text\tdata\ts:extfilename[{dfile}]\ts:exthisto_dir[{hdir}]\tvs:exthisto_in[Bkg_toy]\tvs:exthisto_out[MTAK8]"""

quantile_info = {
    -4: {"legname": "asimov", "name": "asimov", "color": "kYellow + 3", "sigcolor": "kCyan + 2"},
    -3: {"legname": "bestfit", "name": "bestfit", "color": "kOrange + 2", "sigcolor": "kCyan + 2"},
    -2: {"legname": "b-only", "name": "bonly", "color": "kRed", "sigcolor": "kCyan + 2"},
    -1: {"legname": "postfit (obs)", "name": "postfitobs", "color": "kBlue", "sigcolor": "kCyan + 2"},
}

function_info = {
    ("alt",2):  {"formula": "[0]*exp([1]*x/13000+[2]*log(x/13000))", "legname": "g_{2}(x)", "name": "g"},
    ("alt",3):  {"formula": "[0]*exp([1]*x/13000+[2]*log(x/13000)+[3]*log(x/13000)^2)", "legname": "g_{3}(x)", "name": "g"},
    ("ralt",2):  {"formula": "[0]*exp([1]*x/13000)*(x/13000)^([2])", "legname": "g_{2}(x)", "name": "g"},
    ("ralt",3):  {"formula": "[0]*exp([1]*x/13000)*(x/13000)^([2]*(1+[3]*log(x/13000)))", "legname": "g_{3}(x)", "name": "g"},
    ("main",2): {"formula": "([0]*(1-x/13000)^[1])*((x/13000)^(-[2]))", "legname": "f_{1,1}(x)", "name": "f"},
    ("main",5): {"formula": "([0]*(1-x/13000)^([1]+[2]*log(x/13000)+[3]*log(x/13000)^2))*((x/13000)^(-([4]+[5]*log(x/13000))))", "legname": "f_{3,2}(x)", "name": "f"},
}

region_info = {
    "highCut": {"alt": 3, "main": 5, "legname": "high-^{}R_{T}"},
    "lowCut": {"alt": 3, "main": 2, "legname": "low-^{}R_{T}"},
    "highSVJ2": {"alt": 2, "main": 2, "legname": "high-SVJ2"},
    "lowSVJ2": {"alt": 2, "main": 2, "legname": "low-SVJ2"},
}

def makePostfitPlot(mass, name, method, quantile, data_file, datacard_dir, injected, combo, region, reparam):
    ch = "ch1" if "high" in region else "ch2"

    iname = "input_svj_mt_fit_toy_{region}_{name}_{qname}_mZprime{mass}.txt".format(region=region,mass=mass,name=name,qname=quantile_info[quantile]["name"])
    signame = "SVJ_{}_20_0.3_peak".format(mass)
    signamesafe = "SVJ_mZprime{}_mDark20_rinv03_alphapeak".format(mass)
    rinfo = region_info[region]
    ftype = ""
    finfo = None

    fits = OrderedDict()
    sigs = OrderedDict()
    for q in [quantile]:
        qinfo = quantile_info[q]

        fname = getFname(mass, name, method, combo)
        postfname = fname.replace("higgsCombine","multidimfitPostfit{:.3f}".format(q)).replace("{}.".format(method),"")
        params = getParamsTracked(fname, quantile)
        if len(params)==0: return ""

        pfit = {p:v for p,v in params.iteritems() if region in p}
        pvals = [str(v) for p,v in sorted(pfit.iteritems())]
        # only pick finfo once, because it should be consistent for the region
        if finfo is None:
            ftype = "alt" if any("_alt" in p for p in pfit) else "main"
            finfo = function_info[("ralt" if reparam and ftype=="alt" else ftype,rinfo[ftype])]
        fitname = "{}_{}".format(finfo["name"],qinfo["name"])

        fits[fitname] = fit_template.format(
            fitname = fitname,
            fnname = finfo["formula"],
            pvals = ','.join(pvals),
            # yieldval must be multiplied by bin width
            yieldval = str(params["trackedParam_n_exp_final_bin{}_proc_roomultipdf".format(ch)]*100),
            legname = "{}, {}".format(finfo["legname"],qinfo["legname"]),
            fitcol = qinfo["color"],
        )

        # no need to show signal for b-only
#        if qinfo["name"]=="bonly": continue

        signamefull = "{}_{}".format(signame,qinfo["name"])
        hdir = "{}_2018".format(region)
        if qinfo["name"]=="bonly":
            legname = "{} (r = {:.2g})".format(signame,1)
            sigfile = "{}/datacard_{}.root".format(datacard_dir,signame)
            hdirsig = hdir
            signorm = "b:yieldnorm[0]"
        else:
            legname = "{} (r = {:.2g})".format(signame,params["r"])
            sigfile = "test/{}".format(postfname if signamesafe in postfname else signamesafe+"/"+postfname)
            hdirsig = "shapes_fit/{}".format(ch)
            signorm = "d:yieldnormval[{}]".format(params["trackedParam_n_exp_final_bin{}_proc_{}".format(ch,signamesafe)])

        sigs[signamefull] = set_template.format(
            signamefull = signamefull,
            legname = legname,
            sigcol = qinfo["sigcolor"],
            signorm = signorm,
            sigfile = sigfile,
            signame = signame,
            signamesafe = signamesafe,
            hdir = hdirsig,
        )

    data = data_template.format(
        dfile = data_file,
        hdir = hdir,
        inj = "(no signal)" if injected==0 else "(m_{{Z'}} = {:.1f} TeV)".format(float(injected)/1000.)
    )

    options = options_template.format(
        # should quantiles be included here?
        psuff = "_toy_fit_{}_{}_{}_mZprime{}".format(region,name,quantile_info[quantile]["name"],mass),
        etxt = rinfo["legname"],
        fitlist = ','.join(fits),
        signames = ','.join(sigs),
        ofile = "test/fit_toy_mZprime{}_{}_{}_{}".format(mass,region,name,quantile_info[quantile]["name"]),
    )

    with open(iname,'w') as ifile:
        lines = [
            input_template,
            options,
            "FIT",
            '\n'.join(fits.values()),
            '',
            "SET",
            '\n'.join(sigs.values()),
            data,
        ]
        ifile.write('\n'.join(lines))

    return iname

if __name__=="__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--mass", dest="mass", type=int, required=True, help="Zprime mass")
    parser.add_argument("-n", "--name", dest="name", type=str, default="Test", help="test name (higgsCombine[name])")
    parser.add_argument("-M", "--method", dest="method", type=str, default="AsymptoticLimits", help="method name (higgsCombineTest.[method])")
    parser.add_argument("-d", "--data", dest="data", type=str, default="test/trig4_sigfull_datacard.root", help="data file name")
    parser.add_argument("-i", "--injected", dest="injected", type=int, default=0, help="injected Zprime mass")
    parser.add_argument("-D", "--datacards", dest="datacards", type=str, default="root://cmseos.fnal.gov//store/user/pedrok/SVJ2017/Datacards/trig4/sigfull/", help="datacard location (for prefit)")
    parser.add_argument("-q", "--quantile", dest="quantile", type=float, default=-1, help="quantile to plot fits")
    parser.add_argument("-c", "--combos", dest="combos", type=str, default=[], nargs='+', choices=["cut","bdt"], help="combo(s) to plot")
    parser.add_argument("-r", "--reparam", dest="reparam", default=False, action="store_true", help="use reparameterized alt fn")
    args = parser.parse_args()

    combos = {
        "cut": ["highCut","lowCut"],
        "bdt": ["highSVJ2","lowSVJ2"],
    }
    args.combos = {c:combos[c] for c in args.combos}

    input_files = []
    for combo,regions in args.combos.iteritems():
        for region in regions:
            tmp = makePostfitPlot(args.mass,args.name,args.method,args.quantile,args.data,args.datacards,args.injected,combo,region,args.reparam)
            input_files.append(tmp)
    print ' '.join(input_files)

