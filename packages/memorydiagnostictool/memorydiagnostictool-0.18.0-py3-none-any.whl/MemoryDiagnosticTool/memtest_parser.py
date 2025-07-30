#!/usr/bin/env python3
"""Parser for memtest results (ESID Complete Success), miscompares, and missing channels."""

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd

def parse_memtest_umcs(file_name, system_name, bios, output_file):
    """Does the memtest parsing.

    Returns:
        int: Number of errors found.
    """
    with open(file_name, "r") as file:
        # Read all lines from the file
        input_text = file.readlines()
    iod0, iod1 = split_IOD0_IOD1(input_text)
    # pop_string_0 = r"Socket 0 Channel (\d+) Dimm 0 --> DIMM Not Present"
    pop_string = r"No DIMMs Found on Channel (\d+)"
    # memtest_string_0 = r"Agesa Mem Test on channel (\d+),"
    memtest_string = r"Agesa Mem Test on Node (\d+) Channel (\d+) UMC (\d+),"
    # miscompare_string = r"Failed memory test at address"
    # complete_string = r"General ESID Complete Success"
    train_fail_str = r"Channel (\d+) PHY (\d+) PMU Training Failed."
    pmu_train_fails = []
    pmu_train_status = "Pass"
    fail_count = 0    
    errors = 0
    esid_complete_match0 = False
    esid_complete_match1 = False

    miscompare_match0 = False
    miscompare_match1 = False

    s0_d0_dimms = {0: True, 1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True}
    s0_d1_dimms = {0: True, 1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True}
    # s1_dimms = []
    s0_d0_memtest_umcs = {
        0: False,
        1: False,
        2: False,
        3: False,
        4: False,
        5: False,
        6: False,
        7: False,
        8: False,
        9: False,
        10: False,
        11: False,
        12: False,
        13: False,
        14: False,
        15: False,
    }
    s0_d1_memtest_umcs = {
        0: False,
        1: False,
        2: False,
        3: False,
        4: False,
        5: False,
        6: False,
        7: False,
        8: False,
        9: False,
        10: False,
        11: False,
        12: False,
        13: False,
        14: False,
        15: False,
    }
    # s1_memtest_umcs = []
    for line in iod0:
        dimm_match = re.search(pop_string, line)
        if dimm_match:
            s0_d0_dimms[int(dimm_match.group(1))] = False
        memtest_umc_match = re.search(memtest_string, line)
        if memtest_umc_match:
            s0_d0_memtest_umcs[2*int(memtest_umc_match.group(2))+int(memtest_umc_match.group(3))] = True
        if "Failed memory test at address" in line:
            miscompare_match0 = True
            errors += 1
        if "General ESID Complete Success" in line:
            esid_complete_match0 = True
        #Check PMU Train failure
        ptf_match = re.search(train_fail_str, line)
        if ptf_match:
            fail_count += 1
            channel = int(ptf_match.group(1))
            phy = int(ptf_match.group(2))
            # Set the corresponding PHY in the dictionary to True
            pmu_train_fails.append(f"Iod0_Ch{channel}_Phy{phy}")  # Collect the failure information
            pmu_train_status = "Fail"        

    for line in iod1:
        dimm_match = re.search(pop_string, line)
        if dimm_match:
            s0_d1_dimms[int(dimm_match.group(1))] = False
        memtest_umc_match = re.search(memtest_string, line)
        if memtest_umc_match:
            s0_d1_memtest_umcs[2*int(memtest_umc_match.group(2))+int(memtest_umc_match.group(3))] = True
        if "Failed memory test at address" in line:
            miscompare_match1 = True
            errors += 1
        if "General ESID Complete Success" in line:
            esid_complete_match1 = True
        #Check PMU Train failure
        ptf_match = re.search(train_fail_str, line)
        if ptf_match:
            fail_count += 1
            channel = int(ptf_match.group(1))
            phy = int(ptf_match.group(2))
            # Set the corresponding PHY in the dictionary to True
            pmu_train_fails.append(f"Iod1_Ch{channel}_Phy{phy}")  # Collect the failure information
            pmu_train_status = "Fail"   

    fl = Path(file_name).name

    absent_list = []
    for i in range(8):
        if s0_d0_dimms[i] and not (s0_d0_memtest_umcs[2 * i] and s0_d0_memtest_umcs[2 * i + 1]):
            absent_list.append(f"S0 IOD0 Ch{i}")
            # print(f"{fl}: Socket 0 IOD 0 Channel {i} is present but not tested in Agesa Mem Test")
        if s0_d1_dimms[i] and not (s0_d1_memtest_umcs[2 * i] and s0_d1_memtest_umcs[2 * i + 1]):
            absent_list.append(f"S0 IOD1 Ch{i}")
            # print(f"{fl}: Socket 0 IOD 1 Channel {i} is present but not tested in Agesa Mem Test")
    if len(absent_list) > 0:
        # print(f"{fl}: {', '.join(absent_list)} is present but not tested in Agesa Mem Test")
        print(f"{fl}: {absent_list} present but not tested in Agesa Mem Test")
        errors += 1
    if miscompare_match0 or miscompare_match1:
        print(f"{fl}: S0 Agesa Mem Test miscompares on {'IOD0' if miscompare_match0 else ''} {'IOD1' if miscompare_match1 else ''}")
        errors += 1

    print(f"{fl}: S0 ESID Complete: IOD0 {'Pass' if esid_complete_match0 else 'Fail'}, IOD1 {'Pass' if esid_complete_match1 else 'Fail'}")

    miscompare_iods = []
    if miscompare_match0:
        miscompare_iods.append("IOD0")
    if miscompare_match1:
        miscompare_iods.append("IOD1")

    df_am = {
        "Log File": [fl],
        "System": [system_name],
        "BIOS": [bios],
        "Training Status":[pmu_train_status],
        "PMU Training Failures Channel":[pmu_train_fails],
        "IOD0 ESID Pass": ["Pass" if esid_complete_match0 else "Fail"],
        "IOD1 ESID Pass": ["Pass" if esid_complete_match1 else "Fail"],
        "Any Miscompares": [miscompare_iods],
        "Channels Absent From Memtest": [absent_list],
    }
    df = pd.DataFrame(df_am)
    df.to_csv(output_file, mode="a", header=False, index=False)

    return errors


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
    """Get all .csv files from the given directory.

    Returns:
        list: Log file paths
    """
    log_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if os.path.splitext(file)[1] in [".log", ".txt", ""] and os.path.isfile(os.path.join(directory, file))
    ]
    return log_files

