"""
Version : 2.0
Author  : saukae.tan@amd.com
Desc    : extract training value from the log that is available
"""

import re
import sys
import os
import pandas as pd
import argparse
import glob
import numpy as np
import site
import shutil
from collections import defaultdict
from MemoryDiagnosticTool.chseq import sort_text_by_channel_phy
from MemoryDiagnosticTool.MDT_eye_template import html_eye_plot
def signed_32bit(n, bits, mode):
    """Convert an unsigned 32-bit integer to a signed 32-bit integer using two's complement."""
    n = n & 0xFFFFFFFF  # Ensure it's within 32 bits
    if (n & (1 << (bits - 1))) != 0: 
        if (mode == 'delay') or (mode == 'vref') or (mode=='write_dfe') :
            n = n - (1 << bits)
            return n
        else:
            n = (1 << (bits-1)) - n  #handle msb is sign bit
            return n
    else:
        return n

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
        if ("congo" in item) or ("morocco" in item) or ("kenya" in item):
            hostname = item
    return bios, hostname


def get_files_from_directory(directory):
    """Get all .csv files from the given directory."""
    csv_files = glob.glob(os.path.join(directory, "*.csv*"))
    print(csv_files)
    return csv_files


def convert_to_xy_dicts(coord_list):
    """
    Convert a list of [x, y] pairs into a list of {"x": x, "y": y} dictionaries.

    Args:
        coord_list (list): List of [x, y] coordinate pairs.

    Returns:
        list: List of {"x": x, "y": y} dictionaries.
    """
    return [{"x": x, "y": y} for x, y in coord_list]



def convert_qca_eye_to_named_variables(qca_eye):
        # Group keys by the first five elements (excluding dev)
        grouped = defaultdict(list)
        for key in qca_eye:
            group_key = key[:5]  # (soc, iod, ch, sub, rank)
            grouped[group_key].append(key)
        # Process each group
        results = {}
        for group_key, full_keys in grouped.items():
            soc, iod, ch, sub, rank = group_key
            var_name = f"QCAp{soc}i{iod}c{ch}s{sub}r{rank}_data"
            results[var_name] = [convert_to_xy_dicts(qca_eye[key]) for key in sorted(full_keys)]
        return results

import shutil
import os

def update_qca_html_from_results(results_dict, template_file="qca_eye.html", output_prefix="file"):
    for i, var_name in enumerate(results_dict.keys(), start=1):
        output_file = f"{output_prefix}{i}_qca.html"
        shutil.copy(template_file, output_file)
        with open(output_file, "r") as f:
            lines = f.readlines()
        replacement_line = f'const {var_name} = results["{var_name}"];\n'
        with open(output_file, "w") as f:
            for line in lines:
                if line.strip().startswith(f"const {var_name} = [...defaultData]"):
                    f.write(replacement_line)
                else:
                    f.write(line)


def find_left_neighbors(points, centerX, centerY):
        candidates = [pt for pt in points if pt[0] < centerX]
        upper = min((pt for pt in candidates if pt[1] >= centerY), key=lambda pt: abs(pt[1] - centerY), default=None)
        lower = min((pt for pt in candidates if pt[1] < centerY), key=lambda pt: abs(pt[1] - centerY), default=None)
        return upper, lower

def find_right_neighbors(points, centerX, centerY):
        candidates = [pt for pt in points if pt[0] > centerX]
        upper = min((pt for pt in candidates if pt[1] >= centerY), key=lambda pt: abs(pt[1] - centerY), default=None)
        lower = min((pt for pt in candidates if pt[1] < centerY), key=lambda pt: abs(pt[1] - centerY), default=None)
        return upper, lower

def find_top_neighbors(points, centerX, centerY):
        candidates = [pt for pt in points if pt[1] > centerY]
        left = min((pt for pt in candidates if pt[0] <= centerX), key=lambda pt: abs(pt[0] - centerX), default=None)
        right = min((pt for pt in candidates if pt[0] > centerX), key=lambda pt: abs(pt[0] - centerX), default=None)
        return left, right

def find_bottom_neighbors(points, centerX, centerY):
        candidates = [pt for pt in points if pt[1] < centerY]
        left = min((pt for pt in candidates if pt[0] <= centerX), key=lambda pt: abs(pt[0] - centerX), default=None)
        right = min((pt for pt in candidates if pt[0] > centerX), key=lambda pt: abs(pt[0] - centerX), default=None)
        return left, right



def get_interpolated_point(p1, p2, centerX, centerY, direction):
        if p1 is None or p2 is None:
            return None
        x1, y1 = p1
        x2, y2 = p2
        if direction == 'horizontal':
            if x2 == x1:
                return ((x1 + x2) / 2, centerY)
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            x = (centerY - b) / m
            return (x, centerY)
        else:
            if y2 == y1:
                return (centerX, (y1 + y2) / 2)
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            y = m * centerX + b
            return (centerX, y)

# Main plotting function
def calculate_eye_with_distances(eye_points, centerX, centerY):
        eye_points = np.array(eye_points)

        # Get pairs of neighbor points
        neighbors = {
            "left": find_left_neighbors(eye_points, centerX, centerY),
            "right": find_right_neighbors(eye_points, centerX, centerY),
            "top": find_top_neighbors(eye_points, centerX, centerY),
            "bottom": find_bottom_neighbors(eye_points, centerX, centerY),
        }

        directions = {
            "left": "horizontal",
            "right": "horizontal",
            "top": "vertical",
            "bottom": "vertical",
        }

        distances = {}

        for label, (p1, p2) in neighbors.items():
            interp = get_interpolated_point(p1, p2, centerX, centerY, directions[label])
            if interp:
                 distance = np.linalg.norm(np.array([centerX, centerY]) - np.array(interp))
                 distances[label] = distance
            else:
                 distances[label] = None  # or 0.0 or np.nan depending on your use case

        return distances





def compare_byte_sequence_by_group(dataset1, dataset2):
        # Group values by (channel, subchannel, rank)
        def group_by_channel(data):
            grouped = defaultdict(dict)
            for (soc, iod, ch, subch, rank, byte), val in data.items():
                grouped[(soc, iod, ch, subch, rank)][byte] = val
            return grouped
        grouped1 = group_by_channel(dataset1)
        grouped2 = group_by_channel(dataset2)
        # Compare each group
        mismatch_group={}
        for key in grouped1:
            if key not in grouped2:
                mismatch_group[key]="missing"
                continue    # Missing group in dataset2
            bytes1 = grouped1[key]
            bytes2 = grouped2[key]
            if set(bytes1.keys()) != set(bytes2.keys()):
                mismatch_group[key]="key mismatched" # Mismatched byte keys
                continue
            # Get sorted byte order based on values
            sorted_bytes1 = sorted(bytes1, key=lambda b: bytes1[b], reverse=True)
            sorted_bytes2 = sorted(bytes2, key=lambda b: bytes2[b], reverse=True)
            if sorted_bytes1 != sorted_bytes2:
                mismatch_group[key]=f"bytes mismatched:<br>WL   :{sorted_bytes1}<br>RxEN:{sorted_bytes2}" # Order mismatch
                continue
        return mismatch_group

def process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, dfe):
    result=[]
    header_match = header_pattern.search(prev[6])
    if not header_match:
        return []
    if dfe:
        channel, subchannel, rank, tap = header_match.groups()
    else:
        channel, subchannel, rank = header_match.groups()
    subheader_match = subheader_pattern.search(prev[5])
    if not subheader_match:
        return []
    channel2, subchannel2 = subheader_match.groups()
    if channel != channel2 or subchannel != subchannel2:
        return []
    for i in range(5):
        data_match = data_pattern.search(prev[i])
        if data_match:
            groups= data_match.groups()
            db = int(groups[2])
            if dfe:            
                result.extend([((int(channel), int(subchannel), int(rank), int(tap), db*8+j), int(groups[j+3])) for j in range(8)])
            else:
                result.extend([((int(channel), int(subchannel), int(rank), db*8+j), int(groups[j+3])) for j in range(8)])
    return result

def process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, mode):
    
    result=[]
    if mode == 'mrl':       
        header_match = header_pattern.search(curr)
        if header_match:
           channel, subchannel, rank, value = header_match.groups()
           result.extend([((int(channel), int(subchannel), int(rank,16)), int(value,16))])
           return result
        return []
    
    header_match = header_pattern.search(prev[6])
    if not header_match:
        return []
    if mode=='rdac' or mode=='idac'or mode== 'oneui':
        channel, subchannel = header_match.groups()
    else:
        channel, subchannel, rank = header_match.groups()
    subheader_match = subheader_pattern.search(prev[5])
    if not subheader_match:
        return []
    channel2, subchannel2 = subheader_match.groups()
    if channel != channel2 or subchannel != subchannel2:
        return []
    if mode=='wrdelay' or mode=='wrvref':
        for i in range(5):
            data_match = data_pattern.search(prev[i])
            if data_match:
                groups= data_match.groups()
                db = int(groups[2]) 
                result.extend([((int(channel), int(subchannel), int(rank), db*2+j), int(groups[j+3])) for j in range(2)])
    elif mode == 'oneui':
        data_match = data_pattern.search(prev[4])
        if data_match:
            groups= data_match.groups()
            try:
                data=[int(c) for c in groups[2].split('|')]
                if (len(data)>=10):
                    result.extend([((int(channel), int(subchannel), j), int(data[j])) for j in range(10)])    
            except:
                #print(f'oneui data not int')
                return []                
    else:    
        for i in range(5):
            data_match = data_pattern.search(prev[i])
            if data_match:
                groups= data_match.groups()
                try:
                    data=[int(c) for c in groups[2].split('|')]
                    db = data[0]
                    if (len(data)>=9):
                        if mode=='rdac':
                            result.extend([((int(channel), int(subchannel), 0, db*8+j), int(data[j+1])) for j in range(8)])
                        elif mode=='idac':
                            result.extend([((int(channel), int(subchannel), 1, db*8+j), int(data[j+1])) for j in range(8)])
                        else:      
                            result.extend([((int(channel), int(subchannel), int(rank), db*8+j), int(data[j+1])) for j in range(8)])
                except:
                    #print(f'values not int')
                    return []
    return result

def process_rdwrlines_hwa( curr, pattern, mode):
    
    result=[]
    #print(f"current {curr}")
    
    match = pattern.search(curr)
    
    if not match:
        #print(f"no header match")
        return []
        
    channel = int(match.group(1))
    subchannel = int(match.group(2))
 
    if mode=='readvref_rk0_hwa' or mode=='readvref_rk1_hwa':
        values_str = match.group(5)
    else:
        values_str = match.group(6)
 
    data=[int(c) for c in values_str.split('|')]
    db = int(data[0])

        #for i in range(1, 7):
        #    print(f"Group %d: %s" % (i, match.group(i)))
    
    if (len(data)>=9):
        if mode=='readvref_rk0_hwa':
            result.extend([((int(channel), int(subchannel), 0, db*8+j), int(data[j+1])) for j in range(8)])
        elif mode=='readvref_rk1_hwa':
            result.extend([((int(channel), int(subchannel), 1, db*8+j), int(data[j+1])) for j in range(8)])
        else:
            rk = int(match.group(4)) 
            #print ("db %d, value %d " % ((db*8), int(data[1])))
            result.extend([((int(channel), int(subchannel), int(rk), db*8+j), int(data[j+1])) for j in range(8)])
                                   
    return result
    
def process_mr_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern):
        header_match = header_pattern.search(prev2)
        if not header_match:
            return []
        channel, subchannel, mr, rank = header_match.groups()
        subheader_match = subheader_pattern.search(prev1)
        if not subheader_match:
            return []
        channel2, subchannel2 = subheader_match.groups()
        if channel != channel2 or subchannel != subchannel2:
            return []
        data_match = data_pattern.search(curr)
        if not data_match:
            return []
        groups = data_match.groups()
        if len(groups) != 12 or groups[0] != channel or groups[1] != subchannel:
            return []
        # Return list of (key, value) tuples
        return [
            ((int(channel), int(subchannel), int(rank), int(mr), i), int(groups[i + 2], 16))
            for i in range(10)
        ]


