#include "TObject.h"
#include "TNamed.h"
#include <iostream>
#include "TH1.h"
#include "TFolder.h"
#include "TFile.h"
#include "TStyle.h"
#include "TError.h"
#include "TTree.h"
#include "TBranch.h"
#include "TROOT.h"
#include <map>
#include <set>
#include <vector>
#include <string>
#include <algorithm>
#include <ctime>


void Plotter(){
  
  TH1D* h1 = new TH1D("SumPt", " Sum Pt", 300, 0.0, 3000.0);
  TH1D* h2 = new TH1D("InvMass", "Invariant Mass", 200, 0.0, 2000.0);
  TH1D* h3 = new TH1D("MET", " Missing T Energy",  200, 0.0, 2000.0);
  TH1D* h4 = new TH1D("Weight", " Weights",  400, -2000.0 , 2000.0);
  TH1D* h5 = new TH1D("FinalWeights", " FinalWeights",  400, -2000.0 , 2000.0);
  
  Double_t sumpt,invmass,met, mweight, totalEvents, fweg;
  //vector<double> vectE;

  Int_t entries;
  string Foldtest, Foldout,fin,fout;
  Foldtest = "../../../TEST_FOLDER/test_UL17_TTMtt1000_NEW1/";
  Foldout=Foldtest;
  fin = Foldtest +"ECP_TT_Mtt-1000toInf_13TeV_PH.root";
  fout= Foldout + "Plot_TT_Mtt-1000toInf_13TeV_PH.root";
  //TFile *myfile= new TFile("ECP_Data_Run2017B-UL2017_MiniAODv2-v1_297047_299329_SingleMuon.root","READ");
  //TFile *myfile= new TFile(Foldtest+"ECP_TT_Mtt-1000toInf_13TeV_PH_v2.root","READ");
  //TFile *myfile= new TFile(Foldtest.c_str()+"ECP_TT_Mtt-1000toInf_13TeV_PH.root","READ");
  TFile *myfile= new TFile(fin.c_str(),"READ");
  //vectE = myfile->Get("totalEvents");

  std::vector<Double_t> *vectE;
  myfile->GetObject("TotalEvents", vectE);

  for(std::size_t i = 0; i < vectE->size(); ++i) {
    totalEvents = vectE->at(i);
    std::cout << "Total Events: "<< vectE->at(i) << "\n";
  }

  // f->GetListOfKeys()->Contains("1Muon_1Ele_1MET");
  TTree *tree= (TTree*) myfile->Get("_1Muon_1Jet_1MET");
  tree->SetBranchAddress("SumPt",&sumpt);
  tree->SetBranchAddress("InvMass",&invmass);
  tree->SetBranchAddress("MET",&met);
  tree->SetBranchAddress("Weight",&mweight);

  entries= tree->GetEntries();
  for (int i=0; i<entries; i++)
    {
      tree->GetEntry(i);
      fweg=mweight/totalEvents;
      h1->Fill(sumpt);
      h2->Fill(invmass);
      h3->Fill(met);
      h4->Fill(mweight);
      h5->Fill(fweg);
      cout << "Entry, SumPt, InvMass, MET, Weight, fweg:  " << i << "|" << sumpt << "|" << invmass << "|" << met << "|" << mweight << "|" << fweg << endl;

    }

  myfile->Close();
  
  //TFile *myfile2= new TFile("Plot_Data_Run2017B-UL2017_MiniAODv2-v1_297047_299329_SingleMuon.root","RECREATE");
  //TFile *myfile2= new TFile("Plot_TT_Mtt-1000toInf_13TeV_PH_v2.root","RECREATE");
  //TFile *myfile2= new TFile(Foldout.c_str()+"Plot_TT_Mtt-1000toInf_13TeV_PH.root","RECREATE");
  TFile *myfile2= new TFile(fout.c_str(),"RECREATE");
  h1->Write();
  h2->Write();
  h3->Write();
  h4->Write();
  h5->Write();

  myfile2->Close();

}


