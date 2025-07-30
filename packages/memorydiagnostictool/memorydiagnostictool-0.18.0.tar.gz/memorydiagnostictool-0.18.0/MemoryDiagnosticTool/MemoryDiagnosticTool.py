"""
Version : 1.0
Author  : saukae.tan@amd.com
Desc    : summary of MDT
"""

import re
import sys
import os
import pandas as pd
import argparse
import glob
import numpy as np
import tkinter as tk
from tkinter import filedialog
from collections import defaultdict
from MemoryDiagnosticTool.rrw_error_count_parser import rrw_error_count
from MemoryDiagnosticTool.esid_complete_parser import check_esid_complete
from MemoryDiagnosticTool.memtest_parser import check_memtest
from MemoryDiagnosticTool.Trained_CSR_CSV import trained_csr_csv
from MemoryDiagnosticTool.Trained_LOG_CSV import log_to_csv
from MemoryDiagnosticTool.MR_readout_v1 import mr_readout
from MemoryDiagnosticTool.dca_dcs_eye import scan_dcs_dca
from MemoryDiagnosticTool.rd_wr_eye import PMU_Eye
from MemoryDiagnosticTool.rd_wr_eye import Rd_Eye_Scan
from MemoryDiagnosticTool.trained_phycsr_subset import phycsr_subset
from MemoryDiagnosticTool.postcode import get_postcodefile
from MemoryDiagnosticTool.MDT_html_template import parse_to_html

class HtmlWriter:
    def __init__(self, file_name):
        self.file_name = file_name
        # Open the file in append mode
        self.file = open(self.file_name, 'a', encoding='utf-8')
        # Write the initial HTML structure to the file
        self.file.write("<html><head><title>Output</title></head><body><pre>\n")
        
    def write(self, message):
        """Write the message to the HTML file."""
        self.file.write(message)
    
    def flush(self):
        """Flush the file (in case you want to use sys.stdout.flush())."""
        self.file.flush()
        
    def close(self):
        """Close the HTML file after use."""
        self.file.write("\n</pre></body></html>")
        self.file.close()


def get_bios_hostname(base):
    bios = ""
    hostname = ""
    text = base.split("_")
    if len(text)>1:
        bios = text[0]
        hostname = text[1]      
    for item in text:
        if item.startswith("V"):
            bios = item
        if ("congo" in item) or ("morocco" in item):
            hostname = item
    return bios, hostname


def get_logfiles_from_directory(directory):
    """Recursively get all .log files from the given directory and its subdirectories,
    skipping directories that end with '_parsed_log'."""
    log_files = []
    # os.walk will recursively go through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        # Skip directories that end with '_parsed_log'
        dirs[:] = [d for d in dirs if not "parsed" in d]
        
        # Find .log files in the current directory excluding those with 'parsed' in the filename
        log_files.extend(
            [os.path.join(root, f) for f in files if f.endswith(".log") and "parsed" not in f]
        )
    print("Log:")
    print(log_files)
    return log_files
    
    
def get_decodedlogfiles_from_directory(directory):
    """Recursively get all .log files from the given directory and its subdirectories."""
    log_files = []
    # os.walk will recursively go through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        # For each directory, check for .log files
        log_files.extend(glob.glob(os.path.join(root, "*.parsed.log*")))
    print("Decoded Log:")
    print(log_files)
    return log_files    

def get_csrdump_from_directory(directory):
    """Recursively get all .log files from the given directory and its subdirectories."""
    csv_files = []
    # os.walk will recursively go through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        # Skip directories that end with '_parsed_log'
        dirs[:] = [d for d in dirs if not d.endswith('_parsed_log')]    
        # For each directory, check for .log files
        csv_files.extend(glob.glob(os.path.join(root, "*.csv*")))
    filtered_files = [file for file in csv_files if 'MDT' not in file]
    print("CSR Dump:")
    print(filtered_files)
    return filtered_files     


def select_file_or_directory():
    """Opens a file/directory dialog to let the user choose a file or directory."""
    # Initialize Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Open the file/directory dialog
    file_path = filedialog.askdirectory(title="Select a directory")
    #file_path = filedialog.askopenfilename(title="Select a file")  # To select a file
    #if not file_path:  # If no file is selected, prompt for a directory instead
    #    file_path = filedialog.askdirectory(title="Select a directory")
    return file_path