def process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, hex_enable):
    header_match = header_pattern.search(prev2)
    if not header_match:
        return []

    channel, subchannel, rank = header_match.groups()

    subheader_match = subheader_pattern.search(prev1)
    if not subheader_match:
        return []

    channel2, subchannel2 = subheader_match.groups()

    if channel != channel2 or subchannel != subchannel2:
        return []

    data_match = data_pattern.search(curr)
    if not data_match:
        return []

    groups = data_match.groups()
    if len(groups) != 12 or groups[0] != channel or groups[1] != subchannel:
        return []

    # Return list of (key, value) tuples
    if hex_enable:
        return [
            ((int(channel), int(subchannel), int(rank), i), int(groups[i + 2], 16))
            for i in range(10)
        ]
    else:
        return [
            ((int(channel), int(subchannel), int(rank), i), int(groups[i + 2]))
            for i in range(10)
        ]

def detect_qca_rank(curr):
    rank_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*.*?<<---\s*Rank:(\d+)\s*--->>"
    )
    rank_match = rank_pattern.search(curr)
    if rank_match:
        channel, subchannel, rank = rank_match.groups()
        return int(rank)
    return -1
def detect_dcs_eye_start(curr):
    start_pattern=re.compile(
    #CHANNEL: 0,  PHY: 0,  PHYINIT: BTFW1: [DBV_MINOR] [DCS] Exiting PASS 2D scan initial
        #r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Cs\s*Eye\s*->>"
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_MINOR\]\s*\[DCS\]\s*Exiting\s*PASS\s*2D\s*scan\s*initial\s*"
    )
    end_pattern=re.compile(
    #CHANNEL: 0,  PHY: 1,  PHYINIT: BTFW1: [DBV_MINOR] [DCA] Starting 2D scan initial
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_MINOR\]\s*\[DCA\]\s*Starting\s*2D\s*scan\s*initial\s*"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
        channel, subchannel = start_match.groups()
        key = (channel, subchannel)
        return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (channel, subchannel)
            return key, False
    return (), False


def detect_qcs_eye_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Cs\s*Eye\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Qca\s*Eye\s*->>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
        channel, subchannel = start_match.groups()
        key = (channel, subchannel)
        return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (channel, subchannel)
            return key, False
    return (), False

def get_eye_base(curr):
    eyebase_pattern=re.compile(
        r"EyePtsLowerBase\s*=\s*(\d+)\s*EyePtsUpperBase\s*=\s*(\d+)"
    )
    match = eyebase_pattern.search(curr)
    if match:
        lowerbase, upperbase = match.groups()
        return True, int(lowerbase), int(upperbase)
    return False, 0, 0

def detect_read_scan_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*.*?Eyescan\s*Starts\.\s*Rank\s*=\s*(\d+)"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Rd\s*Eye\s*,\s*Odd\s*Phase\s*->>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
       channel, subchannel, rank = start_match.groups()
       key = (int(channel), int(subchannel), int(rank))
       return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (int(channel), int(subchannel))
            return key, False
    return (), False


def detect_read_eye_even_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Rd\s*Eye\s*,\s*Even\s*Phase\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Rd\s*Eye\s*,\s*Odd\s*Phase\s*->>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
       channel, subchannel = start_match.groups()
       key = (int(channel), int(subchannel))
       return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (int(channel), int(subchannel))
            return key, False
    return (), False

def detect_read_eye_odd_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Rd\s*Eye\s*,\s*Odd\s*Phase\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Rd\s*Eye\s*,\s*Even\s*Phase\s*->>"
    )
    final_end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Wr\s*Eye\s*->>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
       channel, subchannel = start_match.groups()
       key = (int(channel), int(subchannel))
       return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (int(channel), int(subchannel))
            return key, False
        else:
            end_match = final_end_pattern.search(curr)
            if end_match:
                channel, subchannel = end_match.groups()
                key = (int(channel), int(subchannel))
                return key, False            
    return (), False

def detect_write_eye_start(curr):
    #CHANNEL: 0,  PHY: 0,  PHYINIT: <<- 2D Eye Print, Wr Eye ->>
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Wr\s*Eye\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW:\s*\[DBV_INFO\]\s*\[WR\s*TRAIN\]\s*<<\s*Rank:\s*\d+,\s*)?TxDqFineDelay\s*>>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
       channel, subchannel = start_match.groups()
       key = (int(channel), int(subchannel))
       return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel = end_match.groups()
            key = (int(channel), int(subchannel))
            return key, False
    return (), False

def detect_qca_eye_start(curr):
    start_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<-\s*2D\s*Eye\s*Print,\s*Qca\s*Eye\s*->>"
    )
    end_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*TxDQS\s*Coarse\s*Delay\s*>>"
    )    
    start_match = start_pattern.search(curr)
    if start_match:
       channel, subchannel = start_match.groups()
       key = (channel, subchannel)
       return key, True
    else:
        end_match = end_pattern.search(curr)
        if end_match:
            channel, subchannel, r = end_match.groups()
            key = (channel, subchannel)
            return key, False
    return (), False


def process_cs_eye(prev3, prev2, prev1, curr, cs_start, mode):
    #pattern definition
    if mode =='qcs':
        #<<--- Rank: 0, Ch: 1, Dram: 0 --->>
        dev_pattern = re.compile(
            #r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*Rank:\s*(\d+),\s*Ch:\s*(\d+),\s*Dram:\s*(\d+)\s*--->>"
            r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*.*?Rank:\s*(\d+)"
            r"(?:,\s*Ch:\s*(\d+),\s*Dram:\s*(\d+))?\s*--->>"
        )
    elif mode =='dcs':
        #CHANNEL: 0,  PHY: 1,  PHYINIT: <<--- Rank: 0, Ch: 0 --->>
        dev_pattern = re.compile(
            r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*Rank:\s*(\d+)"
            r"(?:,\s*Ch:\s*(\d+))?\s*--->>"
        )
    
    offset_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*DelayOffset:\s*(\d+),\s*CenterDelay:\s*(\d+),\s*CenterVref:\s*(\d+)\s*--->>"
    )
    data_pattern=re.compile(
        r"Train Eye EyePts(.*?):(.*)"
    ) 
    #extract eye from log
    cs_eye={}    
    upperbase = 0 #255
    lowerbase = 0 #128
    match = dev_pattern.search(prev3)
    if match:
        if mode == 'qcs':
            ch, sub, r, _ch, dm = match.groups()
        else:
            ch, sub, r, _ch = match.groups()

        if (ch, sub) in cs_start:
            #print(f'ch {ch} and sub {sub} and rank {r}')
            if cs_start[ch, sub]== True:
                match = offset_pattern.search(prev2)
                if match:
                    c, s, delayoffset, centerdelay, centervref = match.groups()
                    match = data_pattern.search(prev1)
                    if match:
                        eyepts, data= match.groups()
                        data2=[int(c) for c in data.split()]
                        #print(f"ch sub r delayoffset is {ch} {sub} {r} {delayoffset}")
                        if eyepts=='Upper':
                            cs_eye[int(ch), int(sub), int(r)]=[[i+int(delayoffset), int(val-upperbase)] for i, val in enumerate(data2) if val != 0]
                        else:
                            cs_eye[int(ch), int(sub), int(r)]=[[i+int(delayoffset), int(val-lowerbase)] for i, val in enumerate(data2) if val != 511]
                        match = data_pattern.search(curr)
                        #print(f"data2 is {data2}")
                        if match:
                            eyepts, data= match.groups()
                            data2=[int(c) for c in data.split()]
                            if eyepts=='Upper':
                                cs_eye[int(ch), int(sub), int(r)].extend([[i+int(delayoffset), int(val-upperbase)] for i, val in enumerate(data2) if val != 0])
                            else:
                                cs_eye[int(ch), int(sub), int(r)].extend([[i+int(delayoffset), int(val-lowerbase)] for i, val in enumerate(data2) if val != 511]) 

    return cs_eye

    
 
def process_qca_eye(prev3, prev2, prev1, curr, qca_start, rank):
    #pattern definition
    #v9bd and above
    #<<- Rank: 0, QCA Dev: 0 ->>  Rank\s*:\s*(\d+),\s*QCA\s*Dev\s*:\s*(\d+)
    dev_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:.*?Rank\s*:\s*(\d+),\s*QCA\s*Dev:\s*(\d+).*?"
    )
    offset_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*DelayOffset:\s*(\d+),\s*CenterDelay:\s*NA,\s*CenterVref:\s*NA\s*--->>"
    )
    data_pattern=re.compile(
        r"Train Eye EyePts(.*?):(.*)"
    ) 
    #extract eye from log
    qca_eye={}    
    upperbase = 0 #255
    lowerbase = 0 #128
    x_delay = list(range(0, 384, 3))
    
    match = dev_pattern.search(prev3)
    if match:
        ch, sub, rk, dev = match.groups()
        if (ch, sub) in qca_start:
            if qca_start[ch, sub]== True:
                match = offset_pattern.search(prev2)
                #x, y, delayoffset = match.groups()
                if match:
                    match = data_pattern.search(prev1)
                    if match:
                        eyepts, data= match.groups()
                        data2=[int(c) for c in data.split()]
                        if eyepts=='Upper':
                            #qca_eye[int(ch), int(sub), int(rk), int(dev)]=[[i, int(val-upperbase)] for i, val in enumerate(data2) if val != 0]
                            filtered_eye_data = [(x, val) for x, val in zip(x_delay, data2) if val != 0]
                            qca_eye[int(ch), int(sub), int(rk), int(dev)] = filtered_eye_data
                            #print(f" i and value {qca_eye[int(ch), int(sub), int(rk), int(dev)] : {data2}}")
                        else:
                            #qca_eye[int(ch), int(sub), int(rk), int(dev)]=[[i, int(val-lowerbase)] for i, val in enumerate(data2) if val != 511]
                            filtered_eye_data = [(x, val) for x, val in zip(x_delay, data2) if val != 511]
                            qca_eye[int(ch), int(sub), int(rk), int(dev)] = filtered_eye_data
                        match = data_pattern.search(curr)
                        if match:
                            eyepts, data= match.groups()
                            data2=[int(c) for c in data.split()]
                            if eyepts=='Upper':
                                #qca_eye[int(ch), int(sub), int(rk), int(dev)].extend([[i, int(val-upperbase)] for i, val in enumerate(data2) if val != 0])
                                filtered_eye_data = [(x, val) for x, val in zip(x_delay, data2) if val != 0]
                                qca_eye[int(ch), int(sub), int(rk), int(dev)].extend(filtered_eye_data)
                            else:
                                #qca_eye[int(ch), int(sub), int(rk), int(dev)].extend([[i, int(val-lowerbase)] for i, val in enumerate(data2) if val != 511]) 
                                filtered_eye_data = [(x, val) for x, val in zip(x_delay, data2) if val != 511]
                                qca_eye[int(ch), int(sub), int(rk), int(dev)].extend(filtered_eye_data)
    return qca_eye

def process_scaneye(prev2, prev1, curr, start, mode):
    ln_sel_ref = {0 : [3,1,6,7], 1 : [0,2,4,5]}

    result = {}
  
    if mode=='delay':
        #delay pattern
        #text="CHANNEL: 6,  PHY: 0,  PHYINIT: BTFW: [DBV_EYES] [RDEYE Eye Scan] lane_sel = 0, Pi offset = 4294967264"
        pattern=re.compile(
            r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:.*?lane_sel\s*=\s*(\d+),\s*Pi\s*offset\s*=\s*(\d+)"
        )
        match = pattern.search(curr)
        if match:
            ch, sub, lane_sel, offset = match.groups()
            val= signed_32bit(int(offset)&0x3F, 6, 'delay')
            result[int(ch), int(sub)] = val 
        
    elif mode=='vref':
        #vref pattern
        #text="CHANNEL: 6,  PHY: 0,  PHYINIT: BTFW: [DBV_EYES] [RDEYE Eye Scan] Rank = 0, Byte = 0, lane_sel = 0, Lane = 3, VrefLow  = 4294967176 "
        offset_pattern=re.compile(
            r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*.*?Rank\s*=\s*(\d+),\s*dbyte\s*=\s*(\d+),\s*lane_sel\s*=\s*(\d+),\s*lane\s*=\s*(\d+)"
        )
        data_pattern=re.compile(
            r"\[RXEYE\] EyePts(.*?)=(.*)"
        ) 
        x_delay = list(range(0, 64))
        
        match = offset_pattern.search(prev2)
        if match:
            ch, sub, rank, db, lane_sel, lane = match.groups()
            #if (int(ch), int(sub), int(rank)) in start:
            #    if start[int(ch), int(sub), int(rank)]== True:          
            pin = int(db)*8+ln_sel_ref[int(lane_sel)][int(lane)]
            
            match = data_pattern.search(prev1)
            if match:
                eyepts, data= match.groups()
                data2=[int(c) for c in data.split()]
                    #result[int(ch), int(sub), int(rank), int(pin)]=[[i, val] for i, val in enumerate(data2)]
                result[int(ch), int(sub), int(rank), int(pin)] = list(zip(x_delay, data2))
                #print(f"result {result}")

                match = data_pattern.search(curr)
                if match:
                    eyepts, data= match.groups()
                    data2=[int(c) for c in data.split()]
                    #print(f"data2 is {data2}")
                    result[int(ch), int(sub), int(rank), int(pin)].extend(list(zip(x_delay, data2)))
                    #print(f"result extend {result}")

            #val= signed_32bit(int(vrefbase)&0x1FF, 9, 'vref')
 
            #if val < 199 and val >-200:
            #    result[int(ch), int(sub), int(rank), pin] = val
    return result
        

