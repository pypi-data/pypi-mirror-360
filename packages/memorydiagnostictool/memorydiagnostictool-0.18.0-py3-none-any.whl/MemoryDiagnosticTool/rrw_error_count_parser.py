#!/usr/bin/env python3
"""Parser for rrw results and errors."""

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd

# import weisshorn.memory.umc.utils.test_utils as tu


def extract_rrw(file_name, system_name, bios, output_file, suppress):
    with open(file_name, "r") as file:
        # Read all lines from the file
        input_text = file.readlines()
    iod0, iod1 = split_IOD0_IOD1(input_text)

    iod0passflag = getting_pass_status(iod0)
    iod1passflag = getting_pass_status(iod1)
    search_string = r"Read Bubble: (\d+)\s+Write Bubble: (\d+)\s+Seed: (\d+)\s+Error Status\s+Error Count : (\d+)\s+Nibble Error Status : (\d+)"
    # \s+Nibble Error Status : (\d+)\s+DQ Errors[71:0] : 0x(?:[\da-fA-F]\s)+DQ Capture DQ[71:0] : 0x(?:[\da-fA-F]\s)+"
    iod0 = "".join(iod0).replace("\t", "").replace("\n", "").replace("\r", "").replace("*", "")
    iod1 = "".join(iod1).replace("\t", "").replace("\n", "").replace("\r", "").replace("*", "")
    # print(iod1)
    iod0_matches = re.finditer(search_string, iod0)
    iod1_matches = re.finditer(search_string, iod1)

    fc = 0

    iod0list = []
    iod1list = []
    iod0pass = True
    iod1pass = True
    for match in iod0_matches:
        rrw_data = {
            "Log File": [Path(file_name).name],
            "System": [system_name],
            "BIOS": [bios],
            "IOD": [0],
            "Read Bubble": [match.group(1)],
            "Write Bubble": [match.group(2)],
            "Seed": [match.group(3)],
            "Error Count": [match.group(4)],
            "Nibble Error Status": [match.group(5)],
        }
        # "DQ Errors[71:0]":[match.group(6)],"DQ Capture DQ[71:0]":[match.group(7)]}
        if match.group(4) != "0":
            iod0pass = False
            fc += 1
        if not suppress:
            iod0list.append(rrw_data)

    for match in iod1_matches:
        rrw_data = {
            "Log File": [Path(file_name).name],
            "System": [system_name],
            "BIOS": [bios],
            "IOD": [1],
            "Read Bubble": [match.group(1)],
            "Write Bubble": [match.group(2)],
            "Seed": [match.group(3)],
            "Error Count": [match.group(4)],
            "Nibble Error Status": [match.group(5)],
        }
        # "DQ Errors[71:0]":[match.group(6)],"DQ Capture DQ[71:0]":[match.group(7)]}
        if match.group(4) != "0":
            iod1pass = False
            fc += 1
        if not suppress:
            iod1list.append(rrw_data)

    fn = Path(file_name).name
    if iod0pass and iod0passflag and iod1pass and iod1passflag:
        print(f"RRW Memory Test Passed for log: {fn}")
    elif (iod0pass is not iod0passflag) or (iod1pass is not iod1passflag):
        print(f"RRW Results Mismatch for log: {fn}. Either logging is wrong or system didn't reach RRW.")
    elif not (iod0pass and iod0passflag) and not (iod1pass and iod1passflag):
        print(f"RRW Memory Test Failed for IOD0 and IOD1 in log: {fn}")
    elif not (iod0pass and iod0passflag):
        print(f"RRW Memory Test Failed for IOD0 in log: {fn}")
    elif not (iod1pass and iod1passflag):
        print(f"RRW Memory Test Failed for IOD1 in log: {fn}")

    if not suppress:
        for rrw_data in iod0list:
            rrw_data["IOD Passed"] = iod0pass
            rrw_data["IOD Passed Log Flag"] = iod0passflag
            if not suppress:
                df = pd.DataFrame(rrw_data)
                df.to_csv(output_file, mode="a", header=False, index=False)

        for rrw_data in iod1list:
            rrw_data["IOD Passed"] = iod1pass
            rrw_data["IOD Passed Log Flag"] = iod1passflag
            if not suppress: 
                df = pd.DataFrame(rrw_data)
                df.to_csv(output_file, mode="a", header=False, index=False)

    return fc


