import ROOT
import os,sys
import os.path
### Let's add some more from different folder
'''
framework = os.path.expandvars('$myLIB')
sys.path.insert(1, framework+'/ROOT_Utils/')
try:
    import CMS_lumi, tdrstyle
    import ROOT_Utils
except:
  print("ERROR:\n\tCan't find the package CMS_lumi and tdrstlye\n\tPlease verify that this file are placed in the path $myLIB/ROOT_Utils/ \n\tAdditionally keep in mind to export the environmental variable $myLIB\nEXITING...\n")
  sys.exit(0)
'''
h1 = ROOT.TH1D("SumPt", " Sum Pt", 300, 0.0, 3000.0);
h2 = ROOT.TH1D("InvMass", "Invariant Mass", 200, 0.0, 2000.0);
h3 = ROOT.TH1D("MET", " Missing T Energy",  200, 0.0, 2000.0);
h4 = ROOT.TH1D("Weight", " Weights",  400, -2000.0 , 2000.0);
h5 = ROOT.TH1D("FinalWeights", " FinalWeights",  140, -20.0 , 120.0);

files = ["../../../TEST_FOLDER/test_UL17_TTMtt1000_NEW1/ECP_TT_Mtt-1000toInf_13TeV_PH.root","Jan.root"]
Filespath=[]
Dirpath = "/user/vigilante/MUSIC_TESTECP_Feb22/mc"
flag1= False
lumi = 41480.
#Choose the class name you want to create your plots here
classname="_1Ele"

for dirpath, dirnames, filenames in os.walk(Dirpath):
    for filename in [f for f in filenames if f.startswith("ECP")]:
        Filespath.append(os.path.join(dirpath, filename))

for f in Filespath:    
    myfile = ROOT.TFile(f,"OPEN")
    if myfile.GetListOfKeys().Contains(classname) is False:
        continue
    print f
    tree = myfile.Get(classname)
    #tree.SetBranchAddress("SumPt",sumpt)
    #tree.SetBranchAddress("InvMass",invmass)
    #tree.SetBranchAddress("MET",met)
    #tree.SetBranchAddress("Weight",mweight)
    
    entries = tree.GetEntries()
    #PyRoot should be able to handle standard vector (std::vector)
    vectE=  ROOT.std.vector("double")()

    myfile.GetObject("TotalEvents",vectE)
    totalEvents = vectE[0]
    
    for i in xrange(entries):
        tree.GetEntry(i)
        fweg = tree.Weight/totalEvents *lumi
        h1.Fill(tree.SumPt)
        h2.Fill(tree.InvMass)
        h3.Fill(tree.MET)
        h4.Fill(tree.Weight)
        h5.Fill(fweg)
    myfile.Close()

myfile2= ROOT.TFile("testOut.root","RECREATE")
h1.Write()
h2.Write()
h3.Write()
h4.Write()
h5.Write()

myfile2.Close()


'''
feb_hist.Scale(1./feb_hist.GetEntries())
feb_hist.SetTitle("Feb")
feb_hist.SetName("Feb")

feb_hist.SetLineColor(ROOT.kRed)
feb_hist.GetXaxis().SetTitle("Energy (a.u.)")
feb_hist.GetXaxis().SetLabelSize(0.03)
feb_hist.GetYaxis().SetTitle("Entries")
feb_hist.GetYaxis().SetLabelSize(0.03)
feb_hist.SetStats(False)
feb_hist.Draw("HIST")

    
latex = ROOT.TLatex()
latex.SetTextFont(42)
latex.SetTextAngle(0)
latex.SetTextColor(ROOT.kBlack)    
latex.SetTextAlign(12)
latex.SetTextSize(0.03)
latex.DrawTextNDC(0.6, 0.86, "ME0-1-CERN-0001")
latex.DrawTextNDC(0.6, 0.82, "Gas: Ar/CO2 (70/30) - 5 L/hr")
latex.DrawTextNDC(0.6, 0.78, "Gas Gain = 15000")

Jan_File = ROOT.TFile(files[1],"OPEN")
jan_hist = Jan_File.Get("htemp")
jan_hist.Scale(1./jan_hist.GetEntries())

jan_hist.Draw("SAME HIST")


gJan = ROOT.TF1("GausJan","gaus",6.36999e-01-1.8*5.61567e-02,6.36999e-01+1.5*5.61567e-02)
gFeb = ROOT.TF1("GausFeb","gaus",6.36999e-01-1.8*5.61567e-02,6.36999e-01+1.5*5.61567e-02)

gJan.SetParameters(0.018,6.36999e-01,5.61567e-02)
gFeb.SetParameters(0.018,6.36999e-01,5.61567e-02)

gFeb.SetLineColor(ROOT.kRed)
gJan.SetLineColor(ROOT.kBlue)

feb_hist.Fit(gFeb,"R")
jan_hist.Fit(gJan,"R")

gFeb.Draw("SAME")
gJan.Draw("SAME")

canvas.Modified()
canvas.Update()

raw_input()
'''
