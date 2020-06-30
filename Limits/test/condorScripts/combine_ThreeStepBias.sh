#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node
source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/CMSSW_10_2_13.tgz .
tar -xf CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz
export SCRAM_ARCH=slc6_amd64_gcc700
cd CMSSW_10_2_13/src/
scramv1 b ProjectRename
eval `scramv1 runtime -sh`

echo "CMSSW: "$CMSSW_BASE

cd Stat/Limits/test
#give names to parameters
mZ=${1}
mD=${2}
rI=${3}
aD=${4}
REGION=${5}
nTOYS=${6}
expSig=${7}
genFunc=${8} # 0 for bkgFunc, 1 for altFunc
fitFunc=${9} # 0 for bkgFunc, 1 for altFunc
SVJOPTS=${10} # 0 for Dijet opts, 1 for SVJ opts


optName="OptD"
if [ ${SVJOPTS} -eq 1 ]
then
  optName="OptS"
fi

SVJ_NAME="SVJ_mZprime${mZ}_mDark${mD}_rinv${rI}_alpha${aD}"

xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/biasStudies2/${SVJ_NAME}/${SVJ_NAME}_${REGION}_2018_template_bias.txt ${SVJ_NAME}_${REGION}_2018_template_bias.txt
xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/biasStudies2/${SVJ_NAME}/ws_${SVJ_NAME}_${REGION}_2018_template.root ws_${SVJ_NAME}_${REGION}_2018_template.root


if [ ${REGION} == "highCut" ]
then
  parOptsGenMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_2_alt=0,${REGION}_p2_2_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt"
  parOptsFitMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_2_alt=0,${REGION}_p2_2_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt --trackParameters ${REGION}_p1_3,${REGION}_p2_3,${REGION}_p3_3"
  parOptsGenAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_3=0,${REGION}_p2_3=0,${REGION}_p3_3=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_3,${REGION}_p2_3,${REGION}_p3_3"
  parOptsFitAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_3=0,${REGION}_p2_3=0,${REGION}_p3_3=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_3,${REGION}_p2_3,${REGION}_p3_3 --trackParameters ${REGION}_p1_2_alt,${REGION}_p2_2_alt"
elif [ ${REGION} == "lowCut" ]
then
  parOptsGenMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_2_alt=0,${REGION}_p2_2_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt"
  parOptsFitMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_2_alt=0,${REGION}_p2_2_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt --trackParameters ${REGION}_p1_2,${REGION}_p2_2"
  parOptsGenAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_2=0,${REGION}_p2_2=0, --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2,${REGION}_p2_2"
  parOptsFitAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_2=0,${REGION}_p2_2=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2,${REGION}_p2_2 --trackParameters ${REGION}_p1_2_alt,${REGION}_p2_2_alt"
elif [ ${REGION} == "highSVJ2" ]
then
  parOptsGenMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_1_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_1_alt"
  parOptsFitMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_1_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_1_alt --trackParameters ${REGION}_p1_1"
  parOptsGenAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_1=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_1"
  parOptsFitAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_1=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_1 --trackParameters ${REGION}_p1_1_alt"
elif [ ${REGION} == "lowSVJ2" ]
then
  parOptsGenMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_2_alt=0,${REGION}_p2_2_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt"
  parOptsFitMain="--setParameters pdf_index_${REGION}_2018=0,${REGION}_p1_2_alt=0,${REGION}_p2_2_alt=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt --trackParameters ${REGION}_p1_2,${REGION}_p2_2"
  parOptsGenAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_2=0,${REGION}_p2_2=0, --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2,${REGION}_p2_2"
  parOptsFitAlt="--setParameters pdf_index_${REGION}_2018=1,${REGION}_p1_2=0,${REGION}_p2_2=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2,${REGION}_p2_2 --trackParameters ${REGION}_p1_2_alt,${REGION}_p2_2_alt"
else
  exit 1
fi

bonusGen=""
bonusFit="--robustFit=1 --setRobustFitTolerance=1."

if [ ${SVJOPTS} -eq 1 ]
then
  bonusGen="--cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex"
  bonusFit="--robustFit=1 --minos none --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex"
fi


if [ ${genFunc} -eq 0 ]
then
  genName="${REGION}${optName}Sig${expSig}GenMain"
  parOptsGen=${parOptsGenMain}
elif [ ${genFunc} -eq 1 ]
then
  genName="${REGION}${optName}Sig${expSig}GenAlt"
  parOptsGen=${parOptsGenAlt}
fi

if [ ${fitFunc} -eq 0 ]
then
  fitName="${genName}FitMain"
  parOptsFit=${parOptsFitMain}
elif [ ${genFunc} -eq 1 ]
then
  fitName="${genName}FitAlt"
  parOptsFit=${parOptsFitAlt}
fi
cmdMDF="combine ${SVJ_NAME}_${REGION}_2018_template_bias.txt -M MultiDimFit -n ${genName} --saveWorkspace --rMin -80 --rMax 80 ${parOptsGen} " 
cmdGen="combine higgsCombine${genName}.MultiDimFit.mH120.root -M GenerateOnly ${bonusGen} ${parOptsGen} -n ${genName} -t ${nTOYS} --toysFrequentist --saveToys --expectSignal ${expSig} --bypassFrequentistFit"
cmdFit="combine higgsCombine${genName}.MultiDimFit.mH120.root -M FitDiagnostics ${bonusFit} ${parOptsFit} -n ${fitName} --toysFile higgsCombine${genName}.GenerateOnly.mH120.123456.root -t ${nTOYS} --toysFrequentist --saveToys --expectSignal ${expSig} --rMin -80 --rMax 80 -v 3 --bypassFrequentistFit"


echo "combine commands:"
echo ${cmdMDF}
echo ${cmdGen}
echo ${cmdFit}

echo "Doing Snapshot" >/dev/stderr
$cmdMDF
echo "Done with Snapshot" >/dev/stderr
ls >/dev/stderr
echo "Doing Gen" >/dev/stderr
$cmdGen
echo "Done with Gen" >/dev/stderr
ls >/dev/stderr
echo "Doing Fit" >/dev/stderr
$cmdFit
echo "Done with Fit" >/dev/stderr
ls >/dev/stderr

# export items to EOS
echo "List all root files = "
ls *.root
echo "List all files"
ls 
echo "*******************************************"
OUTDIR=root://cmseos.fnal.gov//store/user/cfallon/biasStudies3/${SVJ_NAME}
echo "xrdcp output for condor"
for FILE in *.root
do
  if [ ! "ws_${SVJ_NAME}_${REGION}_2018_template.root" = ${FILE} ]
  then
    echo "xrdcp -f ${FILE} ${OUTDIR}/${FILE}"
    xrdcp -f ${FILE} ${OUTDIR}/${FILE} 2>&1
  fi
  rm ${FILE}
done
cd ${_CONDOR_SCRATCH_DIR}
rm -rf CMSSW_10_2_13
