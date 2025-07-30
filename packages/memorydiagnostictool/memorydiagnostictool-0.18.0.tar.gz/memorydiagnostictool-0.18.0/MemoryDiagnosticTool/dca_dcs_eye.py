
"""
Author  : john.khor@amd.com
Desc    : DCA and DCS Training Data Processing
"""

import sys, os
import re
import argparse
import pandas as pd
import numpy as np
#from pylab import *
from matplotlib import pyplot
from matplotlib import patches
from matplotlib import cm

dcavref_hash = re.compile("CHANNEL:\s*([0-9]),\s*PHY:\s*([0-9]),\s*PHYINIT:.*HOST_DCA_COMP.*Lane:(.*?)Vref:(.*?)Channel")
dcsvref_hash = re.compile("CHANNEL:\s*([0-9]),\s*PHY:\s*([0-9]),\s*PHYINIT:.*HOST_DCS_COMP.*Pin:(.*?)Vref:(.*?)Channel:")
# rcd_info_hash = re.compile("RCD Write Channel ([0-9]) SubChannel ([0-9]) Page 0x([0-9A-Fa-f]+) Register (0x[0-9A-Fa-f]+) Data 0x([0-9A-Fa-f]+)")
#rcd_info_hash = re.compile("CHANNEL:\s*([0-9]),\s*PHY:\s*([0-9]),\s*PHYINIT:\s*[MemDdr5RcdWriteWrapper]SubChannel: ([0-9]), Dimm: ([0-9]) Page: 0x([0-9A-Fa-f]+) RW([0-9A-Fa-f]+) data is 0x([0-9A-Fa-f]+)")
rcd_info_hash = re.compile("CHANNEL:\s*([0-9]),\s*PHY:\s*([0-9]),\s*PHYINIT:\s*\[MemDdr5RcdWriteWrapper\]SubChannel: ([0-9]), Dimm: ([0-9]) Page: 0x([0-9a-fA-F]+) RW([0-9a-fA-F]+) data is 0x([0-9a-fA-F]+)")
ch_phy_hash   = re.compile("CHANNEL:\s*([0-9]),\s*PHY:\s*([0-9]),\s*PHYINIT:")
clk_data_hash = re.compile("CHANNEL:\s*([0-9]),\s*PHY:\s*([0-9]),\s*PHYINIT:\s*BTFW:.*\[DCSTDCDS\]\s*([0-9a-f]+)")
#rcd_info_hash = re.compile("RCD Write Channel ([0-9]) SubChannel ([0-9]) Page 0x([0-9A-Fa-f]+) Register (0x[0-9A-Fa-f]+) Data 0x([0-9A-Fa-f]+)")

ca_rw_range = [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]
cs_rw_range = [0x48, 0x49]       
ccc_rw_range = ca_rw_range + cs_rw_range
ccc_ref_dict = dict(zip(ccc_rw_range, ['DCA0','DCA1','DCA2','DCA3','DCA4','DCA5','DCA6','DPAR','DCS0','DCS1']))




class RCDState:
    def __init__(self, ch, sch, pg, reg, val):
        self.channel = ch
        self.subchannel = sch
        self.page = pg
        self.reg = reg
        self.value = val

    def convert(self):
        self.value = int(self.value, 16)
        self.reg = int(self.reg, 16)

class Eye:
    def __init__(self, c,p,reg,d):
        self.channel = c
        self.phy = p
        self.reg = reg
        self.data = d
        self.count = 0


def get_dcs_train(datas):
    cs_data = {}
    for ch in range(8):
        for phy in range(2):
            for cs in range(2):
                ch_phy_ln = f"{ch}_{phy}_DCS{cs}"
                cs_data.update({ch_phy_ln:{}})
                cs_data[ch_phy_ln] = 0
    for line in datas:
        line = line.strip()
        dcsvref_search = dcsvref_hash.search(line)
        if(dcsvref_search):
            (ch, phy, ln, csv) = dcsvref_search.groups()
            ch  = int(ch)
            phy = int(phy)
            ln  = int(ln)
            csv = int(csv)
            ch_phy_ln = f"{ch}_{phy}_DCS{ln}"
            cs_data[ch_phy_ln] = csv
    return cs_data