def process_eye(prev3, prev2, prev1, curr, start, mode, upperbase, lowerbase):
    #pattern definition
    dev_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*Rank:\s*(\d+),\s*DB:\s*(\d+),\s*Dq:\s*(\d+)\s*--->>"
    )
    offset_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<---\s*DelayOffset:\s*(\d+),\s*CenterDelay:\s*\d+,\s*CenterVref:\s*\d+\s*--->>"
    )
    data_pattern=re.compile(
        r"Train Eye EyePts(.*?):(.*)"
    ) 
    #extract eye from log
    upeye={}
    dneye={}
    eye={}    
    match = dev_pattern.search(prev3)
    if match:
        ch, sub, rank, db, dq = match.groups()
        pin=int(db)*8+int(dq)
        if (int(ch), int(sub)) in start:
            if start[int(ch), int(sub)]== True:
                match = offset_pattern.search(prev2)
                if match:
                    _ch, _sub, offset = match.groups()
                    match = data_pattern.search(prev1)
                    if match:
                        eyepts, data= match.groups()
                        data2=[int(c) for c in data.split()]
                        if eyepts=='Upper':
                            if mode == 'read':
                                #upeye[int(ch), int(sub), int(rank), int(pin)]=[[i+int(offset), val+upperbase] for i, val in enumerate(data2)]
                                upeye[int(ch), int(sub), int(rank), int(pin)]=[[i+int(offset), val] for i, val in enumerate(data2)]
                            else:
                                upeye[int(ch), int(sub), int(rank), int(pin)]=[[i+int(offset), int(val-upperbase)] for i, val in enumerate(data2)]
                        else:
                            if mode == 'read':
                                #dneye[int(ch), int(sub), int(rank), int(pin)]=[[i+int(offset), val+lowerbase] for i, val in enumerate(data2)]
                                dneye[int(ch), int(sub), int(rank), int(pin)]=[[i+int(offset), val] for i, val in enumerate(data2)]
                            else:
                                dneye[int(ch), int(sub), int(rank), int(pin)]=[[i+int(offset), int(val-lowerbase)] for i, val in enumerate(data2)]
                    match = data_pattern.search(curr)
                    if match:
                        eyepts, data= match.groups()
                        data2=[int(c) for c in data.split()]
                        if eyepts=='Upper':
                            if mode == 'read':
                                #upeye[int(ch), int(sub), int(rank), int(pin)] =[[i+int(offset), val+upperbase] for i, val in enumerate(data2)]
                                upeye[int(ch), int(sub), int(rank), int(pin)] =[[i+int(offset), val] for i, val in enumerate(data2)]
                            else:
                                upeye[int(ch), int(sub), int(rank), int(pin)] =[[i+int(offset), int(val-upperbase)] for i, val in enumerate(data2)]
                        else:
                            if mode == 'read':
                                #dneye[int(ch), int(sub), int(rank), int(pin)] =[[i+int(offset), val+lowerbase] for i, val in enumerate(data2)]
                                dneye[int(ch), int(sub), int(rank), int(pin)] =[[i+int(offset), val] for i, val in enumerate(data2)]
                            else:
                                dneye[int(ch), int(sub), int(rank), int(pin)] =[[i+int(offset), int(val-lowerbase)] for i, val in enumerate(data2)]
                      
    try:
        for key in set(upeye.keys()).intersection(dneye.keys()):
            up_dict = dict(upeye[key])
            dn_dict = dict(dneye[key])
            common_x = set(up_dict.keys()).intersection(dn_dict.keys())
            merged = []
            for x in sorted(common_x):
                up_y = up_dict[x]
                dn_y = dn_dict[x]
                # Include upeye point if its y > dneye y
                if up_y > dn_y:
                    merged.append([x, up_y])
                # Include dneye point if its y < upeye y
                if dn_y < up_y:
                    merged.append([x, dn_y])
            if merged:
                eye[key] = merged


    except:
        return eye
    return eye

def process_dcs_value(prev1, curr):
    result = []
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[DCS\]\s*<<\s*Rank:\s*(\d+),\s*VrefCS, CSCoarseDelay, CSFineDelay, Gain, Tap\s*>>"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[DCS\]\s*VrefCS\s*=\s*(\d+),\s*CSCoarseDelay\s*=\s*(\d+),\s*CSFineDelay\s*=\s*(\d+),\s*Gain\s*=\s*(\d+),\s*Tap1\s*=\s*(\d+),\s*Tap2\s*=\s*(\d+),\s*Tap3\s*=\s*(\d+),\s*Tap4\s*=\s*(\d+)"
    )
    match = header_pattern.search(prev1)
    if match:
        channel, subchannel, rank = match.groups()
        datamatch = data_pattern.search(curr)
        if datamatch:
            channel, subchannel, vref, coarse, fine, gain, tap1, tap2, tap3, tap4 = datamatch.groups()
            result = [((int(channel), int(subchannel), int(rank)),(int(vref), int(coarse),int(fine),int(gain),int(tap1),int(tap2),int(tap3),int(tap4)))]
    return result    

def process_dca_value(prev1, curr):
    result = []
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[DCA\]\s*<<\s*(\w+),\s*VrefCA, CACoarseDelay, CAFineDelay, Gain, Tap\s*>>"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[DCA\]\s*VrefCA\s*=\s*(\d+),\s*CACoarseDelay\s*=\s*(\d+),\s*CAFineDelay\s*=\s*(\d+),\s*Gain\s*=\s*(\d+),\s*Tap1\s*=\s*(\d+),\s*Tap2\s*=\s*(\d+),\s*Tap3\s*=\s*(\d+),\s*Tap4\s*=\s*(\d+),\s*Tap5\s*=\s*(\d+),\s*Tap6\s*=\s*(\d+)"
    )
    match = header_pattern.search(prev1)
    if match:
        channel, subchannel, ca = match.groups()
        datamatch = data_pattern.search(curr)
        if datamatch:
            channel, subchannel, vref, coarse, fine, gain, tap1, tap2, tap3, tap4, tap5, tap6 = datamatch.groups()
            result = [((int(channel), int(subchannel), ca),(int(vref), int(coarse),int(fine),int(gain),int(tap1),int(tap2),int(tap3),int(tap4),int(tap5),int(tap6)))]
    return result  

def process_qcs_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*QACSDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )   
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_qcs_vref(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*VrefCS\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )   
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result


def process_qca_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*QACADelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )      
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_qcavref_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*Rank:\s*(\d+),\s*VrefCA\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )      
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result

def process_wlcoarse_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*TxDQS\s*Coarse\s*Delay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_wlfine_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*TxDQS\s*Fine\s*Delay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_wlmr3_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*MR3\s*WICA\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_wlmr7_line(prev2, prev1, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*<< Rank:\s*(\d+),\s*MR7\s*0.5tCK\s*Offset\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WL TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )    
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_rxen_coarse_line(prev2, prev1, curr):
    header_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW[^:]*:\s*\[DBV_INFO\])?\s*<<\s*Rank:\s*(\d+),\s*RxEnCoarseDly\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW[^:]*:\s*\[DBV_INFO\])?\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW[^:]*:\s*\[DBV_INFO\])?\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_rxen_fine_line(prev2, prev1, curr):
    header_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW[^:]*:\s*\[DBV_INFO\])?\s*<<\s*Rank:\s*(\d+),\s*RxEnFineDly\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW[^:]*:\s*\[DBV_INFO\])?\s*Db0Nb0\s*\|\s*Db0Nb1\s*\|\s*Db1Nb0\s*\|\s*Db1Nb1\s*\|\s*Db2Nb0\s*\|\s*Db2Nb1\s*\|\s*Db3Nb0\s*\|\s*Db3Nb1\s*\|\s*Db4Nb0\s*\|\s*Db4Nb1"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:(?:\s*BTFW[^:]*:\s*\[DBV_INFO\])?\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)"
    )
    result = process_lines(prev2, prev1, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_read_even_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*RXDQS Dpi_ClkTCode Even\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\](.*)"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'delay')
    return result

def process_read_odd_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*RXDQS Dpi_ClkCCode Odd\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\](.*)"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'delay')
    return result
    
def process_read_vref_r0(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*afe_RdacCtrl\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\](.*)"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'rdac')
    return result
    
def process_read_vref_r1(prev, curr):
    header_pattern=re.compile(
    #[RD TRAIN] << Rank: 1, afe_IdacCtrl >>
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*<<\s*Rank:\s*1,\s*afe_IdacCtrl\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\]"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[RD TRAIN\](.*)"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'idac')
    return result    

def process_read_even_delay_hwa(curr):
    #header_pattern=re.compile(
    #    r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),PHYINIT:.*?\s*,(?:\[DBV_INFO\]\s*)?,(\[RD TRAIN\])?.*?,Rank\s*=\s*(\d+),RXDQ_DPI_CODE_SRDQ_MDQ_DPI_CLKTCODE,.*?Byte\s*=\s*(\d+)\s*,(.*)"

        #r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*Rank\s*=\s*(\d+),\s*RXDQ_DPI_CODE_SRDQ_MDQ_DPI_CLKTCODE\s*(.*)"
    #)
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*"                       # channel
        r"PHY:\s*(\d+),\s*"                           # phy
        r"PHYINIT:[^:]*:\s*"                          # PHYINIT: BTFW:
        r"(?:\[DBV_INFO\]\s*)?"                       # optional [DBV_INFO]
        r"(\[RD TRAIN\])?.*?"                         # optional [RD TRAIN]
        r"Rank\s*=\s*(\d+),\s*"      
        r"(RXDQ_DPI_CODE_SRDQ_MDQ_DPI_CLKTCODE)\s+"   
        r"Byte\s*=\s*(.*)"         
    )

    result = process_rdwrlines_hwa(curr, header_pattern, 'delay_hwa')
    return result
 
def process_read_odd_delay_hwa(curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*"                      
        r"PHY:\s*(\d+),\s*"                           
        r"PHYINIT:[^:]*:\s*"                          
        r"(?:\[DBV_INFO\]\s*)?"                       # optional [DBV_INFO]
        r"(\[RD TRAIN\])?.*?"                         # optional [RD TRAIN]
        r"Rank\s*=\s*(\d+),\s*"                       # rank
        r"(RXDQ_DPI_CODE_SRDQ_MDQ_DPI_CLKCCODE)\s+"   
        r"Byte\s*=\s*(.*)"                      
    )
    
    result = process_rdwrlines_hwa(curr, header_pattern, 'delay_hwa')
    return result
    
def process_read_vref_rk0_hwa(curr):
    header_pattern=re.compile(
        #r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*,\s*RXDQ_AFE_RDACCTRL\s*(.*)" 
        r"CHANNEL:\s*(\d+),\s*"                     
        r"PHY:\s*(\d+),\s*"                          
        r"PHYINIT:[^:]*:\s*"       
        r"(?:\[DBV_INFO\]\s*)?"                       
        r"(\[RD TRAIN\])?.*?"                         
        r"(RXDQ_AFE_RDACCTRL)\s+"   
        r"Byte\s*=\s*(.*)"                    
    )
    
    result = process_rdwrlines_hwa(curr, header_pattern, 'readvref_rk0_hwa')
    return result
    
def process_read_vref_rk1_hwa(curr):
    header_pattern=re.compile(
       #r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW:\s*\[DBV_INFO\]\s*\[RD TRAIN\]\s*Rank\s*=\s*(\d+),\s*RXDQ_AFE_OS\s*(.*)"
        r"CHANNEL:\s*(\d+),\s*"                     
        r"PHY:\s*(\d+),\s*"                          
        r"PHYINIT:[^:]*:\s*"                        
        r"(?:\[DBV_INFO\]\s*)?"                       
        r"(\[RD TRAIN\])?.*?"   
        r"Rank\s*=\s*1,\s*"          
        r"(RXDQ_AFE_OS)\s+"   
        r"Byte\s*=\s*(.*)"  
    )

    result = process_rdwrlines_hwa(curr, header_pattern, 'readvref_rk1_hwa')
    return result