def MDT_summary_table(mdt_html, rrw_file, esid_file, order_result, missing_print, analysis_result):
    # Create a dictionary to store the count of "Pass" entries for each system
    rrw_data  = {}
    rrw_count = {}
    esid_data = defaultdict(lambda: {"log_files": [], "pass_count": 0, "memtest_count": 0})
    memtest_result = {}
    pmu_train_result = ""
    summary_table=""
    try:
        if os.path.exists(rrw_file):
            # Load the CSV data into a pandas DataFrame
            df = pd.read_csv(rrw_file)
            
            # Iterate through the DataFrame and populate the dictionary
            for _, row in df.iterrows():
                system = row["System"]
                log_file = row["Log File"]
                iod = int(row["IOD"])
                iod_pass = row["IOD Passed"]
                iod_logpass = row["IOD Passed Log Flag"]
                # Check if both IOD Passed and Log Flag have a "True"
                if iod_pass == True and iod_logpass == True:
                    rrw_data[system, log_file, iod]= "pass"
                else:
                    rrw_data[system, log_file, iod]= "fail"
            # Iterate through rrw_data and rrw_count passes and total based on the system and index
            for (system, _, index), value in rrw_data.items():
                if system not in rrw_count:
                    rrw_count[system] = {0: {'pass': 0, 'total': 0}, 1: {'pass': 0, 'total': 0}}            
                # Increment pass rrw_count if the value is 'pass'
                if value == 'pass':
                    rrw_count[system][index]['pass'] += 1
                # Increment total rrw_count for each system and index
                rrw_count[system][index]['total'] += 1
                
        if os.path.exists(esid_file):
            # Load the CSV data into a pandas DataFrame
            df = pd.read_csv(esid_file)

            # Iterate through the DataFrame and populate the dictionary
            for _, row in df.iterrows():
                system = row["System"]
                log_file = row["Log File"]
                iod0_pass = row["IOD0 Pass"]
                iod1_pass = row["IOD1 Pass"]
                memtest = row["Channels Absent From Memtest"]
                miscompare = row["Miscompares"]
                pmu_train_status = row["Training Status"]
                
                #check pmu_training fail channel
                if pmu_train_status == "Fail":
                    fail_channel = row["PMU Training Failures Channel"]
                    pmu_train_result += f"{log_file}: {fail_channel}<br>"

                # Add log file to the system's list of log files
                esid_data[system]["log_files"].append(log_file)
                
                if system in memtest_result:
                    if len(memtest) > len(memtest_result[system]):
                        memtest_result[system] = memtest
                else:
                   memtest_result[system]= memtest

                # Check if both miscompare and memtest is empty then consider pass
                if miscompare=="[]" and memtest=="[]":
                    esid_data[system]["memtest_count"] += 1
                    
                # Check if both IOD0 and IOD1 have a "Pass"
                if iod0_pass == "Pass" and iod1_pass == "Pass":
                    esid_data[system]["pass_count"] += 1
   
            # Prepare the HTML table result
            summary_table = "<tr><th>System</th><th>RRW IOD0 Pass/Total</th><th>RRW IOD1 Pass/Total</th><th>ESID Pass/Total</th><th>Memtest Result</th></tr>"
            # Check systems that meet the condition of 8 log files and all "Pass"
            for system, esid_count in esid_data.items():
                total_log = len(esid_count['log_files'])
                if rrw_count:
                    try:
                        if rrw_count[system][0]['total'] != 0:
                            total_rrw_iod0 = max(rrw_count[system][0]['total'] , len(esid_count['log_files']))
                        if rrw_count[system][1]['total'] != 0:
                            total_rrw_iod1 = max(rrw_count[system][1]['total'] , len(esid_count['log_files']))
                        summary_table += f"<tr><td>{system}</td><td>{rrw_count[system][0]['pass']}/{total_rrw_iod0} Pass</td><td>{rrw_count[system][1]['pass']}/{total_rrw_iod1} Pass</td><td>{esid_count['pass_count']}/{total_log} Pass</td><td>{esid_count['memtest_count']}/{total_log} Pass</td></tr>"
                    except:
                        summary_table += f"<tr><td>{system}</td><td> NA </td><td> NA </td><td>{esid_count['pass_count']}/{total_log} Pass</td><td>{esid_count['memtest_count']}/{total_log} Pass</td></tr>"
                else:
                    summary_table += f"<tr><td>{system}</td><td> NA </td><td> NA </td><td>{esid_count['pass_count']}/{total_log} Pass</td><td>{esid_count['memtest_count']}/{total_log} Pass</td></tr>"
            if not pmu_train_result:
                pmu_train_result = "No PMU training error detected."
            else:
                pmu_train_result = "PMU failed channel:<br>" + pmu_train_result + "<br>"
                pmu_train_result += "<br>Memtest Absent channel:<br>"
                for system, esid_count in esid_data.items():
                    pmu_train_result += f"{system} : {memtest_result[system]}"
        else:        
            if not pmu_train_result:
                pmu_train_result = "PMU training failure check will be available on undecoded log to avoid duplicate counting "
            if not summary_table:
                summary_table = "RRW/Memtest checking will be available on undecoded log to avoid duplicate counting"
        
        # Output the HTML file
        parse_to_html(mdt_html, pmu_train_result, summary_table, order_result, missing_print, analysis_result)
    except:
        print("[MDT HTML]: Fail to generate summary table")    