def get_bios_hostname(base):
    bios = ""
    hostname = ""
    text = base.split("_")
    if len(text)>1:
        bios = text[0]
        hostname = text[1]      
    for item in text:
        if item.startswith("V") or item.startswith("03"):
            bios = item
        if ("congo" in item) or ("morocco" in item):
            hostname = item
    return bios, hostname

def check_memtest(inputlog, memtest_output):
    header_data = {"Log File":[],"System":[],"BIOS":[],"Training Status":[], "PMU Training Failures Channel":[], "IOD0 Pass":[],"IOD1 Pass":[], "Miscompares":[], "Channels Absent From Memtest":[]}
    df =pd.DataFrame(header_data)
    df.to_csv(memtest_output, mode="w", header=True, index=False)
    for file in inputlog:
        base = os.path.splitext(os.path.basename(file))[0]
        bios, hostname = get_bios_hostname(base)
        try:
            parse_memtest_umcs(file, hostname, bios, memtest_output)
        except:
            print("ESID: Fail to process file: ",file)
    print("ESID complete & memtest results parsing results are saved in the file: ", memtest_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract whether all UMCs are present in Agesa memtest")
    parser.add_argument("input", help="Input file name")
    parser.add_argument("--system", default="null", help="System name")
    parser.add_argument("--bios", default="null", help="BIOS version")
    args = parser.parse_args()

    header_data = {"Log File":[],"System":[],"BIOS":[],"Training Status":[], "PMU Training Failures Channel":[], "IOD0 Pass":[],"IOD1 Pass":[], "Miscompares":[], "Channels Absent From Memtest":[]}
    df =pd.DataFrame(header_data)

    fail_count = 0

    if os.path.isdir(args.input):
        log_files = get_files_from_directory(args.input)
        newdir, ext = os.path.splitext(os.path.abspath(log_files[0]))
        newdir = f"{newdir}_memtest_umc_consolidated"
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        # out_csv = os.path.join(newdir, f"{log_files[0]}_memtest_umc_consolidated.csv")
        out_csv = Path(newdir) / f"{Path(log_files[0]).stem}_memtest_umc_consolidated.csv"
        df.to_csv(out_csv, mode="w", header=True, index=False)
        for file in log_files:
            base = os.path.splitext(os.path.basename(file))[0]
            fail_count += parse_memtest_umcs(file, args.system, args.bios, out_csv)
        print("Memtest parsing results are saved in the file: ", out_csv)
    else:
        if os.path.exists(args.input):
            newdir, ext = os.path.splitext(os.path.abspath(args.input))
            newdir = f"{newdir}_memtest_umc_consolidated"
            base = os.path.splitext(os.path.basename(args.input))[0]
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            # out_csv = os.path.join(newdir, f"{base}_memtest_umc_consolidated.csv")
            out_csv = Path(newdir) / f"{base}_memtest_umc_consolidated.csv"
            df.to_csv(out_csv, mode="w", header=True, index=False)
            fail_count += parse_memtest_umcs(args.input, args.system, args.bios, out_csv)
            print("Memtest parsing results are saved in the file: ", out_csv)
        else:
            sys.exit(f"File {args.input} does not exist")