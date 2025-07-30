import argparse
import glob
import os
import pandas as pd
import re

def get_files_from_directory(directory):
    """Recursively get all .log files from the given directory and its subdirectories."""
    log_files = []
    # os.walk will recursively go through the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        # For each directory, check for .log files
        log_files.extend(glob.glob(os.path.join(root, "*.log*")))
    print("Decoded Log:")
    print(log_files)
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


def split_Register(input_lines):

    # Initialize variables to store the two sections
    start_MR_marker = "BDAT Schema 8 Type 2, DIMM Mode Register"
    start_RCD_marker = "BDAT Schema 8 Type 3, DIMM RCD Register"
    start_PHY_marker = "BDAT Schema 8 Type 8, Training Data PHY Register Contents"

    section1_lines = []  # First section
    section2_lines = []  # Second section
    section3_lines = []  # Second section
    crop_MR_started = False
    crop_RCD_started = False
    crop_PHY_started = False
    # Loop through lines and split based on markers
    for line in input_lines:

        if start_MR_marker in line:
            crop_MR_started = True  

        if start_RCD_marker in line:
            crop_MR_started = False
            crop_RCD_started = True  
         
        if start_PHY_marker in line:
            crop_PHY_started = True
            crop_RCD_started = False
        
        if "Memory ABL Completed" in line:
            crop_PHY_started = False

        if crop_MR_started:
            section1_lines.append(line)  
        if crop_RCD_started:            
            section2_lines.append(line)
        if crop_PHY_started:
            section3_lines.append(line)


    return section1_lines, section2_lines,section3_lines

def process_data(data):
    result = []
    for key, value in data.items():
        
        channel, ranks, subchannel,mode,register,dbytes = key
        entry = {
            "Channel":channel,
            "Ranks": ranks,
            "subchannel(phy)": subchannel,
            "Mode": mode,
            "Param": register,
            "DBYTE": dbytes,
            "trained_value":value
            
        }
        
        result.append(entry)
    return result


def process_phy_data(data):
    result = []
    for key, value in data.items():
        
        channel, ranks, subchannel,mode,register,dbytes,bit = key
        entry = {
            "Channel":channel,
            "subchannel(phy)": subchannel,
            "Ranks": ranks,
            "Mode": mode,
            "Param": register,
            "DBYTE": dbytes,
            "BIT":bit,
            "trained_value":value
            
        }
        
        result.append(entry)
    return result




def calculate_standard_deviation_and_range(analysis_csv):
    # Step 1: Read the CSV data
    df_analysis = pd.read_csv(analysis_csv)
    # Ensure that the 'trained_value' column is included in the columns of interest

    # Step 2: Identify the columns related to 'trained_value' and runX (dynamically find columns that start with 'run')
    columns_of_interest = ["trained_value"] + [col for col in df_analysis.columns if col.startswith("run")]

    # Step 3: Iterate through each row and calculate the standard deviation and range
    df_analysis["standard_deviation"] = df_analysis[columns_of_interest].std(axis=1, ddof=0)
    df_analysis["range"] = df_analysis[columns_of_interest].max(axis=1) - df_analysis[columns_of_interest].min(axis=1)

    # Step 4 Add pass/fail if range >7
    df_analysis["Pass_Fail"] = df_analysis["range"].apply(lambda x: "Fail" if x > 7 else "Pass")

    # Step 5 Check if 'Param' is 'MRL' and 'trained_value' is not between 14 and 17 for all run columns
    df_analysis["Pass_Fail"] = df_analysis.apply(
        lambda row: "Fail" if (row["Param"] == "MRL" and not (14 <= row["trained_value"] <= 17)) else row["Pass_Fail"],
        axis=1,
    )
    run_columns = [col for col in df_analysis.columns if col.startswith("run")]
    df_analysis["Pass_Fail"] = df_analysis.apply(
        lambda row: "Fail" if (row["Param"] == "MRL" and not all(14 <= row[col] <= 17 for col in run_columns)) else row["Pass_Fail"],
        axis=1,
    )

    # Step 6: Copy 'byte' value to new column 'nibble' for 'WL' or 'RXEN' params
    #df_analysis["nibble"] = df_analysis.apply(
    #    lambda row: row["nibble"] if row["Param"] in ["WL", "RXEN"] else "", axis=1
    #)
    # Step 7: Write the updated DataFrame back to the CSV
    df_analysis.to_csv(analysis_csv, index=False)

    # Step 8 Print out/return failures/all pass
    failures = df_analysis[df_analysis["Pass_Fail"] == "Fail"]

    # Step 9: Create a new DataFrame with the max of each range column for each param
    max_range_per_param = df_analysis.groupby("Param")["range"].max().reset_index()
    max_range_per_param.columns = ["Param", "Max Range"]

    # Print the new DataFrame
    print("Max range for each param:")
    print(max_range_per_param)
    if not failures.empty:
        print("Failing rows:")
        print(failures)
        return failures
    else:
        print("All Pass")
        return None


