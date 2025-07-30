################################################################################################################################################
# Author      : Eu Poh Rung
# Description : Script use to extract out MR values data into excel sheet 
# Date        : 01-03-2025
################################################################################################################################################
# script calling method
# py  script name     --folder     log file path to be run
# py "read_log_ai.py" --folderpath C:\Users\pohruneu\Downloads\testlog
################################################################################################################################################
import pandas as pd
import re, os, argparse, datetime

def hex_to_decimal(hex_str):     
    try:    
        # Convert hex to decimal    
        decimal_number = int(hex_str, 16)    
        return decimal_number    
    except ValueError:    
        # Handle the case where the input is not a valid hexadecimal string    
        print("Invalid hexadecimal number")    
        return None  

# def hex_to_binary(hex_bin_str):     
#     try:    
#         # Convert hex to binary    
#         binary_number = "{0:08b}".format(int(hex_bin_str, 16))
#         binary_number_16 = binary_number.zfill(16)
#         # print(binary_number)  
#         return binary_number_16    
#     except ValueError:    
#         # Handle the case where the input is not a valid binary string    
#         print("Invalid binary number")    
#         return None 

#def mr_select(mr):
    # mr_value = mr
    # if mr_value == 'MrlBuffer':

    #     mrl_info
    # elif mr_value == '0':
    #     mr0_info
    # elif mr_value == '3':
    #     mr3_info
    # elif mr_value == '8':
    #     mr8_info
    # elif mr_value == '10':
    #     mr10_info
    # elif mr_value == '34':
    #     mr34_info
    # elif mr_value == '35':
    #     mr35_info
    # elif mr_value == '40':
    #     mr40_info  

# def mr35_info(op2, op3, op4):
#     #add up bit to form CS/CK/CA ODT
#     odt_bin = op2 + op3 + op4
#     if odt_bin == '000':
#         return "RTT_OFF"
#     elif odt_bin == '001':
#         return "240"
#     elif odt_bin == '010':
#         return "120"
#     elif odt_bin == '011':
#         return "80"
#     elif odt_bin == '100':
#         return "60"
#     elif odt_bin == '101':
#         return "48"
#     elif odt_bin == '110':
#         return "40"
#     elif odt_bin == '111':
#         return "34"
#     else:
#         return "N/A"

# def mr40_info(op2, op3, op4):
#     #add up bit to form CS/CK/CA ODT
#     odt_bin = op2 + op3 + op4
#     if odt_bin == '000':
#         return "0 Clock"
#     elif odt_bin == '001':
#         return "1 Clock"
#     elif odt_bin == '010':
#         return "2 Clock"
#     elif odt_bin == '011':
#         return "3 Clock"
#     elif odt_bin == '100':
#         return "RFU"
#     elif odt_bin == '101':
#         return "RFU"
#     elif odt_bin == '110':
#         return "RFU"
#     elif odt_bin == '111':
#         return "RFU"
#     else:
#         return "N/A"


def _parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folderpath", help="Path to folder containing MsgBlock Logs", type=str)
    return parser.parse_args()

def show_time():
    run_time = datetime.datetime.now()
    print(f'{run_time.hour} : {run_time.minute} . {run_time.second}')

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

def read_MR(file_name, hostname, bios, mr_out):
    with open(file_name, 'r') as file:
        # Read all lines from the file
        input_text = file.readlines()
        
    important = []
    keep_phrases = ["Passing MRL Value after adding MrlBuffer:",
                    "PHYINIT: BTFW: MR0[",
                    "PHYINIT: BTFW: MR3[",
                    "PHYINIT: BTFW: MR8[",
                    "PHYINIT: BTFW: MR10[",
                    "PHYINIT: BTFW: MR11[",
                    "PHYINIT: BTFW: MR12[",
                    "PHYINIT: BTFW: MR35[",
                    "PHYINIT: BTFW: MR40["]

    # Filter out only important lines from the log
    for line in input_text:
        for phrase in keep_phrases:
            if phrase in line:
                important.append(line)
                break
    
    filename = os.path.splitext(os.path.basename(file_name))[0]
    seperate_filename = filename.split('_')
    # Read file and collect data into a temporary DataFrame
    temp_data = []
    for word in important:
        input_string = word
        # Extracting values for each important line using regex
        if keep_phrases[0] in input_string:
            values = re.findall(r'CHANNEL: (\d+),\s+PHY: (\d+),\s+PHYINIT: (.+): Passing MRL Value after adding (\w+): (0x[\da-fA-F]+)', input_string)
            data = [(file_name, bios, hostname, seperate_filename[2], val[0], val[1], val[2], val[3], '', '', val[4], '') for val in values]
            temp_data.extend(data)
        else:
            values = re.findall(r'CHANNEL: (\d+),\s+PHY: (\d+),\s+PHYINIT: (.+): MR(\d+)\[dbyte(\d+).nibble(\d+)\]: (0x[\da-fA-F]+)', input_string)
            #dec_convert = hex_to_decimal(val[6])
            # Create dataframe for each line from the extracted values
            data = [(file_name, bios, hostname, seperate_filename[2], val[0], val[1], val[2], int(val[3]), int(val[4]), int(val[5]), val[6], hex_to_decimal(val[6])) for val in values]
            temp_data.extend(data)

    # Create a DataFrame from the processed data and append it to the main DataFrame
    column_names = ['Log','BIOS','Hostname','Run', 'CHANNEL', 'PHY', 'PHYINIT', 'MR', 'DB', 'NIBBLE', 'VAL', 'Dec']
    df = pd.DataFrame(temp_data, columns=column_names)

    # Append DataFrame to the output file
    df.to_csv(mr_out, mode='a', index=False, header=False)