def MDT_process(file_path):
    # Check if the user selected a valid file or directory
    rrw_csv = ""
    esid_csv= ""
    memtest_csv = ""
    ordered_result={}
    missing_print=""
    analysis_result=""
    if file_path and os.path.exists(file_path):
        if os.path.isdir(file_path):
            #process csr dump
            csr_files = get_csrdump_from_directory(file_path)
            log_files = get_logfiles_from_directory(file_path)
            decoded_logs = get_decodedlogfiles_from_directory(file_path)
            newdir = os.path.join(file_path, f"MDT_output")
            mdt_html = os.path.join(newdir, f"MDT_report.html")
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            if csr_files:
                jmp_csv = os.path.join(newdir, f"MDT_csr_consolidated_jmp.csv")
                analysis_csv = os.path.join(newdir, f"MDT_csr_analysis.csv")
                try:
                    trained_csr_csv(csr_files, jmp_csv, analysis_csv)
                    phycsr_subset(jmp_csv)
                except:
                    print("CSR dump error")
            if log_files:
                rrw_csv = os.path.join(newdir, f"MDT_rrw_consolidated.csv")
                memtest_csv = os.path.join(newdir, f"MDT_memtest_consolidated.csv")
                postcode_csv = os.path.join(newdir, f"MDT_postcode_consolidated.csv")                
                try:
                    rrw_error_count(log_files, rrw_csv)
                except:
                    print("RRW checking error")
                
                try:
                    check_memtest(log_files, memtest_csv)
                except:
                    print("ESID completion & memtest checking error")
                try:
                    get_postcodefile(log_files, postcode_csv)
                except:
                    print("Postcode checking error")
            elif decoded_logs:
                rrw_csv = os.path.join(newdir, f"MDT_rrw_consolidated.csv")
                memtest_csv = os.path.join(newdir, f"MDT_memtest_consolidated.csv")
                postcode_csv = os.path.join(newdir, f"MDT_postcode_consolidated.csv") 
                try:
                    rrw_error_count(decoded_logs, rrw_csv)
                except:
                    print("RRW checking error")                
                try:
                    check_memtest(decoded_logs, memtest_csv)
                except:
                    print("ESID completion & memtest checking error")
                try:
                    get_postcodefile(decoded_logs, postcode_csv)
                except:
                    print("Postcode checking error")                
            if decoded_logs:
                mr_read_csv = os.path.join(newdir, f"MDT_mr_read_consolidated.csv")
                try:
                    mr_readout(decoded_logs, mr_read_csv)
                except:
                    print("MR read error")
                dcsdca_stat_csv = os.path.join(newdir, f"MDT_dcsdca_eyeSTAT_consolidated.csv")
                rdwr_stat_csv = os.path.join(newdir, f"MDT_rdwr_eyeSTAT_consolidated.csv")
                mdteye = os.path.join(newdir, f"MDT_eye")
                jmp_logcsv = os.path.join(newdir, f"MDT_log_consolidated_jmp.csv")
                analysis_logcsv = os.path.join(newdir, f"MDT_log_analysis.csv")           
                if not os.path.exists(mdteye):
                    os.mkdir(mdteye)
                try:
                    ordered_result, missing_print, analysis_result= log_to_csv(decoded_logs, jmp_logcsv, analysis_logcsv, mdteye)
                except:
                    print("[LOG]: Log to csv fail")

                try:
                    rd_wr = PMU_Eye(decoded_logs, mdteye)
                    #rd_wr.main()
                except:
                    print("Read Write eye parsing error")
                try:
                    rd_scan = Rd_Eye_Scan(decoded_logs, mdteye)
                    #rd_scan.main()
                except:
                    print("Rd eye scan parsing error")
        else:
            if os.path.exists(file_path):
                newdir, ext = os.path.splitext(os.path.abspath(file_path))
                newdir = os.path.join(os.path.dirname(file_path), f"MDT_output")
                if not os.path.exists(newdir):
                    os.mkdir(newdir)
                if "log" in ext:
                    log_files=[file_path]
                    rrw_csv = os.path.join(newdir, f"MDT_rrw_consolidated.csv")
                    rrw_error_count(log_files, rrw_csv)
                if "csv" in ext:
                    csr_files =[file_path]
                    jmp_csv = os.path.join(newdir, f"MDT_csr_consolidated_jmp.csv")
                    trained_csr_csv(csr_files, jmp_csv, "")
            else:
                sys.exit(f"File {file_path} does not exist")
        MDT_summary_table(mdt_html, rrw_csv, memtest_csv, ordered_result, missing_print, analysis_result)
        print("MDT file generated")
    else:
        print("No valid file or directory selected, exiting...")
        sys.exit(1)



if __name__ == "__main__":
    # Check if the script is run with an argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = ""

    # If no argument or invalid path, prompt the user
    if not file_path or not os.path.exists(file_path):
        print("No valid file or directory provided, prompting user to select one...")
        file_path = select_file_or_directory()

    MDT_process(file_path)
  