def get_dca_train(datas):
    ca_data = {}
    for ch in range(8):
        for phy in range(2):
            for ca in range(8):
                if ca == 7:
                    ch_phy_ln = f"{ch}_{phy}_DPAR"
                else:
                    ch_phy_ln = f"{ch}_{phy}_DCA{ca}"
                ca_data.update({ch_phy_ln:{}})
                ca_data[ch_phy_ln] = 0
    for line in datas:
        line = line.strip()
        dcavref_search = dcavref_hash.search(line)
        if(dcavref_search):
            (ch, phy, ln, cav) = dcavref_search.groups()
            ch  = int(ch)
            phy = int(phy)
            ln  = int(ln)
            cav = int(cav)
            if ln == 7:
                ch_phy_ln = f"{ch}_{phy}_DPAR"
            else:
                ch_phy_ln = f"{ch}_{phy}_DCA{ln}"
            ca_data[ch_phy_ln] = cav
    return ca_data

def _reverse(value):
    value = f"{value:0128b}" # convert to binary
    value = list(value)      # make it to list for reversing
    value.reverse()          
    value = f"{int(''.join(value), 2):032x}" #convert to 32 hex string 
    return value

def picture_dump(df, out_pic_path):
    print('Generating Pictures....')
    col_code = cm.Set1 ## colour code
    phys = list(set(df.PHY))
    chs  = list(set(df.CH))
    cols = 10 # fix 10 columns
    rows = len(phys)*len(chs)
    hspace = np.linspace(0.90, 0.98, 16)[len(chs)]
    ax = [i for i in range(rows*cols)]
    pyplot.figure(figsize = (cols*3, rows*3))
    pyplot.figtext(0.5, 0.99, f"DCA DPAR DCS Plots", fontsize=18, va='top', ha='center')
    colours = col_code(np.linspace(0, 1, cols))

    tlegend = [patches.Patch(color=c, label=ccc_ref_dict[ccc_rw_range[i]]) for c,i in zip(colours, range(cols))]
    for r in range(rows):
        for c in range(cols):
            i = r*(cols)+c
            ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
    ## 
    for rf in set(df.RawFile):
        i = 0
        bn, ext = os.path.splitext(rf)
        if out_pic_path:
            filename = os.path.basename(rf)
            bn = filename.split('.')[0]
            out_pic =  os.path.join(out_pic_path, f"{bn}_eye.jpg")
        else:
            out_pic =  f"{bn}_eye.jpg"
        print(out_pic)
        for ch in chs:
            for phy in phys:
                for rw_i in ccc_rw_range:
                    rw = ccc_ref_dict[rw_i]
                    pyplot.axes(ax[i])
                    pyplot.title(f'CH{ch} PHY{phy} {rw}', fontsize = 12)
                    subset = df[(df.CH==ch) & (df.PHY==phy) & (df.RW==rw)]
                    # ymin, ymax = subset.Vref_Offset.min()-5,  subset.Vref_Offset.max()+5
                    # xmin, xmax = subset.Delay_Offset.min()-5, subset.Delay_Offset.max()+5
                    # ylim(ymin, ymax); yticks(np.arange(ymin, ymax, 10))
                    # xlim(xmin, xmax); xticks(np.arange(xmin, xmax, 10))
                    ax[i].scatter(subset.DELAY, subset.VREF, color=colours[i%cols], alpha = 0.5, marker = '.')
                    i+=1
        pyplot.tight_layout()
        pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
        pyplot.subplots_adjust(top = hspace, right = 0.95)
        # show()
        pyplot.savefig(out_pic)

