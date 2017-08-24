#! /bin/sh
python Flist.py
tar czvf tarball.tgz Files*.txt TWTopPtSF.root plots/TWrate_Maker*.root Alphabet/fn_bstar*.txt fitdata/*.txt Tagrate*2D*.root rootlogon.C TWanalyzer.py TWrate.py ModMassFile_*.root TWsequencer.py Bstar_Functions.py Triggerweight_2jethack_data.root PileUp_Ratio_ttbar.root
mv Files*.txt txt_temp
./development/runManySections.py --createCommandFile --cmssw --addLog --setTarball=tarball.tgz \toy.listOfJobs commands.cmd
./runManySections.py --submitCondor commands.cmd
condor_q lcorcodi