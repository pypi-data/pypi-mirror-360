#
# Author: muhahmad@amd.com
# Description: create subset by Param for ed5 trained values
# To run: py trained_phycsr_subset.py full\folder\path\filename.csv
# version: 1.0 - hard coded for SR or rank/dimm = 0
#     

import pandas as pd
import os
import sys
import argparse

current_path = os.getcwd()

def create_subset(read_dt, hostname, data_path):

    #keys
    rank_check = "rank"
    #rank_type = ""

    #handle 2 different format of postprocess csr dump .csv: consolidated.csv & *analysis.csv
    if rank_check in read_dt.columns:
        #DCA_Delay
        dca_dly_dt = read_dt[(read_dt["Param"]=="DCA_Delay")]
        dca_dly_dt = dca_dly_dt.drop(columns=["rank", "nibble"])
        
        #DCS_Delay
        dcs_dly_dt = read_dt[read_dt["Param"]=="DCS_Delay"]
        dcs_dly_dt = dcs_dly_dt.drop(columns=["rank", "nibble"])

        #MRL
        mrl_dt = read_dt[read_dt["Param"]=="MRL"]
        mrl_dt = mrl_dt.drop(columns=["pin", "rank"])

        #Read Eye FastVref
        rd_eye_fvref_dt = read_dt[(read_dt["Param"]=="Read eye FastVref") & (read_dt["rank"]== 0)]
        
        #Read Eye evenU
        rdeye_pC_dt = read_dt[(read_dt["Param"]=="Read eye even U") & (read_dt["rank"]== 0)]
        
        #Read Eye oddU
        rdeye_pT_dt = read_dt[(read_dt["Param"]=="Read eye odd U") & (read_dt["rank"]== 0)]
        
        #Read SlowVref
        rd_slowvref_dt = read_dt[(read_dt["Param"]=="Read eye SlowVref")]
        rd_slowvref_dt = rd_slowvref_dt.drop(columns=["rank"])
    
    else:
        #DCA_Delay
        dca_dly_dt = read_dt[(read_dt["Param"]=="DCA_Delay")]
        dca_dly_dt = dca_dly_dt.drop(columns=["Dimm", "byte"])
        
        #DCS_Delay
        dcs_dly_dt = read_dt[read_dt["Param"]=="DCS_Delay"]
        dcs_dly_dt = dcs_dly_dt.drop(columns=["Dimm", "byte"])

        #MRL
        mrl_dt = read_dt[read_dt["Param"]=="MRL"]
        mrl_dt = mrl_dt.drop(columns=["pin", "Dimm"])

        #Read Eye FastVref
        rd_eye_fvref_dt = read_dt[(read_dt["Param"]=="Read eye FastVref") & (read_dt["Dimm"]== 0)]
        
        #Read Eye phaseC
        rdeye_pC_dt = read_dt[(read_dt["Param"]=="Read eye phaseC") & (read_dt["Dimm"]== 0)]
        
        #Read Eye phaseT
        rdeye_pT_dt = read_dt[(read_dt["Param"]=="Read eye phaseT") & (read_dt["Dimm"]== 0)]
        
        #Read SlowVref
        rd_slowvref_dt = read_dt[(read_dt["Param"]=="Read eye SlowVref")]
        rd_slowvref_dt = rd_slowvref_dt.drop(columns=["Dimm"])
    
    #RXEN
    rxen_dt = read_dt[read_dt["Param"]=="RXEN"]
    rxen_dt = rxen_dt.drop(columns=["pin"])

    #WL
    wl_dt = read_dt[read_dt["Param"]=="WL"]
    wl_dt = wl_dt.drop(columns=["pin"])

    #Write Eye
    wreye_dt = read_dt[read_dt["Param"]=="Write Eye"]

    #folder naming
    if hostname != "":
        output_folder = "trained_phycsr_subset_" + hostname
    else:
        output_folder = "trained_phycsr_subset"

    #os.chdir(data_path) #save at source location
    os.chdir(data_path)
    if os.path.exists(output_folder):
        #print("Subset folder already exist.")
        os.chdir(os.path.join(data_path, output_folder))
        create_csv_file(dca_dly_dt, dcs_dly_dt, mrl_dt, rd_eye_fvref_dt, rdeye_pC_dt, rdeye_pT_dt, rd_slowvref_dt, rxen_dt, wl_dt, wreye_dt)
    
    else:
        os.mkdir(output_folder)
        os.chdir(os.path.join(data_path, output_folder))
        create_csv_file(dca_dly_dt, dcs_dly_dt, mrl_dt, rd_eye_fvref_dt, rdeye_pC_dt, rdeye_pT_dt, rd_slowvref_dt, rxen_dt, wl_dt, wreye_dt)


def create_csv_file(dca_dly_dt, dcs_dly_dt, mrl_dt, rd_eye_fvref_dt, rdeye_pC_dt, rdeye_pT_dt, rd_slowvref_dt, rxen_dt, wl_dt, wreye_dt):
    
    dca_dly_dt = dca_dly_dt.to_csv("1_DCA_Delay.csv", index = False)
    dcs_dly_dt = dcs_dly_dt.to_csv("2_DCS_Delay.csv", index = False)
    mrl_dt = mrl_dt.to_csv("3_MRL.csv", index = False)
    rd_eye_fvref_dt = rd_eye_fvref_dt.to_csv("4_Read_Eye_FastVref.csv", index = False)
    rdeye_pC_dt = rdeye_pC_dt.to_csv("5_Read_Eye_evenU.csv", index = False)
    rdeye_pT_dt = rdeye_pT_dt.to_csv("6_Read_Eye_oddU.csv", index = False)
    rd_slowvref_dt = rd_slowvref_dt.to_csv("7_Read_SlowVref.csv", index = False)
    rxen_dt = rxen_dt.to_csv("8_RXEN.csv", index = False)
    wl_dt = wl_dt.to_csv("9_WL.csv", index = False)
    wreye_dt = wreye_dt.to_csv("10_Write_Eye.csv", index = False)
    output_folder = os.getcwd()
    print("\nSubsets data created in folder:", output_folder,  end='\n\n')

def get_hostname(file_path):
    hostname = ""
    data_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_name = file_name.split("_")
    name = file_name[0]
    #if file_name[0] has "morocco" or "congo":
    if ("congo" in name) or ("morocco" in name):
        hostname = name
    return hostname, data_path

def phycsr_subset(file_path):

    read_dt = pd.read_csv(file_path)
    #create_subset(read_dt, data_path)
    hostname, data_path = get_hostname(file_path)
    create_subset(read_dt,hostname, data_path)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="To run: py subset.py full\folder\path\filename.csv")
    parser.add_argument("filename", type=str, help="csv file name", default = 0)
    
    args = parser.parse_args()
    file_path = args.filename

    read_dt = pd.read_csv(file_path)
    #create_subset(read_dt, data_path)
    hostname, data_path = get_hostname(file_path)
    create_subset(read_dt,hostname, data_path)



    