def calculate_1d(df):
    df['Vref_Offset'] = df.apply(lambda x: int(x.VREF) - int(x.Vref_Center), axis = 1)
    df['Delay_Offset']   = df.apply(lambda x: int(x.DELAY) - int(x.Delay_Center), axis = 1)
    tbrl = {}
    chs  = set(df.CH)
    phys = set(df.PHY)
    rws = set(df.RW)
    for c in chs:
        for p in phys:
            for rw in rws:
                bit = f'{c}_{p}_{rw}'
                subdf = df[(df.CH==c) & (df.PHY==p) & (df.RW==rw)]                    
                top, btm, lft, rgt = 999,999,999,999
                if not subdf.empty:
                    max_v = subdf.Vref_Offset.max()
                    min_v = subdf.Vref_Offset.min()
                    
                    EH_l = subdf[subdf.Delay_Offset==0].Vref_Offset.tolist()
                    if len(EH_l)>0:
                        if 0 in EH_l:
                            top = btm = 0
                        else:
                            top_list = subdf[(subdf.Vref_Offset>0)&(subdf.Delay_Offset==0)].Vref_Offset.tolist()
                            btm_list = subdf[(subdf.Vref_Offset<0)&(subdf.Delay_Offset==0)].Vref_Offset.tolist()
                            top = min(top_list) if len(top_list)>0 else max_v
                            btm = max(btm_list) if len(btm_list)>0 else min_v
                    else:
                        top_list = subdf[(subdf.Vref_Offset>0)&(subdf.Delay_Offset<5)&(subdf.Delay_Offset>-5)].Vref_Offset.tolist()
                        btm_list = subdf[(subdf.Vref_Offset<0)&(subdf.Delay_Offset<5)&(subdf.Delay_Offset>-5)].Vref_Offset.tolist()
                        top = min(top_list) if len(top_list)>0 else max_v
                        btm = max(btm_list) if len(btm_list)>0 else min_v
                        
                    EW_l = subdf[subdf.Vref_Offset==0].Delay_Offset.tolist()
                    if len(EW_l)>0 and not(0 in EW_l):
                        rgt = subdf[(subdf.Vref_Offset==0)].Delay_Offset.max()
                        lft = subdf[(subdf.Vref_Offset==0)].Delay_Offset.min()
                else:
                    top, btm, lft, rgt = 0,0,0,0
                tbrl.update({bit:[top, btm, rgt, lft]})
    df['Top'] = df.apply(lambda x: int(tbrl[f'{x.CH}_{x.PHY}_{x.RW}'][0]), axis = 1)
    df['Btm'] = df.apply(lambda x: int(tbrl[f'{x.CH}_{x.PHY}_{x.RW}'][1]), axis = 1)
    df['Rgt'] = df.apply(lambda x: int(tbrl[f'{x.CH}_{x.PHY}_{x.RW}'][2]), axis = 1)
    df['Lft'] = df.apply(lambda x: int(tbrl[f'{x.CH}_{x.PHY}_{x.RW}'][3]), axis = 1)
    return df

def process_eye(eyes = [Eye], outlog = None, rawfile = '', cs_datas = {}, ca_datas = {}):       
    data_struct = {'CH' :[],\
                   'PHY':[],\
                   'RW' :[],\
                   'VREF':[],\
                   'DELAY':[]}
    if outlog != None:
        ofh = open(outlog, 'w')
    for eye in eyes:
        if eye.reg not in ccc_rw_range:
            continue
        ofh.write(f"Channel {eye.channel} Phy {eye.phy} RW{eye.reg:02x}\n")

        # print(f"Channel {eye.channel} Phy {eye.phy} RW{eye.rw:02x}")
        for v_data in sorted(list(eye.data.keys()), reverse = True):
            t_data_h = ''.join(eye.data[v_data])
            ofh.write(f"{v_data:3} {t_data_h}\n")
            # print(f"{v_data:3} {t_data_h}")
            t_data_h = re.sub(' ','',t_data_h)
            t_data_b = ''.join([f"{int(i, 16):04b}" for i in t_data_h])

            ccc = ccc_ref_dict[eye.reg]               
            delays = []
            for t, b in enumerate(t_data_b):
                if t<(len(t_data_b)-1):
                    if (t_data_b[t]!=t_data_b[t+1]):
                        if t_data_b[t] < t_data_b[t+1]:
                            delays.append(t)
                        else:
                            delays.append(t+1)
            data_struct['CH'].extend([eye.channel]*len(delays))
            data_struct['PHY'].extend([eye.phy]*len(delays))
            data_struct['RW'].extend([ccc]*len(delays))
            data_struct['VREF'].extend([v_data]*(len(delays)))
            data_struct['DELAY'].extend(delays)
    df = pd.DataFrame(data_struct)
    df['RawFile'] = rawfile
    cccdata = {}
    cccdata.update(cs_datas)
    cccdata.update(ca_datas)
    df['Vref_Center'] = df.apply(lambda x: cccdata[f"{x.CH}_{x.PHY}_{x.RW}"], axis = 1)
    t_datas = get_timing_center(df)
    df['Delay_Center'] = df.apply(lambda x: t_datas[f"{x.CH}_{x.PHY}_{x.RW}"], axis = 1)
    calculate_1d(df)
    return df