def process_write_nb_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*TxDqNibbleDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Nb0\s*\|\s*Nb1\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'wrdelay')
    return result    

def process_write_coarse_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*TxDqCoarseDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Dq0\s*\|\s*Dq1\s*\|\s*Dq2\s*\|\s*Dq3\s*\|\s*Dq4\s*\|\s*Dq5\s*\|\s*Dq6\s*\|\s*Dq7"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result

def process_write_fine_delay(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*TxDqFineDelay\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Dq0\s*\|\s*Dq1\s*\|\s*Dq2\s*\|\s*Dq3\s*\|\s*Dq4\s*\|\s*Dq5\s*\|\s*Dq6\s*\|\s*Dq7"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, False)
    return result
    
def process_write_dfe(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*DFE BIAS Tap\s*(\d+)\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Dq0\s*\|\s*Dq1\s*\|\s*Dq2\s*\|\s*Dq3\s*\|\s*Dq4\s*\|\s*Dq5\s*\|\s*Dq6\s*\|\s*Dq7"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*\|\s*(-?\d+)\s*"
    )
    result = process_wr_dq(prev, curr, header_pattern, subheader_pattern, data_pattern, True)
    return result
    
def process_write_vref(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*<<\s*Rank:\s*(\d+),\s*DramVref\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*Db\s*\|\s*Nb0\s*\|\s*Nb1\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*\[WR TRAIN\]\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'wrvref')
    return result

def process_oneui(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*<<\s*OneUiCode\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*"
    )
    data_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s(.*)"
    )
    result = process_rdwrlines(prev, curr, header_pattern, subheader_pattern, data_pattern, 'oneui')
    return result


def process_mrl(prev, curr):
    pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_INFO\]\s*##\s*Rank\s*(0x[0-9a-fA-F]+)\s*Passing\s*MRL\s*Value\s*\(\+MrlBuffer\):\s*(0x[0-9a-fA-F]+)\s*##"
    )     
    result = process_rdwrlines(prev, curr, pattern, "", "", 'mrl')
    return result



def process_mr_reg(prev, curr):
    header_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_MR\]\s*<<\s*MR\s*(\d+),\s*Rank:\s*(\d+)\s*>>"
    )
    subheader_pattern=re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_MR\]\s*Dev0\s*\|\s*Dev1\s*\|\s*Dev2\s*\|\s*Dev3\s*\|\s*Dev4\s*\|\s*Dev5\s*\|\s*Dev6\s*\|\s*Dev7\s*\|\s*Dev8\s*\|\s*Dev9"
    )
    data_pattern = re.compile(
        r"CHANNEL:\s*(\d+),\s*PHY:\s*(\d+),\s*PHYINIT:\s*BTFW[^:]*:\s*\[DBV_MR\]\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*"
        r"(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)\s*\|\s*(0x[0-9a-fA-F]+)"
    )
    result = process_mr_lines(prev[1], prev[0], curr, header_pattern, subheader_pattern, data_pattern)
    return result

def detect_decoded_log(filename, filename2=""):

    dcs_coarse_delay = {}
    dcs_fine_delay = {}
    dcs_vref = {}
    dcs_gain = {}
    dcs_tap1 = {}
    dcs_tap2 = {}
    dcs_tap3 = {}
    dcs_tap4 = {}
    
    dca_coarse_delay = {}
    dca_fine_delay = {}
    dca_vref = {}
    dca_gain = {}
    dca_tap1 = {}
    dca_tap2 = {}
    dca_tap3 = {}
    dca_tap4 = {}
    dca_tap5 = {}
    dca_tap6 = {}
        
    qcs_delay = {}
    qcs_vref = {}
    qca_delay = {}
    qca_vref = {}
    
    wlcoarse_value = {}
    wlfine_value = {}
    wlmr3_value = {}
    wlmr7_value = {}
    rxen_coarse_value = {}
    rxen_fine_value = {}
    
    readeven_delay = {}
    readodd_delay = {}
    read_vref = {}
    write_nb_delay = {}
    write_coarse_delay = {}
    write_fine_delay = {}
    write_vref = {}
    write_dfe_tap1 = {}
    write_dfe_tap2 = {}
    write_dfe_tap3 = {}
    write_dfe_tap4 = {}
    
    oneui={}
    mrl={}
    
    mr_reg = {}
    txrank = 0
    dcs_eye_start = {}
    dcs_eye={}
    qcs_eye_start = {}
    qcs_eye={}
    qca_eye_start = {}
    qca_eye={}
    read_scan_start = {}
    read_eye_scan={}
    read_eye_even_start = {}
    read_eye_even={}
    read_eye_odd_start = {}
    read_eye_odd={}
    write_eye_start = {}
    write_eye={}
    
    iod=0
    socket = 0
    valid_text=""
    valid_text2=""
    # Process each line in the log
    if filename:
        with open(filename, 'r') as file:
            # Read all lines from the file
            input_text = file.readlines()
        _, valid_text = sort_text_by_channel_phy(input_text)
    if filename2:
        with open(filename2, 'r') as file:
            # Read all lines from the file
            input_text2 = file.readlines()
        _, valid_text2 = sort_text_by_channel_phy(input_text2)
    
    if valid_text and valid_text2:
        split_index = len(valid_text)
        # Combine the tagged lines
        combine_text = valid_text + valid_text2
    elif valid_text:
        combine_text = valid_text
        iod= 0
    elif valid_text2:
        combine_text = valid_text2
        iod= 1
   
    rank=0
    upperbase = 0
    lowerbase = 0
    previous_line = {}
    previous_line[7] = ""        
    previous_line[6] = ""
    previous_line[5] = ""
    previous_line[4] = ""
    previous_line[3] = ""
    previous_line[2] = ""
    previous_line[1] = ""
    previous_line[0] = ""   
    for idx, line in enumerate(combine_text):
        if valid_text and valid_text2:
            iod = 0 if idx < split_index else 1
        
        dcs_key, dcs_start= detect_dcs_eye_start(line)
        if dcs_start:
            dcs_eye_start[dcs_key] = dcs_start
        elif dcs_key in dcs_eye_start:
            dcs_eye_start[dcs_key] = dcs_start
                     
        # Get DCS eye value
        temp_dcs= process_cs_eye(previous_line[2], previous_line[1], previous_line[0], line, dcs_eye_start, 'dcs')
        if temp_dcs:
            for key in temp_dcs:
                #print(f"temp_dcs[key is {key}, {temp_dcs[key]}")
                dcs_eye[socket, iod, key[0], key[1], key[2]] = temp_dcs[key] 
                
        qcs_key, qcs_start= detect_qcs_eye_start(line)
        if qcs_start:
            qcs_eye_start[qcs_key] = qcs_start
        elif qcs_key in qcs_eye_start:
            qcs_eye_start[qcs_key] = qcs_start
        # Get QCS eye value
        temp_qcs= process_cs_eye(previous_line[2], previous_line[1], previous_line[0], line, qcs_eye_start, 'qcs')
        if temp_qcs:
            for key in temp_qcs:
                qcs_eye[socket, iod, key[0], key[1], key[2]] = temp_qcs[key] 
        
        # Get QCA eye   
        qca_key, qca_start= detect_qca_eye_start(line)
        if qca_start:
            qca_eye_start[qca_key] = qca_start
        elif qca_key in qca_eye_start:
            qca_eye_start[qca_key] = qca_start
        temp = detect_qca_rank(line)
        #if temp>0:
        if (temp!=-1 ):
            rank=temp
        # Get QCA eye value
        temp_qca= process_qca_eye(previous_line[2], previous_line[1], previous_line[0], line, qca_eye_start, rank)
        if temp_qca:
            for key in temp_qca:
                qca_eye[socket, iod, key[0], key[1], key[2], key[3]] = temp_qca[key]    

        #Get Read Scan Eye
        key, read_start= detect_read_eye_even_start(line)
        if read_start:
            read_scan_start[key] = read_start
        elif key:
            if (key[0], key[1], 0) in read_scan_start:
                read_scan_start[key[0], key[1], 0] = read_start
            if (key[0], key[1], 1) in read_scan_start:
                read_scan_start[key[0], key[1], 1] = read_start                
        #Get Read eye
        #delay base 
        #match = process_scaneye(line, read_scan_start, 'base')
        #if match:
            #delay_base = match
        #get x-axis data
        #match = process_scaneye(previous_line[0], line, read_scan_start, 'delay')
        #if match:
        #    _delay = match
        #get y-axis data
        temp_read_eye = process_scaneye(previous_line[1], previous_line[0], line, read_scan_start, 'vref')

        if temp_read_eye:
            for key in temp_read_eye:
                read_eye_scan[socket, iod, key[0], key[1], key[2], key[3]]=temp_read_eye[key]

        #Get Upper & Lower Eye base
        _status, _lower, _upper = get_eye_base(line)
        if _status:
            upperbase = _upper
            lowerbase = _lower
        # Get Read even eye   
        read_key, read_even_start= detect_read_eye_even_start(line)
        if read_even_start:
            read_eye_even_start[read_key] = read_even_start
        elif read_key in read_eye_even_start:
            read_eye_even_start[read_key] = read_even_start
        # Get Read even eye value
        match_eye = process_eye(previous_line[2], previous_line[1], previous_line[0], line, read_eye_even_start, 'read', upperbase, lowerbase)
        if match_eye:
            for key in match_eye:
                new_key = (socket, iod, key[0], key[1], key[2], key[3])
                if new_key in read_eye_even:
                    adjusted_offset = [[x + 0, y] for x, y in match_eye[key]]
                    read_eye_even[socket, iod, key[0], key[1], key[2], key[3]].extend(adjusted_offset)
                else:
                    #MR40 = 0 
                    adjusted_offset = [[x + 128 if x < 32 else x, y] for x, y in match_eye[key]]
                    read_eye_even[socket, iod, key[0], key[1], key[2], key[3]] = adjusted_offset
        # Get Read odd eye   
        read_key, read_odd_start= detect_read_eye_odd_start(line)
        if read_odd_start:
            read_eye_odd_start[read_key] = read_odd_start
        elif read_key in read_eye_odd_start:
            read_eye_odd_start[read_key] = read_odd_start
        # Get Read even eye value
        match_eye = process_eye(previous_line[2], previous_line[1], previous_line[0], line, read_eye_odd_start, 'read', upperbase, lowerbase)
        if match_eye:
            for key in match_eye:
                new_key = (socket, iod, key[0], key[1], key[2], key[3])
                if new_key in read_eye_odd:
                    adjusted_offset = [[x + 0, y] for x, y in match_eye[key]]
                    read_eye_odd[socket, iod, key[0], key[1], key[2], key[3]].extend(adjusted_offset)
                else:
                    #MR40 = 0
                    adjusted_offset = [[x + 128 if x < 32 else x, y] for x, y in match_eye[key]]
                    read_eye_odd[socket, iod, key[0], key[1], key[2], key[3]] = adjusted_offset
        # Get Write eye   
        write_key, write_start= detect_write_eye_start(line)
        if write_start:
            write_eye_start[write_key] = write_start
        elif write_key in write_eye_start:
            write_eye_start[write_key] = write_start
        # Get Read even eye value
        match_eye = process_eye(previous_line[2], previous_line[1], previous_line[0], line, write_eye_start, 'write', 0, 0)
        if match_eye:
            for key in match_eye:
                write_eye[socket, iod, key[0], key[1], key[2], key[3]] = match_eye[key]


        # Get DCS value
        for key, value in process_dcs_value(previous_line[0], line):
            dcs_vref[socket, iod, key[0], key[1], key[2]] = value[0]
            dcs_coarse_delay[socket, iod, key[0], key[1], key[2]] = value[1]
            dcs_fine_delay[socket, iod, key[0], key[1], key[2]] = value[2]
            dcs_gain[socket, iod, key[0], key[1], key[2]] = value[3]
            dcs_tap1[socket, iod, key[0], key[1], key[2]] = value[4]
            dcs_tap2[socket, iod, key[0], key[1], key[2]] = value[5]
            dcs_tap3[socket, iod, key[0], key[1], key[2]] = value[6]
            dcs_tap4[socket, iod, key[0], key[1], key[2]] = value[7]


        # Get DCA delay
        for key, value in process_dca_value(previous_line[0], line):
            if key[2]=='CA0':
                dca=0
            elif key[2]=='CA1':
                dca=1
            elif key[2]=='CA2':
                dca=2
            elif key[2]=='CA3':
                dca=3
            elif key[2]=='CA4':
                dca=4
            elif key[2]=='CA5':
                dca=5
            elif key[2]=='CA6':
                dca=6
            elif key[2]=='PAR':
                dca=7
            
            dca_vref[socket, iod, key[0], key[1], dca] = value[0]
            dca_coarse_delay[socket, iod, key[0], key[1], dca] = value[1]
            dca_fine_delay[socket, iod, key[0], key[1], dca] = value[2]
            dca_gain[socket, iod, key[0], key[1], dca] = value[3]
            dca_tap1[socket, iod, key[0], key[1], dca] = signed_32bit(value[4], 8, 'dca_tap')
            dca_tap2[socket, iod, key[0], key[1], dca] = signed_32bit(value[5], 8, 'dca_tap')
            dca_tap3[socket, iod, key[0], key[1], dca] = signed_32bit(value[6], 8, 'dca_tap')
            dca_tap4[socket, iod, key[0], key[1], dca] = signed_32bit(value[7], 8, 'dca_tap')
            dca_tap5[socket, iod, key[0], key[1], dca] = signed_32bit(value[8], 8, 'dca_tap')
            dca_tap6[socket, iod, key[0], key[1], dca] = signed_32bit(value[9], 8, 'dca_tap')
        
        # Get QCS delay
        for key, value in process_qcs_line(previous_line[1], previous_line[0], line):
            qcs_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get QCS vref
        for key, value in process_qcs_vref(previous_line[1], previous_line[0], line):
            #workaround for vref value up+lowbase/2 => + 191
            #value = value + 191
            qcs_vref[socket, iod, key[0], key[1], key[2], key[3]] = value

        # Get QCA value
        for key, value in process_qca_line(previous_line[1], previous_line[0], line):
            qca_delay[socket, iod, key[0], key[1], key[2], key[3]] = value  
        # Get QCA Vref value
        for key, value in process_qcavref_line(previous_line[1], previous_line[0], line):
            qca_vref[socket, iod, key[0], key[1], key[2], key[3]] = value            
        # Get WL coarse value
        for key, value in process_wlcoarse_line(previous_line[1], previous_line[0], line):
            wlcoarse_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get WL fine value
        for key, value in process_wlfine_line(previous_line[1], previous_line[0], line):
            wlfine_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get WL MR3 value
        for key, value in process_wlmr3_line(previous_line[1], previous_line[0], line):
            wlmr3_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get WL MR7 value
        for key, value in process_wlmr7_line(previous_line[1], previous_line[0], line):
            wlmr7_value[socket, iod, key[0], key[1], key[2], key[3]] = value
       
        # Get RxEN Coarse value
        for key, value in process_rxen_coarse_line(previous_line[1], previous_line[0], line):
            rxen_coarse_value[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get RxEN Fine value
        for key, value in process_rxen_fine_line(previous_line[1], previous_line[0], line):
            rxen_fine_value[socket, iod, key[0], key[1], key[2], key[3]] = value
            
        # Get Read Even delay
        for key, value in process_read_even_delay(previous_line, line):
            readeven_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Read Odd delay
        for key, value in process_read_odd_delay(previous_line, line):
            readodd_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Read Vref Rank0
        for key, value in process_read_vref_r0(previous_line, line):
            read_vref[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Read Vref Rank1
        for key, value in process_read_vref_r1(previous_line, line):
            read_vref[socket, iod, key[0], key[1], key[2], key[3]] = value

        # Get Read Even delay for 8000 hwa
        for key, value in process_read_even_delay_hwa(line):
            readeven_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
    
        # Get Read odd delay for 8000 hwa
        for key, value in process_read_odd_delay_hwa(line):
            readodd_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Read vref rank0 for 8000 hwa
        for key, value in process_read_vref_rk0_hwa(line):
            read_vref[socket, iod, key[0], key[1], key[2], key[3]] = value
            
        # Get Read vref rank1 for 8000 hwa
        for key, value in process_read_vref_rk1_hwa(line):
            read_vref[socket, iod, key[0], key[1], key[2], key[3]] = value
            #print(f"read hwa vref {key}: {value}")
                        
        # Get Write Nibble Delay
        for key, value in process_write_nb_delay(previous_line, line):
            write_nb_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Write Coarse Delay
        for key, value in process_write_coarse_delay(previous_line, line):
            write_coarse_delay[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Write Fine Delay
        for key, value in process_write_fine_delay(previous_line, line):
            write_fine_delay[socket, iod, key[0], key[1], key[2], key[3]] = value             
        # Get Write Vref
        for key, value in process_write_vref(previous_line, line):
            write_vref[socket, iod, key[0], key[1], key[2], key[3]] = value
        # Get Write DFE
        for key, value in process_write_dfe(previous_line, line):
            #print(f"key {key}: {value}")
            #value = signed_32bit((value&0x7f), 7, 'write_dfe')
            if key[3]==1:
                write_dfe_tap1[socket, iod, key[0], key[1], key[2], key[4]] = value  
            elif key[3]==2:
                write_dfe_tap2[socket, iod, key[0], key[1], key[2], key[4]] = value  
            elif key[3]==3:
                write_dfe_tap3[socket, iod, key[0], key[1], key[2], key[4]] = value  
            elif key[3]==4:            
                write_dfe_tap4[socket, iod, key[0], key[1], key[2], key[4]] = value              


        #Get oneui value
        for key, value in process_oneui(previous_line, line):          
            oneui[socket, iod, key[0], key[1], key[2]] = value
        
        #Get MRL value
        for key, value in process_mrl(previous_line, line):
            mrl[socket, iod, key[0], key[1], key[2]] = value

        
        # Get MR register
        for key, value in process_mr_reg(previous_line, line):
            mr_reg[socket, iod, key[0], key[1], key[2], key[3], key[4]] = value


        previous_line[7] = previous_line[6]        
        previous_line[6] = previous_line[5]
        previous_line[5] = previous_line[4]
        previous_line[4] = previous_line[3]
        previous_line[3] = previous_line[2]
        previous_line[2] = previous_line[1]
        previous_line[1] = previous_line[0]
        previous_line[0] = line    

    return (
            dcs_coarse_delay,
            dcs_fine_delay,
            dcs_vref,
            dcs_gain,
            dcs_tap1,
            dcs_tap2,
            dcs_tap3,
            dcs_tap4,
            dca_coarse_delay,
            dca_fine_delay,
            dca_vref,
            dca_gain,
            dca_tap1,
            dca_tap2,
            dca_tap3,
            dca_tap4,
            dca_tap5,
            dca_tap6,    
            qcs_delay,
            qcs_vref,
            qca_delay,
            qca_vref, 
            wlcoarse_value, 
            wlfine_value, 
            wlmr3_value, 
            wlmr7_value, 
            rxen_coarse_value, 
            rxen_fine_value, 
            dcs_eye,
            qcs_eye,
            qca_eye,
            read_eye_scan,
            read_eye_even,
            read_eye_odd,
            write_eye,
            readeven_delay, 
            readodd_delay, 
            read_vref,
            write_nb_delay,
            write_coarse_delay,
            write_fine_delay,
            write_vref,
            write_dfe_tap1,
            write_dfe_tap2,
            write_dfe_tap3,
            write_dfe_tap4,
            oneui,
            mrl,
            mr_reg)

def process_data(data, mode):
    result = []
    for key, value in data.items():
        if mode=='dcs':
            soc, iod, channel, subchannel, rank = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "value/delay": value
            }
        elif mode=='dca':
            soc, iod, channel, subchannel, dca = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "dev/pin": dca,
                "value/delay": value
            }
        elif mode=='dcs_eye':          
            soc, iod, channel, subchannel, rank = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "value/delay": value
            }
        elif mode=='qcs_eye':          
            soc, iod, channel, subchannel, rank = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "value/delay": value
            }            
        elif mode=='qca_eye':
            soc, iod, channel, subchannel, rank, dev = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "dev/pin": dev,
                "value/delay": value
            }            
        elif mode=='oneui':
            soc, iod, channel, subchannel, nb = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "dev/pin": nb,
                "value/delay": value
            }            
        elif mode=='mrl':
            soc, iod, channel, subchannel, rank = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "value/delay": value
            } 
            
        elif mode=='mr_reg':
            soc, iod, channel, subchannel, rank, mr, dev = key
            entry = {
                "Param": f"MR_{mr}", 
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "dev/pin": dev,
                "value/delay": value
            }
        else:
            soc, iod, channel, subchannel, rank, dev = key
            entry = {
                "Socket": soc,
                "IOD": iod,  
                "channel": channel,
                "subchannel(phy)": subchannel,
                "rank": rank,
                "dev/pin": dev,
                "value/delay": value
            }
        result.append(entry)
    return result

