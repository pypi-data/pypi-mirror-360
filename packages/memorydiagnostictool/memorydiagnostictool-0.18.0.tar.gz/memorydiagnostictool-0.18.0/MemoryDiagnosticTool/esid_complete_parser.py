import sys
import os
import pandas as pd
import argparse
import glob
from pathlib import Path


def extract_esid_complete(file_name, system_name, bios, output_file):
    with open(file_name, 'r') as file:
        # Read all lines from the file
        input_text = file.readlines()
    iod0, iod1 = split_IOD0_IOD1(input_text)

    # search_string = r"General ESID Complete Success"
    # iod0 = ''.join(iod0)
    # iod1 = ''.join(iod1)

    # iod0pass = re.match(search_string, iod0) is not None
    # iod1pass = re.match(search_string, iod1) is not None

    iod0pass = getting_pass_status(iod0)
    iod1pass = getting_pass_status(iod1)


    if(os.path.splitext(file_name)[1] == ".log"):
        fl = Path(file_name).name
        print(f"{fl}: IOD0 {'Pass' if iod0pass else 'Fail'}, IOD1 {'Pass' if iod1pass else 'Fail'}")
        df_am = {"Log File":[fl],"System":[system_name],"BIOS":[bios],"IOD0 Pass":["Pass" if iod0pass else "Fail"],"IOD1 Pass":["Pass" if iod1pass else "Fail"]}
        df = pd.DataFrame(df_am)
        df.to_csv(output_file, mode='a', header=False, index=False)
    return

def getting_pass_status(text):
    for line in text:
       if "General ESID Complete Success" in line:
          return True
    return False

def get_files_from_directory(directory):
    """Get all .csv files from the given directory."""
    log_files = glob.glob(os.path.join(directory, "*.log*"))
    # print(log_files)
    return log_files

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
            ##section2_lines.append(line)  # Include the start_marker line in section2
            continue  # Skip to the next iteration
        if crop_started:
            if end_marker in line:
               crop_started = False  # Stop cropping once the end marker is found
            else:
               section2_lines.append(line)  # Add all lines between the markers to section2
        else:
            section1_lines.append(line)  # Add lines before the start_marker to section1
    return section1_lines, section2_lines

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

def check_esid_complete(inputlog, esidcomplete_output):
    header_data = {"Log File":[],"System":[],"BIOS":[],"IOD0 Pass":[],"IOD1 Pass":[]}
    df =pd.DataFrame(header_data)
    df.to_csv(esidcomplete_output, mode="w", header=True, index=False)
    
    for file in inputlog:
        base = os.path.splitext(os.path.basename(file))[0]
        bios, hostname = get_bios_hostname(base)
        try:
            extract_esid_complete(file, hostname, bios, esidcomplete_output)
        except:
            print("ESID: Fail to process file: ",file)
    print("ESID complete results parsing results are saved in the file: ", esidcomplete_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract whether boot log passes Agesa Memtest')
    parser.add_argument('input', help='Input file name')
    parser.add_argument('--system', help='System name')
    parser.add_argument('--bios', help='BIOS version')
    args = parser.parse_args()

    header_data = {"Log File":[],"System":[],"BIOS":[],"IOD0 Pass":[],"IOD1 Pass":[]}
    df =pd.DataFrame(header_data)

    if os.path.isdir(args.input):
        log_files = get_files_from_directory(args.input)
        newdir, ext = os.path.splitext(os.path.abspath(log_files[0]))
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        out_csv = os.path.join(newdir, f"{log_files[0]}_pass_consolidated.csv")
        df.to_csv(out_csv, mode="w", header=True, index=False)
        for file in log_files:
            base = os.path.splitext(os.path.basename(file))[0]
            extract_esid_complete(file, args.system, args.bios, out_csv)
        print("ESID complete results parsing results are saved in the file: ", out_csv)
    else:
        if os.path.exists(args.input):
            newdir, ext = os.path.splitext(os.path.abspath(args.input))
            base = os.path.splitext(os.path.basename(args.input))[0]
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            out_csv = os.path.join(newdir, f"{base}_pass_consolidated.csv")
            df.to_csv(out_csv, mode="w", header=True, index=False)
            extract_esid_complete(args.input, args.system, args.bios, out_csv)
            print("ESID complete results parsing results are saved in the file: ", out_csv)
        else:
            sys.exit(f"File {args.input} does not exist")