def get_timing_center(df):
    cccs = ['DCA{i}' for i in range(7)] + ['DPAR'] + ['DCS' for i in range(2)]
    t_datas = {}
    for ch in range(8):
        for phy in range(2):
            for c in cccs:
                ch_phy_ln = f"{ch}_{phy}_{c}"
                t_datas.update({ch_phy_ln:{}})
                t_datas[ch_phy_ln] = 0
    t_datas = {}
    for ch in set(df.CH):
        for phy in set(df.PHY):
            for rw in set(df.RW):
                vt = int(np.mean(df[(df.CH==ch) & (df.PHY==phy) & (df.RW==rw)].Vref_Center))
                t_lr = df[(df.CH==ch) & (df.PHY==phy) & (df.RW==rw) & (df.VREF==vt)].DELAY.tolist()
                t_delay = int(np.mean(t_lr))
                ch_phy_ln = f"{ch}_{phy}_{rw}"
                t_datas[ch_phy_ln] = t_delay
    return t_datas
    
def serialize_data(log):
      
    chlogs = {i:[] for i in range(8)}
    with open(log, 'r') as ifh:
        for line in ifh.readlines():
            line = line.strip()
            match = rcd_info_hash.search(line)
            if match:
                (ch, phy, sch, dimm, pg, reg, v) = match.groups()
                # ch, phy, pg, reg, v = match.groups()
                chlogs[int(ch)].append(f"{line}")
            match = clk_data_hash.search(line)        
            if match:
                ch, phy, data = match.groups()
                chlogs[int(ch)].append(f"{line}")
            match = dcavref_hash.search(line)
            if match:
                ch, phy, l, v = match.groups()
                chlogs[int(ch)].append(f"{line}")
            match = dcsvref_hash.search(line)
            if match:
                ch, phy, l, v = match.groups()
                chlogs[int(ch)].append(f"{line}")
    output = []
    for k, v in chlogs.items():
        for l in v:
            output.append(l)
    return output

def analyze_log(datas):
    rcd_s = {id:None for id in ccc_rw_range}
    eyes = list()
    for line in datas:
        line = line.strip()
        rcd_info_search = rcd_info_hash.search(line)
        if(rcd_info_search):
            (ch, phy, sch, dimm, pg, reg, v) = rcd_info_search.groups()
            # (ch, sch, pg, reg, v) = rcd_info_search.groups()
            rcd = RCDState(ch, sch, pg, reg, v)
            rcd.convert() # convert value set into RCD
            rcd_s[reg] = rcd
            
        #BTFW processing
        clk_data_hash_search = clk_data_hash.search(line)
        if(clk_data_hash_search):
            channel, phy, data = clk_data_hash_search.groups()
            channel = int(channel)
            phy = int(phy)
            data = data.strip()
            data = _reverse(int(data,16))
            rcd_set_value = rcd.value
            if not eyes: # eye is empty
                eyes.append(Eye(channel,phy,rcd.reg,{rcd_set_value: [data]}))
            else: # not empty, proceed to append data
                found = False
                for eye in eyes:
                    if eye.channel == channel and eye.phy == phy and eye.reg == rcd.reg: # match he phy channel and RCW number
                        if rcd_set_value in eye.data:
                            if eye.reg in cs_rw_range:   # detection for CS
                                if len(eye.data[rcd_set_value])<2: # take only the raw data for CS
                                    eye.data[rcd_set_value].insert(0, data)
                            elif eye.reg in ca_rw_range: # detection for CA
                                eye.data[rcd_set_value].append(data)
                        else:
                            eye.data[rcd_set_value] = [data]
                        found = True
                        break
                if found == False:
                    eyes.append(Eye(channel,phy,rcd.reg,{rcd_set_value: [data]}))
    return eyes

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