def process_eyedata(data, mode):
    result = []
    for key, value in data.items():
        for delay, vref in data[key]:
            if mode=='qcs' or mode=='dcs':
                soc, iod, channel, subchannel, rank = key
                entry = {
                    "Socket": soc,
                    "IOD": iod,  
                    "channel": channel,
                    "subchannel(phy)": subchannel,
                    "rank": rank,
                    "value/delay": delay,
                    "vref": vref
                }
            elif mode=='qca':
                soc, iod, channel, subchannel, rank, dev = key
                entry = {
                    "Socket": soc,
                    "IOD": iod,  
                    "channel": channel,
                    "subchannel(phy)": subchannel,
                    "rank": rank,
                    "dev/pin": dev,
                    "value/delay": delay,
                    "vref": vref
                }
            else:
                soc, iod, channel, subchannel, rank, bit = key
                entry = {
                    "Socket": soc,
                    "IOD": iod,  
                    "channel": channel,
                    "subchannel(phy)": subchannel,
                    "rank": rank,
                    "dev/pin": bit,
                    "value/delay": delay,
                    "vref": vref
                }
                
            result.append(entry)
    return result



def calculation(
    dcs_fine,
    dcs_coarse,
    dca_fine,
    dca_coarse,
    qcs_delay,
    qca_delay,
    wlfine_value,
    wlcoarse_value,
    oneui,
    rxen_coarse_value,
    rxen_fine_value,
    readeven_delay,
    readodd_delay,
    write_nb_delay,
    write_coarse_delay,
    write_fine_delay,
    wlmr3_value,
    dcs_eye,
    qcs_eye,
    qca_eye,
    read_eye_scan,
    read_eye_even,
    read_eye_odd,
    write_eye
):
    missing_item=""
    # DCS
    dcs_result = {}
    try:
        for key, value in dcs_coarse.items():
            soc, iod, ch, sub, cs = key
            ##TxCsCoarseDly * 64 + stdqs_mdqs_dqsuTx[tc]_TxClkGenPiCode
            dcs_result[key] = (value * 64) + dcs_fine[key]
    except:
        print("DCS not calculated")
    # DCA
    dca_result = {}
    try:
        for key, value in dca_coarse.items():
            soc, iod, ch, sub, ca = key
            ##TxCaCoarseDly * 64 + stdqs_mdqs_dqtx[ul][0-3]_TxClkGenPiCode
            dca_result[key] = (value * 64) + dca_fine[key]
    except:
        print("DCA not calculated")
        
    #qca centering
    qca_result = {}
    try:
        for key, value in qca_delay.items():
            soc, iod, ch, sub, r, db = key
            if key in qcs_delay:
                onetck_qcsdelay = qcs_delay[key] & 0x40
                if onetck_qcsdelay != 0:
                    #qca_result[key] = value - 64
                    qca_result[key] = value
                else:
                    qca_result[key] = value + 64                 
                #print(f" onetck qcs of {key} is {onetck_qcsdelay}, {value}")                    
            else:
                missing_item+=f"<br>missing qcs delay {key}<br>"
    except:
        print("qca not calculated")  
        
    # WL
    wl_result = {}
    try:
        for key, value in wlcoarse_value.items():
            soc, iod, ch, sub, r, db = key
            #print(f"key {key}")
            ##DqsCoarseDly * 64 + stdqs_mdqs_dqs[ul]Txt_TxClkGenPiCode
            if (key in wlfine_value) and (key in wlmr3_value):
                wl_result[key] = (value * 128) + wlfine_value[key] + (wlmr3_value[key] * 128)   
                #print(f"value {value}")                
            else:
                missing_item+=f"<br>missing WL fine {key}<br>"
    except:
        print("WL not calculated")    
    # RxEN
    rxen_result = {}
    try:
        for key, value in rxen_coarse_value.items():
            soc, iod, ch, sub, r, db = key
            # rxen_result[key] = (rxen_coarse_value* 128) + rxen_fine_value[key]*(128/(2*OneUI[key]))
            #oneui[socket, iod, key[0], key[1], key[2]]
            # process oneui key to be in rxen calculation
            new_key = (soc, iod, ch, sub, db)
            if new_key not in oneui:
                oneui_newkey = 1
            else:
                #oneui_newkey = int(np.round(128 / (2 * oneui[new_key])))
                oneui_newkey = (128 / (2 * oneui[new_key]))
            #print(f" oneui is {oneui_newkey}, with {oneui[new_key]}")
            if key in rxen_fine_value:
                rxen_result[key] = (value * 128) + int(rxen_fine_value[key] * oneui_newkey)
                #print(f" rxen is {rxen_result[key]}")
            else:
                missing_item+=f"<br>missing RxEN fine {key}<br>"
    except:
        print("RxEN not calculated")
    #read even    
    readeven_result = {}
    try:
        for key, value in readeven_delay.items():
            soc, iod, ch, sub, r, dq = key
            if value >= 64:
                readeven_result[key]= 128-value
            else:
                readeven_result[key]= value
    except:
        print("Read Even not calculated")
    #read odd 
    readodd_result = {}
    try:
        for key, value in readodd_delay.items():
            soc, iod, ch, sub, r, dq = key
            if value >= 64:
                readodd_result[key]= 128-value
            else:
                readodd_result[key]= value
    except:
        print("Read Odd not calculated")
    #write delay
    write_result = {}
    try:
        for key, value in write_coarse_delay.items():
            soc, iod, ch, sub, r, dq = key
            n= int(dq/4)
            nb_key = (soc, iod, ch, sub, r, n)  #write_nb_delay
            ##(DqCoarseDly + CoarseDly) * 64 + stdqs_mdqs_dqtx[ul][0-3]_TxClkGenPiCode
            if nb_key in wlcoarse_value:
                if nb_key in wlmr3_value:                                        
                    if key in write_fine_delay:
                        if nb_key in write_nb_delay:
                            write_result[key] = (
                                wlcoarse_value[nb_key] * 128) + (value + write_nb_delay[nb_key] - 1
                            ) * 64 + write_fine_delay[key] + (wlmr3_value[nb_key] * 128) 
                            #print(f"key is {key}, nvkey is {nb_key} wrte coarse is {value}, wlcoarse {wlcoarse_value[nb_key]}, write_nb {write_nb_delay[nb_key]}")
                        else:
                            missing_item+=f"<br>missing TxDqNibbleDelay {nb_key}<br>"
                    else:
                        missing_item+=f"<br>missing Write fine {key}<br>"
                else:
                    missing_item+=f"<br>missing WL MR3 {nb_key}<br>"
            else:
                missing_item+=f"<br>missing WL coarse delay {nb_key}<br>"
    except:
        print("Write not calculated")

    dcs_eye_width = {}
    dcs_eye_height = {}
    qcs_eye_width = {}
    qcs_eye_height = {}
    qca_eye_width = {}
    qca_eye_height = {}
    read_scan_width = {}
    read_scan_height = {}
    read_even_width = {}
    read_even_height = {}
    read_odd_width = {}
    read_odd_height = {}
    write_eye_width = {}
    write_eye_height = {}
    try:
        if dcs_eye:
           dcs_eye_width, dcs_eye_height=get_width_height(dcs_eye)
        if qcs_eye:
           qcs_eye_width, qcs_eye_height=get_width_height(qcs_eye)
        if qca_eye:
           qca_eye_width, qca_eye_height=get_width_height(qca_eye)        
        if read_eye_scan:
           read_scan_width, read_scan_height=get_width_height(read_eye_scan)
        if read_eye_even:
           read_even_width, read_even_height=get_width_height(read_eye_even)
        if read_eye_odd:
           read_odd_width, read_odd_height=get_width_height(read_eye_odd)
        if write_eye:
           write_eye_width, write_eye_height=get_width_height(write_eye)
    except:
        print("Eye width or eye height not calculated")
    
    return (
        dcs_result,
        dca_result,
        qca_result,
        wl_result, 
        rxen_result,
        readeven_result,
        readodd_result,
        write_result,
        dcs_eye_width,
        dcs_eye_height,
        qcs_eye_width,
        qcs_eye_height,
        qca_eye_width,
        qca_eye_height,
        read_scan_width,
        read_scan_height,
        read_even_width,
        read_even_height,
        read_odd_width,
        read_odd_height,
        write_eye_width,
        write_eye_height,
        missing_item
    )