def mr_readout(inputlog, mr_read_csv):
    # Create 'MR_value_Date({time_n.year}_{time_n.month}_{time_n.day})Time({time_n.hour}_{time_n.minute}).csv' file with column names
    column_names = {'Log':[],'BIOS':[],'Hostname':[],'Run':[], 'CHANNEL':[], 'PHY':[], 'PHYINIT':[], 'MR':[], 'DB':[], 'NIBBLE':[], 'VAL':[], 'Dec':[]}
    # Create an empty DataFrame to store all the data
    all_data = pd.DataFrame(column_names)
    all_data.to_csv(mr_read_csv, mode="w", header=True, index=False)
    for file in inputlog:
        base = os.path.splitext(os.path.basename(file))[0]
        bios, hostname = get_bios_hostname(base)
        try:
            read_MR(file, hostname, bios, mr_read_csv)
        except:
            print("MR: Fail to process file: ",file) 
    print("MR parsing results are saved in the file: ", mr_read_csv)



def read_log(folder_path):
    # Get all files in the folder
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.log')]

    # Create 'MR_value_Date({time_n.year}_{time_n.month}_{time_n.day})Time({time_n.hour}_{time_n.minute}).csv' file with column names
    column_names = ['Log','BIOS','Hostname','Run', 'CHANNEL', 'PHY', 'PHYINIT', 'MR', 'DB', 'NIBBLE', 'VAL', 'Dec']
    time_n = datetime.datetime.now()
    name = f'MR_value_Date({time_n.year}_{time_n.month}_{time_n.day})Time({time_n.hour}_{time_n.minute}).csv'  
    final_name = os.path.join(folder_path, name)

    # Create an empty DataFrame to store all the data
    all_data = pd.DataFrame(columns=column_names)
    #all_data.to_csv(mr_read_csv, mode="w", header=True, index=False)

    for file_path in file_paths:
        # Check if the file exists before processing
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue
        
        # To know which file is running now and time taken 
        print(file_path)
        filename = os.path.split(file_path)
        seperate_filename = filename[1].split('_')
        
        show_time()

        important = []
        keep_phrases = ["Passing MRL Value after adding MrlBuffer:",
                        "PHYINIT: BTFW: MR0[",
                        "PHYINIT: BTFW: MR3[",
                        "PHYINIT: BTFW: MR8[",
                        "PHYINIT: BTFW: MR10[",
                        "PHYINIT: BTFW: MR11[",
                        "PHYINIT: BTFW: MR12[",
                        "PHYINIT: BTFW: MR35[",
                        "PHYINIT: BTFW: MR40["]

        with open(file_path) as f:
            lines = f.readlines()

        # Filter out only important lines from the log
        for line in lines:
            for phrase in keep_phrases:
                if phrase in line:
                    important.append(line)
                    break

        # Read file and collect data into a temporary DataFrame
        temp_data = []
        for word in important:
            input_string = word
            # Extracting values for each important line using regex
            if keep_phrases[0] in input_string:
                values = re.findall(r'CHANNEL: (\d+),\s+PHY: (\d+),\s+PHYINIT: (.+): Passing MRL Value after adding (\w+): (0x[\da-fA-F]+)', input_string)
                data = [(filename[1], seperate_filename[0], seperate_filename[1], seperate_filename[2], val[0], val[1], val[2], val[3], '', '', val[4], '') for val in values]
                temp_data.extend(data)
            else:
                values = re.findall(r'CHANNEL: (\d+),\s+PHY: (\d+),\s+PHYINIT: (.+): MR(\d+)\[dbyte(\d+).nibble(\d+)\]: (0x[\da-fA-F]+)', input_string)
                #dec_convert = hex_to_decimal(val[6])
                # Create dataframe for each line from the extracted values
                data = [(filename[1], seperate_filename[0], seperate_filename[1], seperate_filename[2], val[0], val[1], val[2], int(val[3]), int(val[4]), int(val[5]), val[6], hex_to_decimal(val[6])) for val in values]
                temp_data.extend(data)

        # Create a DataFrame from the processed data and append it to the main DataFrame
        df = pd.DataFrame(temp_data, columns=column_names)
        all_data = pd.concat([all_data, df], ignore_index=True)
        
        show_time()

    # Write the final DataFrame 'all_data' to the output file
    all_data.to_csv(final_name, index=False, mode='w', header=True)

if __name__ == "__main__":
    args = _parse()
    read_log(args.folderpath)