def getting_pass_status(text):
    for line in text:
        if "RRW Memory Test Passed" in line:
            return True
    return False

def split_IOD0_IOD1(input_lines):
    # Initialize variables to store the two sections
    start_marker = "ESID_LOG_NODE1 log, Start"
    end_marker = "ESID_LOG_NODE1 log, End"
    section1_lines = []  # First section
    section2_lines = []  # Second section
    crop_started = False
    # Loop through lines and split based on markers
    for line in input_lines:
        if start_marker in line:
            crop_started = True  # Start cropping once the start marker is found
            continue  # Skip to the next iteration
        if crop_started:
            if end_marker in line:
                crop_started = False  # Stop cropping once the end marker is found
            else:
                section2_lines.append(line)  # Add all lines between the markers to section2
        else:
            section1_lines.append(line)  # Add lines before the start_marker to section1
    return section1_lines, section2_lines


def get_files_from_directory(directory):
    """Get all .csv files from the given directory."""
    log_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if os.path.splitext(file)[1] in [".log", ".txt", ""] and os.path.isfile(os.path.join(directory, file))
    ]  # print(log_files)
    return log_files

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

def rrw_error_count(inputlog, rrw_output):
    header_data = {
        "Log File": [],
        "System": [],
        "BIOS": [],
        "IOD": [],
        "Read Bubble": [],
        "Write Bubble": [],
        "Seed": [],
        "Error Count": [],
        "Nibble Error Status": [],
        "IOD Passed": [],
        "IOD Passed Log Flag": [],
    }
    df =pd.DataFrame(header_data)
    df.to_csv(rrw_output, mode="w", header=True, index=False)
    for file in inputlog:
        base = os.path.splitext(os.path.basename(file))[0]
        bios, hostname = get_bios_hostname(base)
        try:
            extract_rrw(file, hostname, bios, rrw_output, "")
        except:
            print("RRW: Fail to process file: ",file) 
    print("RRW data parsing results are saved in the file: ", rrw_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract R/W Bubble, Seed, Error Count, Nibble Error Status, DQ Errors[71:0], DQ Capture DQ[71:0]")
    parser.add_argument("input", help="Input file name")
    parser.add_argument("--system", default="null", help="System name")
    parser.add_argument("--bios", default="null", help="BIOS version")
    parser.add_argument("--suppress", help="Suppress writing to csv file", action="store_true")
    args = parser.parse_args()

    header_data = {
        "Log File": [],
        "System": [],
        "BIOS": [],
        "IOD": [],
        "Read Bubble": [],
        "Write Bubble": [],
        "Seed": [],
        "Error Count": [],
        "Nibble Error Status": [],
        "IOD Passed": [],
        "IOD Passed Log Flag": [],
    }
    # "DQ Errors[71:0]":[],"DQ Capture DQ[71:0]":[]}
    df = pd.DataFrame(header_data)

    fail_count = 0

    if os.path.isdir(args.input):
        log_files = get_files_from_directory(args.input)
        if args.suppress:
            out_csv = "NULL"
        else:
            newdir, ext = os.path.splitext(os.path.abspath(log_files[0]))
            newdir = f"{newdir}_rrw_consolidated"
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            out_csv = Path(newdir) / f"{Path(log_files[0]).stem}_rrw_consolidated.csv"
            df.to_csv(out_csv, mode="w", header=True, index=False)
        for file in log_files:
            base = os.path.splitext(os.path.basename(file))[0]
            fail_count += extract_rrw(file, args.system, args.bios, out_csv, args.suppress)
        print("RRW data parsing results are saved in the file: ", out_csv)
    else:
        if os.path.exists(args.input):
            if args.suppress:
                out_csv = "NULL"
            else:
                newdir, ext = os.path.splitext(os.path.abspath(args.input))
                newdir = f"{newdir}_rrw_consolidated"
                base = os.path.splitext(os.path.basename(args.input))[0]
                if not os.path.exists(newdir):
                    os.mkdir(newdir)
                out_csv = Path(newdir) / f"{base}_rrw_consolidated.csv"
                df.to_csv(out_csv, mode="w", header=True, index=False)
            fail_count += extract_rrw(args.input, args.system, args.bios, out_csv, args.suppress)
            print("RRW data parsing results are saved in the file: ", out_csv)
        else:
            sys.exit(f"File {args.input} does not exist")