def get_width_height(eye):
        width = {}
        height = {}
        for key, coords in eye.items():
            x_to_ys = defaultdict(list)
            for x, y in coords:
                x_to_ys[x].append(y)
            # Height: max vertical range for fixed x
            max_height = max(max(ys) - min(ys) for ys in x_to_ys.values())
            height[key] = max_height
            # Width: max x distance where y-ranges overlap
            xs = sorted(x_to_ys.keys())
            max_width = 0
            for i in range(len(xs)):
                x1 = xs[i]
                y1_min, y1_max = min(x_to_ys[x1]), max(x_to_ys[x1])
                for j in range(i + 1, len(xs)):
                    x2 = xs[j]
                    y2_min, y2_max = min(x_to_ys[x2]), max(x_to_ys[x2])
                    # Check if y-ranges overlap
                    if max(y1_min, y2_min) <= min(y1_max, y2_max):
                        max_width = max(max_width, abs(x2 - x1))
            width[key] = max_width
        return width, height



def calculate_standard_deviation_and_range(analysis_csv):
    #initialize warning result
    warning_result=""
    
    # Step 1: Read the CSV data
    df_analysis = pd.read_csv(analysis_csv)
    # Ensure that the 'trained_value' column is included in the columns of interest

    # Step 2: Identify the columns related to 'trained_value' and runX (dynamically find columns that start with 'run')
    columns_of_interest = ["value/delay"] + [col for col in df_analysis.columns if col.startswith("run")]

    # Step 3: Iterate through each row and calculate the standard deviation and range
    df_analysis["standard_deviation"] = df_analysis[columns_of_interest].std(axis=1, ddof=0)
    df_analysis["range"] = df_analysis[columns_of_interest].max(axis=1) - df_analysis[columns_of_interest].min(axis=1)

    # Step 4 Add pass/fail if range >7
    df_analysis["Pass_Fail"] = df_analysis["range"].apply(lambda x: "Warning" if x > 7 else "Pass")

    # Step 5 Check if 'Param' is 'MRL' and 'trained_value' is not between 14 and 17 for all run columns
    # df_analysis["Pass_Fail"] = df_analysis.apply(
        # lambda row: "Fail" if (row["Param"] == "MRL" and not (14 <= row["trained_value"] <= 17)) else row["Pass_Fail"],
        # axis=1,
    # )
    # run_columns = [col for col in df_analysis.columns if col.startswith("run")]
    # df_analysis["Pass_Fail"] = df_analysis.apply(
        # lambda row: "Fail" if (row["Param"] == "MRL" and not all(14 <= row[col] <= 17 for col in run_columns)) else row["Pass_Fail"],
        # axis=1,
    # )

    # Step 6: Copy 'byte' value to new column 'nibble' for 'WL' or 'RXEN' params
    #df_analysis["nibble"] = df_analysis.apply(
    #    lambda row: row["nibble"] if row["Param"] in ["WL", "RXEN"] else "", axis=1
    #)
    # Step 7: Write the updated DataFrame back to the CSV
    df_analysis.to_csv(analysis_csv, index=False)

    # Step 8 Print out/return warning/all pass
    warning = df_analysis[df_analysis["Pass_Fail"] == "Warning"]

    # Step 9: Create a new DataFrame with the max of each range column for each param
    max_range_per_param = df_analysis.groupby("Param")["range"].max().reset_index()
    max_range_per_param.columns = ["Param", "Max Range"]

    # Print the new DataFrame
    warning_result += "Max range for each param:<br>"
    warning_result += max_range_per_param.to_string(index=False).replace("\n", "<br>")
    warning_result += "<br>"
    print("Max range for each param:")
    print(max_range_per_param)
    if not warning.empty:
        print("Warning rows:")
        print(warning)
        #warning_result += "Warning rows:<br>"
        #warning_result += warning.to_string(index=False).replace("\n", "<br>")
        #warning_result += "<br>"
        return warning, warning_result
    else:
        print("All Pass")
        warning_result+="<br>All Pass and no warning<br>"
        return None, warning_result