def scan_dcs_dca(inputlog, mdt_path, stat_csv):
    dflist = []
    rawfile = ''
    basename = os.path.splitext(os.path.basename(inputlog[0]))[0]
    out_csv = os.path.join(mdt_path, f"{basename}_DCADCS_Eye.csv")    
    if len(inputlog)> 0:
        for file in inputlog:
            try:
                dflist = []
                base = os.path.splitext(os.path.basename(file))[0]
                #bios, hostname = get_bios_hostname(base)
                rawfile = file
                bn = file.split('.')[0] 
                out_log = os.path.join(mdt_path, f"{base}_eye")
                srlz_data = serialize_data(file)
                cs_datas = get_dcs_train(srlz_data)
                ca_datas = get_dca_train(srlz_data)
                eyes = analyze_log(srlz_data)
                dflist.append(process_eye(eyes, out_log, rawfile, cs_datas, ca_datas))
                df = pd.concat(dflist)
                if df.empty:
                    sys.exit("DCS DCA No Data Found!")
                picture_dump(df, mdt_path)
                out_stat_csv = os.path.join(mdt_path, f"{base}_DCSDCA_Eye_STAT.csv")
                out_stat_csv = stat_csv
                dfstat = df.drop_duplicates(subset = ["RawFile","PHY","CH","RW"])
                #dfstat['Filename'] = dfstat['RawFile'].apply(lambda x: os.path.basename(x))
                dfstat = dfstat.copy()  # Create a copy of the DataFrame slice
                dfstat['Filename'] = dfstat['RawFile'].apply(lambda x: os.path.basename(x))
                if os.path.exists(out_stat_csv):
                    dfstat.to_csv(out_stat_csv, mode="a", header=False, index = 0)
                else:
                    dfstat.to_csv(out_stat_csv, mode="a", header=True, index = 0)
                out_csv = os.path.join(mdt_path, f"{base}_DCADCS_Eye.csv") 
                df.to_csv(out_csv, index = 0)   
            except:
                print("[DCS DCA]: Parssing error for file: ", file)         
    else:
        print("no decoded log file found in the folder")
       


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'DCA Training Eye Processing')
    parser.add_argument('log',       help='log file to process', default=None)
    args = parser.parse_args()

    file = args.log
    if os.path.exists(file):
        if os.path.isfile(file):
            files = [file]
            newdir  = os.path.dirname(file)
        elif os.path.isdir(file):
            files = [i for i in os.listdir(file) if i.endswith('.log')]
            newdir = file
    else:
        sys.exit("FILE not exists") 
    basename = os.path.splitext(os.path.basename(file))[0]
    out_csv = os.path.join(newdir, f"{basename}_DCADCS_Eye.csv")
    dflist = []
    rawfile = ''
    for f in files:
        file = os.path.join(newdir, f)
        rawfile = file
        bn = f.split('.')[0]
        out_log = os.path.join(newdir, f"{bn}_eye")
        srlz_data = serialize_data(file)
        cs_datas = get_dcs_train(srlz_data)
        ca_datas = get_dca_train(srlz_data)
        eyes = analyze_log(srlz_data)
        dflist.append(process_eye(eyes, out_log, rawfile, cs_datas, ca_datas))
    df = pd.concat(dflist)
    if df.empty:
        sys.exit("No Data Found!")
    picture_dump(df, "")
    out_stat_csv = os.path.join(newdir, f"{basename}_DCSDCA_Eye_STAT.csv")
    dfstat = df.drop_duplicates(subset = ["RawFile","PHY","CH","RW"])
    dfstat.to_csv(out_stat_csv, index = 0)
    df.to_csv(out_csv, index = 0)
    