def process_BDAT(filename, run,inputbase, inputhost, inputbios, analysis_csv             
                 ):
    


    with open (filename,'r') as file:
        input_text = file.readlines()


    MR,RCD,PHY = split_Register(input_text)
    MR_result = {}
    rcd_result = {}
    phy_result = {}
    decoded_MR_pattern =  re.compile(r"Channel\s*(\d+)\s*Rank\s*(\d)\s*SubChannel\s*(\d)")
    decoded_RCD_pattern =  re.compile(r"Channel\s*(\d+)\s*Dimm\s*(\d)\s*SubChannel\s*(\d)")
    CS_delay = False
    CA_delay = False
    dfimrl = False
    RxPBDly = False
    RxClkDly = False
    RxEnDly = False
    TxDqsDly = False
    TxDqDly = False
    VrefDac = False
    page =0 
    for line in MR:

        decoded_MR_match = decoded_MR_pattern.search(line)

        if decoded_MR_match:
            ch,r,sub = decoded_MR_match.groups()

        if line.strip().startswith("Dram"):
            index = line.split()
    
        if line.startswith("MR"):
            register = line.split()[0]
            for i in range(len(index)):
                key = (ch,r,sub,"Mode Register",register,index[i])
                #print(key)
                MR_result[key] = int(line.split()[i+1],16)

    for line in RCD:

        decoded_RCD_match = decoded_RCD_pattern.search(line)

        if decoded_RCD_match:
            ch,dimm,sub = decoded_RCD_match.groups()

        if line.strip().startswith("x"):
            index = line.split()
            
        
        if line.strip().startswith("Page"):
            page = line.split()[1]
        
        if line.strip().startswith("RW"):
            register = line.split()[0]
            for i in range(len(index)):
                if(len(index) == len(line.split()[1:])):
                    key = (ch,dimm,sub,"RCD Register",register[0:3]+index[i][1],f"Page{page}")
                    rcd_result[key] = int(line.split()[i+1],16)
    
    pstate=0
    for line in PHY:

        if line.startswith("Channel"):
            ch = int(line.split()[1])
            subchannel = 0
            ranks = 0
            if (line.find("PState") != -1):
                pstate = int(line.split()[3])
            if (line.find("Rank") != -1):
                ranks = int(line.split()[3])
    
        if line.startswith("CS delay"):
            CS_delay = True

        if CS_delay == True:
            if line.startswith("Subchannel"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                subchannel = numbers[0]
                ranks = numbers[1:5]
                data = numbers[5:9]
                for value in range(len(ranks)):
                    keys = (ch,ranks[value],subchannel,"PHY Register","CS Delay","","")
                    phy_result[keys] = int(data[value],16)
                       
            if "Copy CS Delay" in line:
                CS_delay = False

        if line.startswith("CA delay"):
            CA_delay = True

        if CA_delay == True:
            if line.startswith("Subchannel"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                subchannel = numbers[0]
                ranks = numbers[2:9]
                data = numbers[9:16]
                for value in range(len(ranks)):
                    keys = (ch,ranks[value],subchannel,"PHY Register","CA Delay","","")
                    phy_result[keys] = int(data[value],16)
                       
            if "Copy CA Delay" in line:
                CA_delay = False
    
        if line.startswith("DFIMRL"):
            dfimrl = True
        

        if dfimrl == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                dbyte = numbers[0:9]
                data = numbers[10:19]
                for value in range(len(dbyte)):
                    keys = (ch,ranks,subchannel,"PHY Register","DFIMRL",dbyte[value],"")
                    phy_result[keys] = int(data[value],16)
            
            if "Copy DFIMRL to" in line:
                dfimrl = False

        if line.startswith("RxPBDly"):
            RxPBDly = True

        if RxPBDly == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                dbyte = numbers[0]
                bit = numbers[1:9]
                data = numbers[9:17]
                for value in range(len(bit)):
                    keys = (ch,ranks,subchannel,"PHY Register","RxPBDly",dbyte,bit[value])
                    phy_result[keys] = int(data[value],16)

            if "Copy RxPBDly to" in line:
                RxPBDly = False

        if line.startswith("RxClkDly"):
            RxClkDly = True

        if RxClkDly == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                dbyte = numbers[0]
                Nibble = numbers[1:3]
                data = numbers[3:5]
                for value in range(len(Nibble)):
                    keys = (ch,ranks,subchannel,"PHY Register","RxClkDly",dbyte,Nibble[value])
                    phy_result[keys] = int(data[value],16)

            if "Copy RxClkDly to" in line:
                RxClkDly = False

        if line.startswith("RxEnDly"):
            RxEnDly = True

        if RxEnDly == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                dbyte = numbers[0]
                Nibble = numbers[1:3]
                data = numbers[3:5]
                for value in range(len(Nibble)):
                    keys = (ch,ranks,subchannel,"PHY Register","RxEnDly",dbyte,Nibble[value])
                    phy_result[keys] = int(data[value],16)

            if "Copy RxEnDly to" in line:
                RxEnDly = False

        if line.startswith("TxDqsDly"):
            TxDqsDly = True

        if TxDqsDly == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                dbyte = numbers[0]
                Nibble = numbers[1:3]
                data = numbers[3:5]
                for value in range(len(Nibble)):
                    keys = (ch,ranks,subchannel,"PHY Register","TxDqsDly",dbyte,Nibble[value])
                    phy_result[keys] = int(data[value],16)

            if "Copy TxDqsDly to" in line:
                TxDqsDly = False

        if line.startswith("TxDqDly"):
            TxDqDly = True

        if TxDqDly == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)
                dbyte = numbers[0]
                bit = numbers[1:9]
                data = numbers[9:17]
                for value in range(len(bit)):
                    keys = (ch,ranks,subchannel,"PHY Register","TxDqDly",dbyte,bit[value])
                    phy_result[keys] = int(data[value],16)

            if "Copy TxDqDly to" in line:
                TxDqDly = False

        if line.startswith("VrefDac"):
            dac = int(''.join(filter(str.isdigit, line)))
            VrefDac = True

        if VrefDac == True:
            if line.startswith("Dbyte"):
                numbers = re.findall(r'\b0[xX][0-9a-fA-F]+\b|\b[0-9a-fA-F]+\b', line)              
                dbyte = numbers[0]
                bit = numbers[1:9]
                data = numbers[9:17]
                for value in range(len(bit)):
                    keys = (ch,ranks,subchannel,"PHY Register",f"VrefDac{dac}",dbyte,bit[value])
                    phy_result[keys] = int(data[value],16)

            if f"Copy VrefDac1 to" in line:
                VrefDac = False

    df_MR_result = process_data(MR_result)
    df_MR_result = pd.DataFrame(df_MR_result)
    
    df_RCD_result = process_data(rcd_result)
    df_RCD_result = pd.DataFrame(df_RCD_result)

    df_PHY_result = process_phy_data(phy_result)
    df_PHY_result = pd.DataFrame(df_PHY_result)

    df = pd.concat(
        [
            df_MR_result,
            df_RCD_result,
            df_PHY_result
        ]
    ).reset_index(drop=True)

    hstnme = [inputhost]
    bios = [inputbios]
    df["Hostname"] = hstnme * len(df)
    df["BIOS"] = bios * len(df)
    df["Filename"] = inputbase
    df["run"] = run
    
    ordered_columns = [
        "Filename",
        "Hostname",
        "BIOS", 
        "Channel",
        "Ranks",
        "subchannel(phy)",
        "Mode",
        "Param",
        "DBYTE",
        "BIT",
        "trained_value",
        "run",
    ]
    df = df[ordered_columns]

    hstnme = [inputhost]
    bios = [inputbios]
    
    if analysis_csv:
        df_analysis = pd.concat(
            [
                df_MR_result,
                df_RCD_result,
                df_PHY_result
            ]
        ).reset_index(drop=True)

        df_analysis["Hostname"] = hstnme * len(df)
        df_analysis["BIOS"] = bios * len(df)
        df_analysis["Filename"] = inputbase
        
        ordered_columns_analysis = [
            "Filename",
            "Hostname",
            "BIOS", 
            "Channel",
            "Ranks",
            "subchannel(phy)",
            "Mode",
            "Param",
            "DBYTE",
            "BIT",
            "trained_value",
    
        ]

        df_analysis = df_analysis[ordered_columns_analysis]

        if run == 0:
            df_analysis.to_csv(analysis_csv, mode="a", header=False, index=False)
        else:
            df_analysis = pd.read_csv(analysis_csv)
            trained_value_column = df["trained_value"]
            run_column_name = f"run{run}"
            df_analysis[run_column_name] = trained_value_column
            df_analysis.to_csv(analysis_csv, mode="w", header=True, index=False)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load BDAT log files ")
    parser.add_argument("log", help="log file to process", default=None)
    args = parser.parse_args()

    header_newdata = {
        "Filename": [],
        "Hostname": [],
        "BIOS": [],
        "Channel": [],
        "Ranks": [],
        "subchannel(phy)": [],
        "Mode":[],        
        "Param": [],
        "DBYTE":[],
        "BIT":[],
        "trained_value": [],
        
    }
    df_new = pd.DataFrame(header_newdata)
    run = 0
    hostname = ""
    bios = ""
    if os.path.isdir(args.log):
        log_files = get_files_from_directory(args.log)
        newdir, ext = os.path.splitext(os.path.abspath(log_files[0]))
        base = os.path.splitext(os.path.basename(log_files[0]))[0]
        if not os.path.exists(newdir):
            os.mkdir(newdir)

        analysis_csv = os.path.join(newdir, f"{base}_log_analysis.csv")
        df_new.to_csv(analysis_csv, mode="w", header=True, index=False)
        for file in log_files:
            base = os.path.splitext(os.path.basename(file))[0]
            bios, hostname = get_bios_hostname(base)
            
            process_BDAT(file,run, base, hostname, bios, analysis_csv)
            run = run + 1
        calculate_standard_deviation_and_range(analysis_csv)

    print("csv file generated")