def process_decodedlog(
    filename, outputfile, run, inputbase, inputhost, inputbios, analysis_csv, mdteye_path, filename2=""
):
    missing_printing=""
    (
        dcs_coarse_delay,
        dcs_fine_delay,
        dcs_vref,
        dcs_gain,
        dcs_tap1,
        dcs_tap2,
        dcs_tap3,
        dcs_tap4,
        dca_coarse_delay,
        dca_fine_delay,
        dca_vref,
        dca_gain,
        dca_tap1,
        dca_tap2,
        dca_tap3,
        dca_tap4,
        dca_tap5,
        dca_tap6,    
        qcs_delay,
        qcs_vref,
        qca_delay,
        qca_vref, 
        wlcoarse_value, 
        wlfine_value, 
        wlmr3_value, 
        wlmr7_value, 
        rxen_coarse_value, 
        rxen_fine_value, 
        dcs_eye,
        qcs_eye,
        qca_eye,
        read_eye_scan,
        read_eye_even,
        read_eye_odd,
        write_eye,        
        readeven_delay, 
        readodd_delay, 
        read_vref,
        write_nb_delay,
        write_coarse_delay,
        write_fine_delay,
        write_vref,
        write_dfe_tap1,
        write_dfe_tap2,
        write_dfe_tap3,
        write_dfe_tap4,
        oneui,
        mrl,        
        mr_reg
    ) = detect_decoded_log(filename, filename2)
   
    (
        dcs_result,
        dca_result,
        qca_result,        
        wl_result, 
        rxen_result,
        readeven_result,
        readodd_result,
        write_result,
        dcs_eye_width,
        dcs_eye_height,
        qcs_eye_width,
        qcs_eye_height,
        qca_eye_width,
        qca_eye_height,
        read_scan_width,
        read_scan_height,
        read_even_width,
        read_even_height,
        read_odd_width,
        read_odd_height,
        write_eye_width,
        write_eye_height,        
        missing_item
    ) = calculation(
        dcs_fine_delay,
        dcs_coarse_delay,
        dca_fine_delay,
        dca_coarse_delay,
        qcs_delay,
        qca_delay,
        wlfine_value,
        wlcoarse_value,
        oneui,
        rxen_coarse_value, 
        rxen_fine_value,
        readeven_delay,
        readodd_delay,
        write_nb_delay,
        write_coarse_delay,
        write_fine_delay,
        wlmr3_value,
        dcs_eye,
        qcs_eye,
        qca_eye,
        read_eye_scan,
        read_eye_even,
        read_eye_odd,
        write_eye
    )

    try:
        file = os.path.basename(filename)
        bn = file.split('.')[0]
        dcs_html = os.path.join(mdteye_path, f'{bn}_dcs.html')
        qcs_html = os.path.join(mdteye_path, f'{bn}_qcs.html')
        qca_html = os.path.join(mdteye_path, f'{bn}_qca.html')
        readscan_html = os.path.join(mdteye_path, f'{bn}_readscan.html')
        readeven_html = os.path.join(mdteye_path, f'{bn}_readeven.html')
        readodd_html = os.path.join(mdteye_path, f'{bn}_readodd.html')    
        write_html = os.path.join(mdteye_path, f'{bn}_write.html')

        if dcs_eye:
            html_eye_plot(dcs_html, dcs_eye, 'dcs', dcs_result, dcs_vref)
        if qcs_eye:
            html_eye_plot(qcs_html, qcs_eye, 'qcs', qcs_delay, qcs_vref)
        if qca_eye:
            html_eye_plot(qca_html, qca_eye, 'qca', qca_result, qca_vref)            
        if read_eye_scan:
            html_eye_plot(readscan_html, read_eye_scan, 'readscan', readeven_delay, read_vref)
        if read_eye_even:
            html_eye_plot(readeven_html, read_eye_even, 'readeven', readeven_delay, read_vref)
        if read_eye_odd:
            html_eye_plot(readodd_html, read_eye_odd, 'readodd', readodd_delay, read_vref)   
        if write_eye:
            write_eye_center ={}
            for key, value in write_coarse_delay.items():
                soc, iod, ch, sub, r, dq = key
                n= int(dq/4)
                nb_key = (soc, iod, ch, sub, r, n)  #write_nb_delay
                ##(DqCoarseDly + CoarseDly) * 64 + stdqs_mdqs_dqtx[ul][0-3]_TxClkGenPiCode
                if key in write_fine_delay:
                    if nb_key in write_nb_delay:
                        write_eye_center[key] = (
                            value + 0
                        ) * 64 + write_fine_delay[key]
                    else:
                        missing_item+=f"<br>missing TxDqNibbleDelay {key}<br>"
                else:
                    missing_item+=f"<br>missing Write fine {key}<br>"             

            html_eye_plot(write_html, write_eye, 'write', write_eye_center, write_vref)       
    except:
        print(f"Cannot produce eye for {file}")

    wl_rxen_ordered_result=""
    try:
        if wl_result and rxen_result:
            result = compare_byte_sequence_by_group(wl_result, rxen_result)
            if result:
                wl_rxen_ordered_result = f"<br>{filename}:<br>(soc,iod,ch,sub,rank)"
                for key, value in result.items(): 
                    wl_rxen_ordered_result += f"<br>{key}:<br>{value}"
    except:
        print("cannot compare order of WL vs RxEN")
        
    df_dcsdelay = process_data(dcs_result, 'dcs')
    df_dcsdelay = pd.DataFrame(df_dcsdelay)
    df_dcsdelay["Param"] = "DCS_Delay"
    df_dcsvref = process_data(dcs_vref, 'dcs')
    df_dcsvref = pd.DataFrame(df_dcsvref)
    df_dcsvref["Param"] = "DCS_Vref"
    df_dcsgain = process_data(dcs_gain, 'dcs')
    df_dcsgain = pd.DataFrame(df_dcsgain)
    df_dcsgain["Param"] = "DCS_Gain"
    df_dcstap1 = process_data(dcs_tap1, 'dcs')
    df_dcstap1 = pd.DataFrame(df_dcstap1)
    df_dcstap1["Param"] = "DCS_Tap1"
    df_dcstap2 = process_data(dcs_tap2, 'dcs')
    df_dcstap2 = pd.DataFrame(df_dcstap2)
    df_dcstap2["Param"] = "DCS_Tap2"
    df_dcstap3 = process_data(dcs_tap3, 'dcs')
    df_dcstap3 = pd.DataFrame(df_dcstap3)
    df_dcstap3["Param"] = "DCS_Tap3"
    df_dcstap4 = process_data(dcs_tap4, 'dcs')
    df_dcstap4 = pd.DataFrame(df_dcstap4)
    df_dcstap4["Param"] = "DCS_Tap4"

    df_dcadelay = process_data(dca_result, 'dca')
    df_dcadelay = pd.DataFrame(df_dcadelay)
    df_dcadelay["Param"] = "DCA_Delay"
    df_dcavref = process_data(dca_vref, 'dca')
    df_dcavref = pd.DataFrame(df_dcavref)
    df_dcavref["Param"] = "DCA_Vref"
    df_dcagain = process_data(dca_gain, 'dca')
    df_dcagain = pd.DataFrame(df_dcagain)
    df_dcagain["Param"] = "DCA_Gain"
    df_dcatap1 = process_data(dca_tap1, 'dca')
    df_dcatap1 = pd.DataFrame(df_dcatap1)
    df_dcatap1["Param"] = "DCA_Tap1"
    df_dcatap2 = process_data(dca_tap2, 'dca')
    df_dcatap2 = pd.DataFrame(df_dcatap2)
    df_dcatap2["Param"] = "DCA_Tap2"
    df_dcatap3 = process_data(dca_tap3, 'dca')
    df_dcatap3 = pd.DataFrame(df_dcatap3)
    df_dcatap3["Param"] = "DCA_Tap3"
    df_dcatap4 = process_data(dca_tap4, 'dca')
    df_dcatap4 = pd.DataFrame(df_dcatap4)
    df_dcatap4["Param"] = "DCA_Tap4"
    df_dcatap5 = process_data(dca_tap5, 'dca')
    df_dcatap5 = pd.DataFrame(df_dcatap4)
    df_dcatap5["Param"] = "DCA_Tap5"
    df_dcatap6 = process_data(dca_tap6, 'dca')
    df_dcatap6 = pd.DataFrame(df_dcatap6)
    df_dcatap6["Param"] = "DCA_Tap6"
    
    df_qcs = process_data(qcs_delay, 'qcs')
    df_qcs = pd.DataFrame(df_qcs)
    df_qcs["Param"] = "QAQCS_Delay"

    df_qcsvref = process_data(qcs_vref, 'qcs')
    df_qcsvref = pd.DataFrame(df_qcsvref)
    df_qcsvref["Param"] = "QCS_Vref"

    df_qca = process_data(qca_delay, 'qca')
    df_qca = pd.DataFrame(df_qca)
    df_qca["Param"] = "QAQCA_Delay"

    df_qcavref = process_data(qca_vref, 'qca')
    df_qcavref = pd.DataFrame(df_qcavref)
    df_qcavref["Param"] = "QCA_Vref"

    df_wl = process_data(wl_result, 'wl')
    df_wl = pd.DataFrame(df_wl)
    df_wl["Param"] = "WL_Value"

    df_wlmr3 = process_data(wlmr3_value, 'wl')
    df_wlmr3 = pd.DataFrame(df_wlmr3)
    df_wlmr3["Param"] = "WL_MR3"

    df_wlmr7 = process_data(wlmr7_value, 'wl')
    df_wlmr7 = pd.DataFrame(df_wlmr7)
    df_wlmr7["Param"] = "WL_MR7"    

    df_rxen = process_data(rxen_result, 'rxen')
    df_rxen = pd.DataFrame(df_rxen)
    df_rxen["Param"] = "RxEN_Value"

    df_readeven = process_data(readeven_result, 'rxeven')
    df_readeven = pd.DataFrame(df_readeven)
    df_readeven["Param"] = "Read_Even"
    
    df_readodd = process_data(readodd_result, 'rxodd')
    df_readodd = pd.DataFrame(df_readodd)
    df_readodd["Param"] = "Read_Odd"    

    df_readvref = process_data(read_vref, 'readvref')
    df_readvref = pd.DataFrame(df_readvref)
    df_readvref["Param"] = "Read_Vref"

    df_wrdelay = process_data(write_result, 'write')
    df_wrdelay = pd.DataFrame(df_wrdelay)
    df_wrdelay["Param"] = "Write_Delay"     

    df_wrvref = process_data(write_vref, 'write')
    df_wrvref = pd.DataFrame(df_wrvref)
    df_wrvref["Param"] = "Write_Vref"        

    df_wrdfetap1 = process_data(write_dfe_tap1, 'write')
    df_wrdfetap1 = pd.DataFrame(df_wrdfetap1)
    df_wrdfetap1["Param"] = "Write_DFE_Tap1"  

    df_wrdfetap2 = process_data(write_dfe_tap2, 'write')
    df_wrdfetap2 = pd.DataFrame(df_wrdfetap2)
    df_wrdfetap2["Param"] = "Write_DFE_Tap2" 

    df_wrdfetap3 = process_data(write_dfe_tap3, 'write')
    df_wrdfetap3 = pd.DataFrame(df_wrdfetap3)
    df_wrdfetap3["Param"] = "Write_DFE_Tap3" 

    df_wrdfetap4 = process_data(write_dfe_tap4, 'write')
    df_wrdfetap4 = pd.DataFrame(df_wrdfetap4)
    df_wrdfetap4["Param"] = "Write_DFE_Tap4"     

    df_oneui = process_data(oneui, 'oneui')
    df_oneui = pd.DataFrame(df_oneui)
    df_oneui["Param"] = "OneUI"  

    df_mrl = process_data(mrl, 'mrl')
    df_mrl = pd.DataFrame(df_mrl)
    df_mrl["Param"] = "MRL" 

    df_mrreg = process_data(mr_reg, 'mr_reg')
    df_mrreg = pd.DataFrame(df_mrreg)

    df_dcs_width = process_data(dcs_eye_width, 'dcs_eye')
    df_dcs_width = pd.DataFrame(df_dcs_width)
    df_dcs_width["Param"] = "DCS Eye Width"      

    df_dcs_height = process_data(dcs_eye_height, 'dcs_eye')
    df_dcs_height = pd.DataFrame(df_dcs_height)
    df_dcs_height["Param"] = "DCS Eye Height"  

    df_qcs_width = process_data(qcs_eye_width, 'qcs_eye')
    df_qcs_width = pd.DataFrame(df_qcs_width)
    df_qcs_width["Param"] = "QCS Eye Width"      

    df_qcs_height = process_data(qcs_eye_height, 'qcs_eye')
    df_qcs_height = pd.DataFrame(df_qcs_height)
    df_qcs_height["Param"] = "QCS Eye Height"  

    df_qca_width = process_data(qca_eye_width, 'qca_eye')
    df_qca_width = pd.DataFrame(df_qca_width)
    df_qca_width["Param"] = "QCA Eye Width"      

    df_qca_height = process_data(qca_eye_height, 'qca_eye')
    df_qca_height = pd.DataFrame(df_qca_height)
    df_qca_height["Param"] = "QCA Eye Height"  

    df_rdscan_width = process_data(read_scan_width, 'eye')
    df_rdscan_width = pd.DataFrame(df_rdscan_width)
    df_rdscan_width["Param"] = "ReadScan Width"      

    df_rdscan_height = process_data(read_scan_height, 'eye')
    df_rdscan_height = pd.DataFrame(df_rdscan_height)
    df_rdscan_height["Param"] = "ReadScan Height"  

    df_rdeven_width = process_data(read_even_width, 'eye')
    df_rdeven_width = pd.DataFrame(df_rdeven_width)
    df_rdeven_width["Param"] = "ReadEven Width"

    df_rdeven_height = process_data(read_even_height, 'eye')
    df_rdeven_height = pd.DataFrame(df_rdeven_height)
    df_rdeven_height["Param"] = "ReadEven Height" 

    df_rdodd_width = process_data(read_odd_width, 'eye')
    df_rdodd_width = pd.DataFrame(df_rdodd_width)
    df_rdodd_width["Param"] = "ReadOdd Width"

    df_rdodd_height = process_data(read_odd_height, 'eye')
    df_rdodd_height = pd.DataFrame(df_rdodd_height)
    df_rdodd_height["Param"] = "ReadOdd Height" 

    df_write_width = process_data(write_eye_width, 'eye')
    df_write_width = pd.DataFrame(df_write_width)
    df_write_width["Param"] = "WriteEye Width"

    df_write_height = process_data(write_eye_height, 'eye')
    df_write_height = pd.DataFrame(df_write_height)
    df_write_height["Param"] = "WriteEye Height" 
    
    df_dcseye = process_eyedata(dcs_eye, 'dcs')
    df_dcseye = pd.DataFrame(df_dcseye)
    df_dcseye["Param"] = "DCS_eye"

    df_qcseye = process_eyedata(qcs_eye, 'qcs')
    df_qcseye = pd.DataFrame(df_qcseye)
    df_qcseye["Param"] = "QCS_eye"

    df_qcaeye = process_eyedata(qca_eye, 'qca')
    df_qcaeye = pd.DataFrame(df_qcaeye)
    df_qcaeye["Param"] = "QCA_eye"

    df_readeyescan = process_eyedata(read_eye_scan, 'read')
    df_readeyescan = pd.DataFrame(df_readeyescan)
    df_readeyescan["Param"] = "Read_Scan_eye"
    
    df_readeveneye = process_eyedata(read_eye_even, 'read')
    df_readeveneye = pd.DataFrame(df_readeveneye)
    df_readeveneye["Param"] = "Read_Even_eye"

    df_readoddeye = process_eyedata(read_eye_odd, 'read')
    df_readoddeye = pd.DataFrame(df_readoddeye)
    df_readoddeye["Param"] = "Read_Odd_eye"

    df_writeeye = process_eyedata(write_eye, 'write')
    df_writeeye = pd.DataFrame(df_writeeye)
    df_writeeye["Param"] = "Write_eye"

    df_dcsfinedelay = process_data(dcs_fine_delay, 'dcs')
    df_dcsfinedelay = pd.DataFrame(df_dcsfinedelay)
    df_dcsfinedelay["Param"] = "DCS_Fine_Delay"

    df_dcscoarsedelay = process_data(dcs_coarse_delay, 'dcs')
    df_dcscoarsedelay = pd.DataFrame(df_dcscoarsedelay)
    df_dcscoarsedelay["Param"] = "DCS_Coarse_Delay"

    df_dcafinedelay = process_data(dca_fine_delay, 'dca')
    df_dcafinedelay = pd.DataFrame(df_dcafinedelay)
    df_dcafinedelay["Param"] = "DCA_Fine_Delay"

    df_dcacoarsedelay = process_data(dca_coarse_delay, 'dca')
    df_dcacoarsedelay = pd.DataFrame(df_dcacoarsedelay)
    df_dcacoarsedelay["Param"] = "DCA_Coarse_Delay"

    df_wlfine = process_data(wlfine_value, 'wl')
    df_wlfine = pd.DataFrame(df_wlfine)
    df_wlfine["Param"] = "WL_Fine_Value"

    df_wlcoarse = process_data(wlcoarse_value, 'wl')
    df_wlcoarse = pd.DataFrame(df_wlcoarse)
    df_wlcoarse["Param"] = "WL_Coarse_Value"        

    df_rxen_fine = process_data(rxen_fine_value, 'rxen')
    df_rxen_fine = pd.DataFrame(df_rxen_fine)
    df_rxen_fine["Param"] = "RxEN_Fine_Value"

    df_rxen_coarse = process_data(rxen_coarse_value, 'rxen')
    df_rxen_coarse = pd.DataFrame(df_rxen_coarse)
    df_rxen_coarse["Param"] = "RxEN_Coarse_Value"

    df_readeven_raw = process_data(readeven_delay, 'rxeven')
    df_readeven_raw = pd.DataFrame(df_readeven_raw)
    df_readeven_raw["Param"] = "Read_Even_raw"

    df_readodd_raw = process_data(readodd_delay, 'rxodd')
    df_readodd_raw = pd.DataFrame(df_readodd_raw)
    df_readodd_raw["Param"] = "Read_Odd_raw"  

    df_wrcoarsedelay = process_data(write_coarse_delay, 'write')
    df_wrcoarsedelay = pd.DataFrame(df_wrcoarsedelay)
    df_wrcoarsedelay["Param"] = "Write_Coarse_Delay"     

    df_wrfinedelay = process_data(write_fine_delay, 'write')
    df_wrfinedelay = pd.DataFrame(df_wrfinedelay)
    df_wrfinedelay["Param"] = "Write_Fine_Delay"    

    df_wrnbdelay = process_data(write_nb_delay, 'wl')
    df_wrnbdelay = pd.DataFrame(df_wrnbdelay)
    df_wrnbdelay["Param"] = "Write_Nibble_Delay" 

    df = pd.concat(
        [
            df_dcsdelay,
            df_dcsvref,
            df_dcsgain,
            df_dcstap1,
            df_dcstap2,
            df_dcstap3,
            df_dcstap4,
            df_dcadelay,
            df_dcavref,
            df_dcagain,
            df_dcatap1,
            df_dcatap2,
            df_dcatap3,
            df_dcatap4,
            df_dcatap5,
            df_dcatap6,
            df_qcs,
            df_qcsvref,
            df_qca,
            df_qcavref,
            df_wl,
            df_wlmr3,
            df_wlmr7,
            df_rxen,
            df_readeven,
            df_readodd,
            df_readvref,
            df_wrdelay,
            df_wrvref,
            df_wrdfetap1,
            df_wrdfetap2,
            df_wrdfetap3,
            df_wrdfetap4,
            df_oneui,
            df_mrl,
            df_mrreg,
            df_dcseye,
            df_qcseye,
            df_qcaeye,
            df_readeyescan,
            df_readeveneye,
            df_readoddeye,
            df_writeeye,
            df_dcs_width,
            df_dcs_height,
            df_qcs_width,
            df_qcs_height,
            df_qca_width,
            df_qca_height,
            df_rdscan_width,
            df_rdscan_height,
            df_rdeven_width,
            df_rdeven_height,
            df_rdodd_width,
            df_rdodd_height,
            df_write_width,
            df_write_height,
            df_dcsfinedelay,
            df_dcscoarsedelay,
            df_dcafinedelay,
            df_dcacoarsedelay,
            df_wlfine,
            df_wlcoarse,
            df_rxen_fine,
            df_rxen_coarse,
            df_readeven_raw,
            df_readodd_raw,
            df_wrcoarsedelay,
            df_wrfinedelay,
            df_wrnbdelay            
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
        "Param",
        "Socket",
        "IOD",           
        "channel",
        "subchannel(phy)",
        "rank",
        "dev/pin",
        "value/delay",
        "run"
    ]
    missing = [col for col in ordered_columns if col not in df.columns]
    if missing:
        print(f"Missing columns before reordering: {missing}")
    else:

        df = df[ordered_columns]
    if os.path.exists(outputfile):
        df.to_csv(outputfile, mode="a", header=False, index=False)
    else:
        df.to_csv(outputfile, mode="w", header=True, index=False)    


    if analysis_csv:
        
        # Convert to Path object
        original_path = Path(analysis_csv)
        
        # Create the new filename with "_raw" before the suffix
        raw_csv = original_path.with_name(original_path.stem + "_raw" + original_path.suffix)

        #Columns sequence
        ordered_columns_analysis = [
            "Param",
            "Socket",
            "IOD",           
            "channel",
            "subchannel(phy)",
            "rank",
            "dev/pin",
            "value/delay"
        ]



        df_raw = pd.concat(
            [
                df_dcsfinedelay,
                df_dcscoarsedelay,
                df_dcafinedelay,
                df_dcacoarsedelay,
                df_wlfine,
                df_wlcoarse,
                df_rxen_fine,
                df_rxen_coarse,
                df_readeven_raw,
                df_readodd_raw,
                df_wrcoarsedelay,
                df_wrfinedelay,
                df_wrnbdelay,
                df_wlmr3
            ]
        ).reset_index(drop=True)
        df_raw = df_raw[ordered_columns_analysis]

        df_analysis = pd.concat(
            [
                df_dcsdelay,
                df_dcsvref,
                df_dcsgain,
                df_dcstap1,
                df_dcstap2,
                df_dcstap3,
                df_dcstap4,
                df_dcadelay,
                df_dcavref,
                df_dcagain,
                df_dcatap1,
                df_dcatap2,
                df_dcatap3,
                df_dcatap4,
                df_dcatap5,
                df_dcatap6,
                df_qcs,
                df_qcsvref,
                df_qca,
                df_qcavref,
                df_wl,
                df_wlmr3,
                df_wlmr7,
                df_rxen,
                df_readeven,
                df_readodd,
                df_readvref,
                df_wrdelay,
                df_wrvref,
                df_wrdfetap1,
                df_wrdfetap2,
                df_wrdfetap3,
                df_wrdfetap4,
                df_oneui,
                df_mrl,                
                df_mrreg,
                df_dcs_width,
                df_dcs_height,
                df_qcs_width,
                df_qcs_height,
                df_qca_width,
                df_qca_height,
                df_rdscan_width,
                df_rdscan_height,
                df_rdeven_width,
                df_rdeven_height,
                df_rdodd_width,
                df_rdodd_height,
                df_write_width,
                df_write_height
            ]
        ).reset_index(drop=True)
        df_analysis = df_analysis[ordered_columns_analysis]
        
        
        if run == 0:
            if Path(analysis_csv).exists() or Path(raw_csv).exists():
                print("Warning: overwriting existing analysis files for run 0")
            df_analysis.to_csv(analysis_csv, mode="w", header=True, index=False)
            df_raw.to_csv(raw_csv, mode="w", header=True, index=False)
        else:

            # Your unique identifying columns
            key_columns = ["Param", "Socket", "IOD", "channel", "subchannel(phy)", "rank", "dev/pin"]

            # Read existing analysis CSV
            df_analysis_existing = pd.read_csv(analysis_csv)

            # Create the new run column name
            run_column_name = f"run{run}"

            # Prepare a temp DataFrame with just keys + value
            df_update = df[key_columns + ["value/delay"]].copy()
            df_update = df_update.rename(columns={"value/delay": run_column_name})

            # Merge the new run values into the existing dataframe
            df_analysis_updated = pd.merge(
                df_analysis_existing,
                df_update,
                on=key_columns,
                how="left"
            )
            df_analysis_updated.to_csv(analysis_csv, mode="w", header=True, index=False)

            # Read existing analysis CSV
            df_raw_existing = pd.read_csv(raw_csv)

            # Create the new run column name
            run_column_name = f"run{run}"

            # Prepare a temp DataFrame with just keys + value
            df_rawupdate = df[key_columns + ["value/delay"]].copy()
            df_rawupdate = df_rawupdate.rename(columns={"value/delay": run_column_name})

            # Merge the new run values into the existing dataframe
            df_raw_updated = pd.merge(
                df_raw_existing,
                df_rawupdate,
                on=key_columns,
                how="left"
            )
            df_raw_updated.to_csv(raw_csv, mode="w", header=True, index=False)            

            # df_analysis = pd.read_csv(analysis_csv)
            # trained_value_column = df["value/delay"]
            # run_column_name = f"run{run}"
            # df_analysis[run_column_name] = trained_value_column
            # df_analysis.to_csv(analysis_csv, mode="w", header=True, index=False)
    if missing_item:
        missing_printing+=f"file combination that have missing printing: <br>"
        missing_printing+=f"            iod0:{filename}<br>"
        missing_printing+=f"            iod1:{filename2}<br>"
        missing_printing+=missing_item
    return wl_rxen_ordered_result, missing_printing

def grouping_files(filelist):
    # Initialize groups
    grouped_files = defaultdict(dict)
    # Group files based on common prefix (before iodX)
    for filename in filelist:
        match = re.match(r"(.*)_iod(\d)\.parsed\.log", filename)
        if match:
            base = match.group(1)
            iod = match.group(2)
            grouped_files[base][f'iod{iod}'] = filename
    return grouped_files

def log_to_csv(inputlog, jmp_output, analysis_output, mdteye_path):
    run = 0
    hostname = ""
    bios = ""
    ordered_result=""
    missing_print=""
    analysis_result=""
    merge= grouping_files(inputlog)
    if len(inputlog) >1:
        for path, iod_files in merge.items():
            iod0_file = iod_files.get("iod0")
            iod1_file = iod_files.get("iod1")
            if iod0_file:
                base = os.path.splitext(os.path.basename(iod0_file))[0]
            else:
                base = os.path.splitext(os.path.basename(iod1_file))[0]
            bios, hostname = get_bios_hostname(base)
            try:
                print(f"start log debug: {analysis_output}")
                ordering, missing=process_decodedlog(iod0_file, jmp_output, run, base, hostname, bios, analysis_output, mdteye_path, iod1_file)
                ordered_result+=ordering
                missing_print+=missing
            except:
                print(f"LOG: Fail to process file: {iod0_file} & {iod1_file}" ) 
            run = run + 1
        try:
            _, analysis_result= calculate_standard_deviation_and_range(analysis_output)
        except:
            print("fail to calculate std deviation")

    else:
        base = os.path.splitext(os.path.basename(inputlog[0]))[0]
        bios, hostname = get_bios_hostname(base)
        ordering, missing=process_decodedlog(inputlog[0], jmp_output, run, base, hostname, bios, mdteye_path, "")
        ordered_result+=ordering
        missing_print+=missing
    print("csv file generated")
    return ordered_result, missing_print, analysis_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training value Processing")
    parser.add_argument("log", help="log file to process", default=None)
    args = parser.parse_args()
    run = 0
    hostname = ""
    bios = ""
    if os.path.isdir(args.log):
        log_files = get_files_from_directory(args.log)
        newdir, ext = os.path.splitext(os.path.abspath(log_files[0]))
        base = os.path.splitext(os.path.basename(log_files[0]))[0]
        if not os.path.exists(newdir):
            os.mkdir(newdir)
        out_csv = os.path.join(newdir, f"{base}__log_consolidated_jmp.csv")
        analysis_csv = os.path.join(newdir, f"{base}_log_analysis.csv")
        for file in log_files:
            base = os.path.splitext(os.path.basename(file))[0]
            bios, hostname = get_bios_hostname(base)
            process_decodedlog(file, out_csv, run, base, hostname, bios, analysis_csv)
            run = run + 1
        calculate_standard_deviation_and_range(analysis_csv)
    else:
        if os.path.exists(args.log):
            newdir, ext = os.path.splitext(os.path.abspath(args.log))
            base = os.path.splitext(os.path.basename(args.log))[0]
            if not os.path.exists(newdir):
                os.mkdir(newdir)
            out_csv = os.path.join(newdir, f"{base}_log_consolidated_jmp.csv")
            bios, hostname = get_bios_hostname(base)
            process_decodedlog(args.log, out_csv, run, base, hostname, bios, "")
        else:
            sys.exit(f"File {args.log} does not exist")
    print("csv file generated")


