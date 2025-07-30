"""
Author  : john.khor@amd.com
Desc    : Plot Read Write Data Eye at each training step that is available
"""
import os, re, argparse
import pandas as pd
import numpy as np
#from pylab import *
from matplotlib import pyplot
from matplotlib import patches
from matplotlib import animation
from matplotlib import cm
from PIL import Image



class Tempdata():
    prm  = None
    oe   = None
    ch   = None
    cs   = None
    phy  = None
    bit  = None
    base = [0,0]

ch_phy_info = re.compile("CHANNEL:\s*([0-9]+),\s*PHY:\s*([0-9]+),\s*PHYINIT:")
mr10_hash = re.compile("BTFW:.*MR10\[dbyte(\d+).nibble(\d+)\]: 0x([0-9A-Fa-f]+)")
mr40_hash = re.compile("BTFW:.*MR40\[dbyte(\d+).nibble(\d+)\]: 0x([0-9A-Fa-f]+)")
mr40_hash = re.compile("BTFW:.*MR40.*Dbyte 0x(\d+), Nibble 0x(\d+), Mr40 0x(\d+),")

def serialize_data(log):
    chlogs = {f"{ch}_{phy}":[] for ch in range(8) for phy in range(2)}
    with open(log, 'r') as ifh:
        for line in ifh.readlines():
            line = line.strip()
            match = ch_phy_info.search(line)
            if match:
                ch, phy = match.groups()
                ch_phy = f"{int(ch)}_{int(phy)}"
                chlogs[ch_phy].append(f"{line}")
    output = []
    for k, v in chlogs.items():
        for l in v:
            output.append(l)
    return output

def _round(x, base=5):
    return base * round(x/base)

def twos_comp(val, bits=7):
    if (val & (1 << (bits - 1))) != 0: 
        val = val - (1 << bits)
    return val 

def getmr10(datas):
    mr10_ref = range(0x7d, -1,-1)
    jedec_ref = [0x7d-i for i in mr10_ref]
    txv = dict(zip(mr10_ref, jedec_ref))
    
    mr10_datas = {}
    for ch in range(8):
        for phy in range(2):
            for bit in range(40):
                ch_phy_bit = f"{ch}_{phy}_{bit}"
                mr10_datas.update({ch_phy_bit:0})
    for d in datas:
        match = ch_phy_info.search(d)
        if match:
            ch, phy = match.groups()
            ch = int(ch)
            phy = int(phy)
        match = mr10_hash.search(d)
        if match:
            db, nb, val = match.groups()
            db = int(db)
            nb = int(nb)
            val = txv[int(val, 16)&0x7F] # refer JEDEC SPEC MR10; index started from 35%
            for b in range(4):
                bit = (db*8)+(nb*4)+b
                ch_phy_bit = f"{ch}_{phy}_{bit}"
                mr10_datas[ch_phy_bit] = val
    return mr10_datas

def getmr40(datas):
    mr40_datas = {}
    for ch in range(8):
        for phy in range(2):
            for cs in range(4):
                for bit in range(40):
                    ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                    mr40_datas.update({ch_phy_bit:0})
    for d in datas:
        match = ch_phy_info.search(d)
        if match:
            ch, phy = match.groups()
            ch = int(ch)
            phy = int(phy)
        match = mr40_hash.search(d)
        if match:
            db, nb, val = match.groups()
            db = int(db)
            nb = int(nb)
            val = int(val, 16)
            for cs in range(4): # ranks
                for b in range(4): # bits per nibble
                    bit = (db*8)+(nb*4)+b
                    ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                    mr40_datas[ch_phy_bit] = val
    return mr40_datas

class MR():
    def __init__(self, log):
        self.mr_datas = {}
        self.read_mr(log)
        
    def read_mr(self, log):
        mr_num_rk = re.compile("MR (\d+),.*Rank: (\d+)")
        mr_dev_val = re.compile("\[DBV_MR\] (.*)")
        for ch in range(8):
            for phy in range(2):
                for cs in range(4):
                    for bit in range(40):
                        ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                        self.mr_datas.update({ch_phy_bit:{}})
        with open(log, 'r') as ifh:
            for line in ifh:
                line = line.strip()
                if line=='': continue
                match = ch_phy_info.search(line)
                if match:
                    ch, phy = match.groups()
                    ch = int(ch)
                    phy = int(phy)
                match = mr_dev_val.search(line)
                if match:
                    content = match.group(1)
                    mr_num_rk_search = mr_num_rk.search(content)
                    if mr_num_rk_search:
                        mr, cs = mr_num_rk_search.groups()
                    elif ('|' in content):
                        if re.search('Dev', content, re.I): continue
                        else:
                            mr_vals = re.sub('\s','', content).strip().split('|')
                            mr_val = [int(i,16) for i in mr_vals]
                            for dev, val in enumerate(mr_val):
                                for bt in range(4):
                                    self.mr_datas[f"{ch}_{phy}_{cs}_{(dev*4)+bt}"].update({mr:val})
    
    def getmr(self, mr):
        mr_datas = {}
        for ch_phy_bit, mr_val in self.mr_datas.items():
            val = mr_val[mr] if mr in mr_val else 0
            if mr=='10':
                mr10_ref = range(0x7d, -1,-1)
                jedec_ref = [0x7d-i for i in mr10_ref]
                txv = dict(zip(mr10_ref, jedec_ref))
                val = txv[val]
            mr_datas.update({ch_phy_bit:val})
        return mr_datas
    
class RdScanState():
    def __init__(self, ch, phy, rk, db, bit):
        self.ch  = ch
        self.phy = phy
        self.rk  = rk
        self.db  = db
        self.bit = bit
        self.count = 0
        self.data = []
    def add_data(self, d):
        self.data.append(d)

class eyeState():
    def __init__(self, prm, ch, phy, cs, bit, oe, dly_offset, count = 0):
        # self.btsq = btsq
        self.prm  = prm
        self.oe   = oe
        self.ch   = ch
        self.cs   = cs
        self.phy  = phy
        self.bit  = bit
        self.dly_offset = dly_offset
        self.count = count
        self.data = {'Upper':{}, 'Lower':{}}
    def add_data(self, dir, data):
        # if (self.prm == 'RD') and (self.oe=='_odd') and (self.ch==3) and (self.phy==1) and (self.cs==1) and (self.bit==32):
            # print(f"{self.count} {self.count//2}")
        self.data[dir].update({self.count//2:data})

# Class Function for Rd HW Accelerator Eye Scan
class Rd_Eye_Scan():
    def __init__(self, files, mdtpath):
        self.lane_info   = re.compile("BTFW:.*RDEYE Eye Scan.*Rank = (\d+), Byte = (\d+), (.*?) Nibble, Lane = (\d+), Pi code start = ([0-9]+)")
        self.start_info  = re.compile("BTFW:.*RDEYE Eye Scan.*lane_sel = (\d+), Pi offset = ([0-9]+)")
        self.eye_set_info = re.compile("RDEYE_SCAN_COMPLETED", re.I)
        # data_info   = re.compile("BTFW:.*RDEYE Eye Scan\].*Lane = (\d+), Vref[High|Low].*= ([0-9]+)", re.I)
        self.data_info = re.compile("BTFW:.*Rank = (\d), Byte = (\d), lane_sel = (\d), Lane = (\d), Vref(.*?) = ([0-9]+)", re.I)
        self.df_list = []
        self.files = files
        self._pic = False
        self._pch = False
        self._stat = True
        self._gif = False
        self._mdtpath = mdtpath        

    def get_data_frame(self, datas):
        data_struct = {'RawFile':[],\
                       'PRM':[],\
                       'CH':[],\
                       'PHY':[],\
                       'CS':[],\
                       'DB':[],\
                       'NIB':[],\
                       'DQ':[],\
                       'BIT':[],\
                       'DIR':[],\
                       'PI_Offset':[],\
                       'Vref_Offset':[],\
                       'Stage':[]
                       }
        for d in datas:
            for stg,t,dir,v in d.data:
                nib = (d.bit//4)%2
                dq  = d.bit%4
                data_struct['RawFile'].append(self.rawfile)
                data_struct['PRM'].append('RD_Comp')
                data_struct['CH'].append(d.ch)
                data_struct['PHY'].append(d.phy)
                data_struct['CS'].append(d.rk)
                data_struct['DB'].append(d.db)
                data_struct['NIB'].append(nib)
                data_struct['DQ'].append(dq)
                data_struct['BIT'].append(d.bit)
                data_struct['DIR'].append(dir)
                data_struct['Stage'].append(stg)
                data_struct['PI_Offset'].append(twos_comp(t&0x3F, 6))
                data_struct['Vref_Offset'].append(v)
        return pd.DataFrame(data_struct)

    def calculate_1d(self, df):
        tbrl = {}
        prms = set(df.PRM)
        chs  = set(df.CH)
        phys = set(df.PHY)
        cs_s = set(df.CS)
        bits = set(df.BIT)
        for rf in set(df.RawFile):
            tbrl.update({rf:{}})
            for prm in prms:
                for c in chs:
                    for p in phys:
                        for r in cs_s:
                            for b in bits:
                                bit = f'{prm}_{c}_{p}_{r}_{b}'
                                tbrl[rf].update({bit:[]})
                                subdf = df[(df.RawFile==rf) & (df.PRM==prm) & (df.CH==c) & (df.PHY==p) & (df.CS==r) & (df.BIT==b)]                    
                                top, btm, lft, rgt = 999,999,999,999
                                if not subdf.empty:
                                    max_t = subdf.PI_Offset.max()
                                    min_t = subdf.PI_Offset.min()
                                    
                                    EW_l = subdf[subdf.Vref_Offset==0].PI_Offset.tolist()
                                    if len(EW_l)>0 :
                                        if 0 in EW_l:
                                            lft = rgt = 0
                                        else:
                                            rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                            lft = max(lft_list) if len(lft_list)>0 else min_t
                                    else:
                                        rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                        lft = max(lft_list) if len(lft_list)>0 else min_t
                                        
                                    EH_l = subdf[subdf.PI_Offset==0].Vref_Offset.tolist()
                                    if len(EH_l)>0 and not(0 in EH_l):
                                        top = subdf[(subdf.PI_Offset==0)].Vref_Offset.max()
                                        btm = subdf[(subdf.PI_Offset==0)].Vref_Offset.min()
                                else:
                                    top, btm, lft, rgt = 0,0,0,0
                                tbrl[rf].update({bit:[top, btm, rgt, lft]})
                                    
        df['Top'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][0]), axis = 1)
        df['Btm'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][1]), axis = 1)
        df['Rgt'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][2]), axis = 1)
        df['Lft'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][3]), axis = 1)

    def picture_dump_ch(self, df):
        col_code = cm.rainbow ## colour code
        rflist = list(set(df.RawFile))
        chs  = sorted(set(df.CH))
        stages = set(df.Stage)
        css  = sorted([i for i in range(4)])
        bits = sorted([i for i in range(40)])
        phys = sorted([i for i in range(2)])
        nibs = [i for i  in range(10)]
        # grids = len(chs)*len(phys)*len(css)*len(nibs)
        grids = len(phys)*len(bits)
        cols = 8 # fix 8 columns
        rows = int(grids/cols)
        hspace = 0.95
        for rf in rflist:
            for stg in stages:
                for ch in chs:
                    # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                    ax = [i for i in range(rows*cols)]
                    pyplot.figure(figsize = (cols*3, rows*3))
                    pyplot.figtext(0.5, 0.99, f"CH{ch} RD Eye Scan", fontsize=20, va='top', ha='center')
                    colours = ['b','r','g','k']
                    tlegend = [patches.Patch(color=c, label=f"CS{i}") for c,i in zip(colours, [0,1,2,3])]
                    for r in range(rows):
                        for c in range(cols):
                            i = r*(cols)+c
                            ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                    ch = int(ch)
                    subset = df[(df.RawFile==rf) & (df.CH==ch) & (df.Stage==stg)]
                    if subset.empty:
                        i+=1
                        continue
                    xmin, xmax = -40, 40 #subset.PI_Offset.min()-5, subset.PI_Offset.max()+5
                    ymin, ymax = _round(subset.Vref_Offset.min()-10),  _round(subset.Vref_Offset.max()+10)
                    # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #                
                    i=0
                    for phy in phys:
                        phy = int(phy)
                        for bt in bits:
                            bit = int(bt)
                            db = int(bt//8)
                            nib = int((bt//4)%2)
                            # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                            pyplot.axes(ax[i])
                            pyplot.title(f'PHY{phy} DB{db} Nib{nib} DQ{bt%4}', fontsize = 10)                        
                            pyplot.ylim(ymin, ymax); pyplot.yticks(np.arange(ymin, ymax, int((ymax-ymin)/10)))
                            pyplot.xlim(xmin, xmax); pyplot.xticks(np.arange(xmin, xmax, 4), rotation = 90)
                            for cs in css:
                                cs = int(cs)
                                subset = df[(df.CH==ch) & (df.PHY==phy) & (df.BIT==bt)  & (df.CS==cs) & (df.RawFile==rf) & (df.Stage==stg)]
                                if subset.empty: continue
                                pyplot.axhline(0, color='0.5', linestyle = ':', alpha = 0.5)
                                pyplot.axvline(0, color='0.5', linestyle = ':', alpha = 0.5)
                                ax[i].scatter(subset.PI_Offset, subset.Vref_Offset, color=colours[cs], s=20, alpha = 0.8, marker = '.')
                                # if bt%4 ==3: i+=1
                            i+=1
                            # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                    pyplot.tight_layout()
                    pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                    pyplot.subplots_adjust(top = hspace, right = 0.95)
                    # show()
                    # out_pic = os.path.join(dirname, f"{basename}_ReadEyeScan.jpg")
                    if self._mdtpath:
                        filename = os.path.basename(rf)
                        bn = filename.split('.')[0]
                        out_pic = os.path.join(self._mdtpath, f'{bn}_RD_Composite_CH{ch}_{stg}.jpg')
                    else:
                        out_pic = os.path.splitext(rf)[0]+f'_RD_Composite_CH{ch}_{stg}.jpg'
                    pyplot.savefig(out_pic)
                    pyplot.close()
                    

    def picture_dump(self, df):
        col_code = cm.rainbow ## colour code
        rflist = list(set(df.RawFile))
        chs  = sorted(set(df.CH))
        stages = set(df.Stage)
        css  = sorted([i for i in range(4)])
        bits = sorted([i for i in range(40)])
        phys = sorted([i for i in range(2)])
        nibs = [i for i  in range(10)]
        # grids = len(chs)*len(phys)*len(css)*len(nibs)
        grids = len(chs)*len(phys)*len(bits)
        cols = 8 # fix 8 columns
        rows = int(grids/cols)
        hspace = np.linspace(0.95, 0.98, 16)[len(chs)]
        for rf in rflist:
            for stg in stages:
                # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                ax = [i for i in range(rows*cols)]
                pyplot.figure(figsize = (cols*3, rows*3))
                pyplot.figtext(0.5, 0.99, f"RD Eye Scan", fontsize=20, va='top', ha='center')
                colours = ['b','r','g','k']
                tlegend = [patches.Patch(color=c, label=f"CS{i}") for c,i in zip(colours, [0,1,2,3])]
                for r in range(rows):
                    for c in range(cols):
                        i = r*(cols)+c
                        ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                i = 0
                for ch in chs:
                    ch = int(ch)
                    subset = df[(df.RawFile==rf) & (df.CH==ch) & (df.Stage==stg)]
                    if subset.empty: 
                        i+=1
                        continue
                    xmin, xmax = -40, 40 #subset.PI_Offset.min()-5, subset.PI_Offset.max()+5
                    ymin, ymax = _round(subset.Vref_Offset.min()-10),  _round(subset.Vref_Offset.max()+10)
                    ylim(ymin, ymax); yticks(np.arange(ymin, ymax, int((ymax-ymin)/10)))
                    xlim(xmin, xmax); xticks(np.arange(xmin, xmax, 4), rotation = 90)
                    for phy in phys:
                        phy = int(phy)
                        for bt in bits:
                            # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                            pyplot.axes(ax[i])                        
                            bt = int(bt)
                            db = bt//8
                            nib = (bt//4)%2
                            pyplot.title(f'CH{ch} PHY{phy} DB{db} Nib{nib} DQ{bt%4}', fontsize = 10)
                            for cs in css:
                                cs = int(cs)
                                subset = df[(df.CH==ch) & (df.PHY==phy) & (df.BIT==bt)  & (df.CS==cs) & (df.RawFile==rf) & (df.Stage==stg)]
                                if subset.empty: continue
                                pyplot.axhline(0, color='0.5', linestyle = ':', alpha = 0.5)
                                pyplot.axvline(0, color='0.5', linestyle = ':', alpha = 0.5)
                                ax[i].scatter(subset.PI_Offset, subset.Vref_Offset, color=colours[cs], s=20, alpha = 0.8, marker = '.')
                                # if bt%4 ==3: i+=1
                            i+=1
                            # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                            pyplot.tight_layout()
                            pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                            pyplot.subplots_adjust(top = hspace, right = 0.95)
                        # show()
            # out_pic = os.path.join(dirname, f"{basename}_ReadEyeScan.jpg")
            if self._mdtpath:
                filename = os.path.basename(rf)
                bn = filename.split('.')[0]
                out_pic = os.path.join(self._mdtpath, f'{bn}_RD_Composite_{stg}.jpg')
            else:
                out_pic = os.path.splitext(rf)[0]+f'_RD_Composite_{stg}.jpg'
            pyplot.savefig(out_pic)
            pyplot.close()

    def process(self, srlz_data):
        header = re.compile("BTFW: \[RDEYE Eye\] (.*)")
        datas = []
        temp = Tempdata()
        ln_sel_ref = {0 : [3,1,6,7], 1 : [0,2,4,5]} 
        # temp = {}
        for line in srlz_data:
            line = line.strip()
            match = ch_phy_info.search(line)
            if match:
                ch, phy = match.groups()
                temp.ch = int(ch)
                temp.phy = int(phy)
            match = self.eye_set_info.search(line)
            if match:
                if len(datas)>0:
                    for d in datas:
                        if (d.ch==temp.ch) and (d.phy==temp.phy):
                            d.count+=1
                continue
            match = self.start_info.search(line)
            if match:
                ln_sel, pi_off = match.groups()
                pi_off = int(pi_off)
                temp.currpi = pi_off
                continue
            match = self.data_info.search(line)
            if match:
                rk, db, ln_sel, ln, dir, _data = match.groups()
                rk = int(rk)
                db = int(db)
                ln = int(ln)
                ln_sel = int(ln_sel)
                ln = ln_sel_ref[ln_sel][ln]
                bit = (db*8)+ln
                dir = dir.strip().lower()
                _data = twos_comp(int(_data) & 0x1FF, 9)
                if (((dir == 'high') & (_data<0)) | ((dir == 'low') & (_data>0))): continue
                if len(datas) == 0:
                    d = RdScanState(temp.ch, temp.phy, rk, db, bit)
                    datas.append(d)
                    datas[0].add_data((d.count, temp.currpi, dir, _data))
                else:
                    found = False
                    for d in datas:
                        if (d.ch==temp.ch) and (d.phy==temp.phy) and (d.rk==rk) and (d.db==db) and (d.bit==bit):
                            d.add_data((d.count, temp.currpi, dir, _data))
                            found = True
                            break;
                    if not found:
                        d = RdScanState(temp.ch, temp.phy, rk, db, bit)
                        d.add_data((d.count, temp.currpi, dir, _data))
                        datas.append(d)
        return self.get_data_frame(datas)
        
    def main(self):
        basename = os.path.splitext(os.path.basename(self.files[0]))[0]
        if self._mdtpath:
            out_csv = os.path.join(self._mdtpath, f"{basename}_ReadEyeScan.csv")
            out_stat_csv = os.path.join(self._mdtpath, f"MDT_ReadScan_STAT.csv")        
        else:
            out_csv = os.path.join(dirname, f"{basename}_ReadEyeScan.csv")
            out_stat_csv = os.path.join(dirname, f"{basename}_ReadScan_STAT.csv")
        for f in self.files:
            try:
                self.df_list = []
                self.rawfile = f
                srlz_data = serialize_data(f)
                self.df_list.append(self.process(srlz_data))
                df = pd.concat(self.df_list)
                if not df.empty:
                    df.to_csv(out_csv, mode="w", header=True, index = False)
                    if self._stat:
                        self.calculate_1d(df)   
                        dfstat = df.drop_duplicates(subset = ["RawFile","PRM","PHY","CH","CS","BIT"])
                        dfstat = dfstat[["RawFile","PRM","PHY","CH","CS","DB","NIB","DQ","BIT","Top","Btm","Rgt","Lft"]]
                        dfstat = dfstat.copy()  # Create a copy of the DataFrame slice
                        # Get just the filenames
                        dfstat['Filename'] = dfstat['RawFile'].apply(lambda x: os.path.basename(x))
                        # Add the IOD column based on filename content
                        dfstat['IOD'] = dfstat['Filename'].apply(lambda x: 0 if 'iod0' in x else (1 if 'iod1' in x else None))
                        if os.path.exists(out_stat_csv):
                            dfstat.to_csv(out_stat_csv, mode="a", header=False, index = 0)
                        else:
                            dfstat.to_csv(out_stat_csv, mode="a", header=True, index = 0)
                    if self._pic | self._gif | self._pch:
                        print('Generating RD_EYE_SCAN Pictures....')
                        if self._pch:
                            self.picture_dump_ch(df)
                        if self._pic or (len(set(df.CH))>1):
                            self.picture_dump(df)
            except:
                print("[Rd Eye Scan]: Parssing error for file: ", f)

# Class Function for Rd Wr FW Vref/Timing Eye Scan
class PMU_Eye():
    def __init__(self, files, mdtpath):
        self.txswitchrank = re.compile("BTFW:.*\[WR TRAIN\] D5WrTrain.*training start rank ([0-9])")
        self.r_train_v_info = re.compile("BTFW:.*Read Train Vref: Rank 0x([0-9a-fA-F]+), Dbyte 0x([0-9a-fA-F]+), Nibble 0x([0-9a-fA-F]+), Dq 0x([0-9a-fA-F]+), Vref 0x([0-9a-fA-F]+)")
        self.r_train_d_info = re.compile("BTFW:.*Read Train Delays: Rank 0x([0-9a-fA-F]+), Dbyte 0x([0-9a-fA-F]+), Nibble 0x([0-9a-fA-F]+), Dq 0x([0-9a-fA-F]+), Phase 0x([0-9a-fA-F]+), PiCode 0x([0-9a-fA-F]+)")
        self.r_chinfo = re.compile("Dumping(.*?)Eyes for: Cs:(.*?), Dbyte:(.*?), Nibble:(.*?), Dq:(.*)")
        self.roe_info = re.compile('Dumping Rd Eyes for Delay/Vref (.*?) Phase')
        self.w_chinfo = re.compile("Dumping(.*?)Eye for: Ch:(.*?), Db:(.*?), Dq:(.*)")
        self.cntr_info = re.compile("-- DelayOffset: (\d+), CenterDelay: (\d+), CenterVref: (\d+) --" )
        self.data_cntr = re.compile("Train Eye EyePts(.*?):(.*)")
        self.btfw_seq = re.compile("BTFW:.*BTFWSEQ: TRAIN STEP:(.*?)Enabled: 1 Start.")
        self.read_base = re.compile("DAC Vref Step Size =\s*[0-9A-Fa-f].*Delay Step Size =\s*[0-9a-fA-F].*EyePtsLowerBase.*= ([0-9a-fA-F]+)\s*EyePtsUpperBase.*= ([0-9a-fA-F]+)")
        self.eye_param_hash = re.compile("<<- 2D Eye Print, (.*?) Eye(.*?) ->>")
        self.rd_phase_info = re.compile("\s(.*?) Phase")
        self.rk_db_dq_info = re.compile("<<--- Rank.*(\d+), DB.*(\d+), Dq.*(\d+) --->>")
        self.rk_info = re.compile("<<--- Rank:(\d+) --->>")
        self.nb_info = re.compile("<<--- Nb:(\d+) --->>")
        self.rk_ch_info = re.compile("<<--- Rank: (\d+), Ch: (\d+) --->>")
        self.df_list = []
        self.eye_datas = {}
        self.files = files
        self.dummy_train_data = {}
        self._mdtpath = mdtpath
        self._params = ['RD', 'WR', 'QCA', 'CS']
        self._pic = True
        self._pch = False
        self._stat = True
        self._gif = False
    
    def identify_mr40(self, df):
        for ch in set(df.CH):
            for phy in set(df.PHY):
                for cs in set(df.CS):
                    for bit in set(df.BIT):
                        for prm in set(df.PRM):
                            subset = df[(df.PRM==prm) & (df.CH==ch) & (df.PHY) & (df.CS==cs) & (df.BIT==bit)]
                            if ('RD' not in prm) or (subset.empty): continue
                            ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                            mr40 = 0
                            delay_range = [subset.DELAY.min(), subset.DELAY.max()]
                            pi = self.read_data[ch_phy_bit]['pi'][prm][-1]
                            prm_ch_phy_bit = f"{prm}_{ch}_{phy}_{cs}_{bit}"
                            pi += (self.mr40_stat[prm_ch_phy_bit]['edge'] if pi<delay_range[0] else 0)
                            self.read_data[ch_phy_bit]['pi'][prm] = pi

    def get_train_data(self, datas):
        trn_step_params = {'CS':  ['VREFCS', 'QACSDELAY', 'QBCSDELAY'],\
                           'QCA' :['VREFCA', 'QACADELAY', 'QBCADELAY'],\
                           'WL'  :['TXDQS_COARSE_DELAY', 'TXDQS_FINE_DELAY', 'MR3_WICA', 'MR7_0.5TCK_OFFSET'],\
                           'RXEN':['RXENCOARSEDLY', 'RXENFINEDLY'],\
                           'RD'  :['AFE_DACCTRL', 'RXDQS_DPI_CLKCCODE_ODD', 'RXDQS_DPI_CLKTCODE_EVEN'],\
                           'WR'  :['DRAMVREF','TXDQNIBBLEDELAY', 'TXDQCOARSEDELAY', 'TXDQFINEDELAY']}
        trn_rk_info = re.compile("^Rank: (\d+), (.*)")
        trn_info = re.compile("<< (.*?) >>")
        trn_dmp_info = re.compile("(PHYINIT:.*\|.*)")
        trn_val_params = []
        for k, v in trn_step_params.items():
            if k in self._params:
                trn_val_params.extend(v)
        ## Initialize dummy default data
        param_data = {}
        for prm in trn_val_params:
            param_data.update({prm:{}})
            for ch in range(8):
                for phy in range(2):
                    for cs in range(4):
                        for bit in range(40):
                            ch_phy_cs_bit = f'{ch}_{phy}_{cs}_{bit}'
                            param_data[prm].update({f'{ch}_{phy}_{cs}_{bit}':0})
        for content in datas:
            match = ch_phy_info.search(content)
            if match:
                ch, phy = match.groups()
                ch = int(ch)
                phy = int(phy)
            match = trn_info.search(content)
            if match:
                trn_param = match.group(1).strip()
                trn_rk_search = trn_rk_info.search(trn_param)
                if trn_rk_search:
                    cs, param = trn_rk_search.groups()
                    cs = int(cs)
                else:
                    param = trn_param
                    # handler for READ CS0 (RDAC) and CS1 (IDAC), rename AFE_IDACCTRL and AFE_RDACCTRL
                    if re.search('RDAC', param, re.I):
                        param = 'AFE_DACCTRL'
                        cs=0
                    elif re.search('IDAC', param, re.I):
                        param = 'AFE_DACCTRL'
                        cs=1
                    else: cs = 0
                param = re.sub(' ','_',param.strip().upper())
                # if (ch==5) and (phy==1) and (cs==0):
                    # print(param)
                continue
            if re.search('\|', content):
                if param not in trn_val_params: continue # skip unwanted training parameters
                if re.search('\]|:', content):
                    content = re.split(']|:', content)[-1]
                if re.search('Db|Dev', content): # header handler
                    per_db = True if re.search('^Db', content.strip()) else False                   
                    shared_bit = 1
                    if re.search('Dev(\d)|Nb(\d+)\s', content):
                        shared_bit = 4
                    elif re.search('Dq(\d)', content):
                        shared_bit = 1
                else: # is value content
                    content = re.sub('\s','', content).split('|')
                    values = []
                    for v in content:
                        if re.search('--', v):    v = 0
                        elif re.search('0x', v):  v = int(v, 16)
                        else:                     v = int(v, 10)
                        values.append(v)
                    (db, values) = (values[0], values[1:]) if per_db else (0, values)
                    ## special case for READ
                    if param in trn_step_params['RD']:
                        values = values[1:]
                    ## special case for READ
                    for idx, val in enumerate(values):
                        for dq in range(shared_bit):
                            bit = (db*8)+(idx*shared_bit)+dq
                            ch_phy_cs_bit = f"{ch}_{phy}_{cs}_{bit}"
                            param_data[param][ch_phy_cs_bit] = val
        ## structure to specific DQ / CA/ CS path 
        self.trained_data = {}
        for param in self._params:
            if param == 'RD':
                self.trained_data['RD_odd']  = {'VREF':param_data['AFE_DACCTRL'], 'DELAY':param_data['RXDQS_DPI_CLKCCODE_ODD']}
                self.trained_data['RD_even'] = {'VREF':param_data['AFE_DACCTRL'], 'DELAY':param_data['RXDQS_DPI_CLKTCODE_EVEN']}
            elif param == 'WR':            
                self.trained_data[param] = {'VREF':param_data['DRAMVREF'], 'DELAY': param_data['TXDQFINEDELAY']}
            elif param == 'QCA':
                self.trained_data[param] = {'VREF':param_data['VREFCA'], 'DELAY':param_data['QACADELAY']}
            elif param == 'CS':
                self.trained_data[param] = {'VREF':param_data['VREFCS'], 'DELAY':param_data['QACSDELAY']}


    def get_rd_train(self, datas):
        self.read_data = {}
        for ch in range(8):
            for phy in range(2):
                for rk in range(4):
                    for bit in range(40):
                        ch_phy_bit = f"{ch}_{phy}_{rk}_{bit}"
                        self.read_data.update({ch_phy_bit:{}})
                        self.read_data[ch_phy_bit] = {'vref':0, 'pi':{'RD_odd':[],'RD_even':[]}}
        for d in datas:
            match = ch_phy_info.search(d)
            if match:
                ch, phy = match.groups()
                ch = int(ch)
                phy = int(phy)
            match = self.r_train_v_info.search(d)
            if match:
                rk, db, nb, dq, vref = match.groups()
                rk = int(rk)
                db = int(db)
                nb = int(nb)
                dq = int(dq)
                bit = (db*8)+(nb*4)+dq
                if bit > 80: print(d)
                vref = int(vref, 16)
                ch_phy_bit = f"{ch}_{phy}_{rk}_{bit}"
                self.read_data[ch_phy_bit]['vref'] = vref
            match = self.r_train_d_info.search(d)
            if match:
                oe_ref = {0:'RD_odd',1:'RD_even'}
                rk, db, nb, dq, _ph, pi = match.groups()
                rk = int(rk)
                db = int(db)
                nb = int(nb)
                dq = int(dq)
                bit = (db*8)+(nb*4)+dq
                ph = oe_ref[int(_ph, 16)]
                pi = int(pi, 16)# + (128 if int(pi,16)<128 else 0)
                ch_phy_bit = f"{ch}_{phy}_{rk}_{bit}"
                # self.read_data[ch_phy_bit]['pi'][ph] = pi
                self.read_data[ch_phy_bit]['pi'][ph].append(pi)

    def get_wr_train(self, datas):
        ch_phy_info = re.compile("CHANNEL: ([0-9]+),  PHY: ([0-9]+),  PHYINIT: ")
        wr_trn_data = re.compile("\[WR TRAIN\] (.*)")
        wr_trn_info = re.compile("<< Rank: (\d+), (.*?) >>")
        dbidx = 0
        self.write_data = {}
        for ch in range(8):
            for phy in range(2):
                for cs in range(4):
                    for bit in range(40):
                        ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                        self.write_data.update({ch_phy_bit:{'DRAMVREF':0, 'TXDQDELAY':0}})
        for d in datas:
            match = ch_phy_info.search(d)
            if match:
                ch, phy = match.groups()
                ch = int(ch)
                phy = int(phy)
            match = wr_trn_data.search(d)
            if match:
                content = match.group(1)
                wr_trn_info_search = wr_trn_info.search(content)
                if wr_trn_info_search:
                    cs, param = wr_trn_info_search.groups()
                    cs = int(cs)
                    param = re.sub(' ','',param.upper())
                    self.write_data[f"{ch}_{phy}_{cs}_{bit}"].update({param:0})
                elif ('|' in content):
                    if re.search('Db', content, re.I):
                        dbidx = [i.strip().upper() for i in  content.strip().split('|')].index('DB')
                    if re.search('Dq', content, re.I): 
                        dq_set = 1
                        continue
                    elif re.search('Nb', content, re.I): 
                        dq_set = 4
                        continue
                    else:
                        wr_train_vals = re.sub('\s','', content).strip().split('|')
                        db = int(wr_train_vals[dbidx]) #int(wr_train_vals.pop(0))
                        wr_train_vals = [int(i) for i in wr_train_vals[(dbidx+1):] if i.strip()!='']
                        for nb_dq, val in enumerate(wr_train_vals):
                            for bt in range(dq_set):
                                bit = (db*8) + (nb_dq*dq_set) + bt
                                # print(f"CH{ch:<2} PHY{phy:<2} CS{cs:<2} DB{db:<2} BIT{bit:<2} {param} = {val}")
                                self.write_data[f"{ch}_{phy}_{cs}_{bit}"][param] = val

    def fill_eye(self, df):
        delays = sorted([i for i in set(df.DELAY)])
        eye_s = {'Vref':[], 'Delay':[]}
        for t in delays:
            vrefs = df[df.DELAY == t].VREF.tolist()
            if (len(vrefs)==0) or any([np.isnan(i) for i in vrefs]):
                eye_s['Vref'].append(0)
                eye_s['Delay'].append(0)
            else:
                for v in range(int(min(vrefs)), int(max(vrefs))):
                    eye_s['Vref'].append(v)
                    eye_s['Delay'].append(t)
        return pd.DataFrame(eye_s)

    def eyeCoM(self, df):
        CoM = {}
        prms = set(df.PRM)
        chs  = set(df.CH)
        phys = set(df.PHY)
        cs_s = set(df.CS)
        bits = set(df.BIT)
        for prm in prms:
            for c in chs:
                for p in phys:
                    for r in cs_s:
                        for b in bits:
                            subdf = df[(df.PRM==prm) & (df.CH==c) & (df.PHY==p) & (df.CS==r) & (df.BIT==b)]
                            bit = f'{prm}_{c}_{p}_{r}_{b}'
                            eyedata = self.fill_eye(subdf)
                            if (len(subdf)<=2) or len(set(eyedata.Delay))<2 or len(set(eyedata.Vref))<2:
                                t_center = 0
                                v_center = 0
                            else:
                                weightedEH = 0; instantEH = 0
                                weightedEW = 0; instantEW = 0
                                delays = sorted([i for i in set(eyedata.Delay)])
                                for t in delays:
                                    edge = sorted(eyedata[eyedata.Delay == t].Vref.tolist())
                                    instantEH += edge[-1] - edge[0] 
                                    weightedEH += t*(edge[-1] - edge[0])
                                t_center = weightedEH / instantEH
                                vrefs = sorted([i for i in set(eyedata.Vref)])
                                for v in vrefs:
                                    edge = sorted(eyedata[eyedata.Vref == v].Delay.tolist())
                                    instantEW += edge[-1] - edge[0] 
                                    weightedEW += v*(edge[-1] - edge[0])
                                v_center = weightedEW / instantEW
                            CoM.update({bit:(t_center, v_center)})
        return CoM
    
    def construct_eye(self, prm, ch, phy, cs, bit, oddeven, dly_offset, dir, data_t, data_v):
        data = {'DELAY':data_t, 'VREF':data_v}
        if len(self.eye_datas)==0:
            eye = eyeState(prm, ch, phy, cs, bit, oddeven, dly_offset, 0)
            eye.add_data(dir, data)
            self.eye_datas = [eye]
        else:
            found = False
            for eye in self.eye_datas:
                if (eye.prm==prm and eye.ch==ch and eye.phy==phy and eye.cs==cs and eye.bit==bit and eye.oe==oddeven):
                    eye.count+=1
                    eye.add_data(dir, data)
                    found = True
                    break;
            if found == False:
                eye = eyeState(prm, ch, phy, cs, bit, oddeven, dly_offset, 0)
                eye.add_data(dir, data)
                self.eye_datas.append(eye)
    
    def make_df(self):
        data_dict = {'PRM':[],\
                     'CH':[],\
                     'PHY':[],\
                     'CS':[],\
                     'DB':[],\
                     'NIB':[],\
                     'DQ':[],\
                     'BIT':[],\
                     'PRE_LAUNCH':[],\
                     'ERROR':[],\
                     'VREF':[],\
                     'DELAY':[],
                    }
        for e in self.eye_datas:
            prm = e.prm+e.oe
            _data_top = e.data['Upper']
            _data_btm = e.data['Lower']
            db = e.bit//8
            nb = (e.bit//4)%2
            dq = e.bit%4
            ch_phy_bit = f"{e.ch}_{e.phy}_{e.cs}_{e.bit}"
            prm_ch_phy_bit = f"{prm}_{e.ch}_{e.phy}_{e.cs}_{e.bit}"
            total_sets = sorted([s for s in set([i for i in _data_top] + [i for i in _data_btm])])
            total_sets = sorted([i for i in total_sets if (i%2==0)])
            missing_data = False
            eye_closed = []
            for s in total_sets:
                mr40 = s//2
                ## ----------------------------------------- HANDLE MISSING DATA ---------------------------------------------- ##
                err_msg = ''
                err_template = 'ERROR on MR40={1} DQ{0}' if ('RD' in prm) else 'ERROR on DQ{0}'
                if (s not in _data_top) or (s not in _data_btm):
                    missing_data = True
                    err_msg = err_template.format(dq, s)
                    if   (s in _data_top) and (s not in _data_btm):
                        dummy_data = {'VREF': [np.nan for i in _data_top[s]['VREF']], 'DELAY':[i for i in _data_top[s]['DELAY']]}
                        _data_btm[s] = dummy_data
                    elif (s in _data_btm) and (s not in _data_top):
                        dummy_data = {'VREF': [np.nan for i in _data_btm[s]['VREF']], 'DELAY':[i for i in _data_btm[s]['DELAY']]}
                        _data_top[s] = dummy_data
                    else:
                        _data_top[s] = {'VREF': [np.nan], 'DELAY':[np.nan]}
                        _data_btm[s] = {'VREF': [np.nan], 'DELAY':[np.nan]}
                    v_top = _data_top[s]['VREF']
                    v_btm = _data_btm[s]['VREF']
                    
                if _data_top[s]['DELAY'] != _data_btm[s]['DELAY']:
                    print(f'TOP BOTTOM DELAY MISMATCH {prm} CH{e.ch} PHY{e.phy} CS{e.cs} DB{db} NB{nb} DQ{dq} set{s}')
                    continue
                total_delay = _data_top[s]['DELAY']
                invalid_data_found = 0
                for i, t in enumerate(total_delay):
                    mr40_edge = t
                    if ('RD' in prm):
                        self.mr40_stat[prm_ch_phy_bit]['edge'] = mr40_edge if (s and ('RD' in prm)) else 0
                    if t>127 and ('RD' in prm): break;
                    top = _data_top[s]['VREF'][i]
                    btm = _data_btm[s]['VREF'][i]
                    if (top > btm) or (missing_data):
                        if missing_data: top = btm = np.nan
                        data_dict['PRM'].extend([prm]*2)
                        data_dict['CH'].extend([e.ch]*2)
                        data_dict['PHY'].extend([e.phy]*2)
                        data_dict['CS'].extend([e.cs]*2)
                        data_dict['DB'].extend([db]*2)
                        data_dict['NIB'].extend([nb]*2)
                        data_dict['DQ'].extend([dq]*2)
                        data_dict['BIT'].extend([e.bit]*2)
                        data_dict['ERROR'].extend([err_msg]*2)
                        data_dict['PRE_LAUNCH'].extend([mr40]*2)
                        data_dict['VREF'].extend([top, btm] )
                        data_dict['DELAY'].extend([t,  t])
                    elif (top < btm):
                        invalid_data_found += 1
                if invalid_data_found == len(total_delay):
                    eye_closed.append(s)
                
            if len(eye_closed) == len(total_sets):
                # print("CH{} PHY{} CS{} BIT{} S{} {} {} {}".format( e.ch, e.phy, e.cs, e.bit, s, prm, set(_data_top[s]['VREF']), set(_data_btm[s]['VREF'])))
                data_dict['PRM'].extend([prm]*2)
                data_dict['CH'].extend([e.ch]*2)
                data_dict['PHY'].extend([e.phy]*2)
                data_dict['CS'].extend([e.cs]*2)
                data_dict['DB'].extend([db]*2)
                data_dict['NIB'].extend([nb]*2)
                data_dict['DQ'].extend([dq]*2)
                data_dict['BIT'].extend([e.bit]*2)
                data_dict['ERROR'].extend([f'ERROR EYE CLOSED DQ{dq}']*2)
                data_dict['PRE_LAUNCH'].extend([mr40]*2)
                data_dict['VREF'].extend([np.nan, np.nan] )
                data_dict['DELAY'].extend([np.nan, np.nan])
        df = pd.DataFrame(data_dict)
        if not df.empty:
            df['RawFile']   = self.rawfile
            df['MR40']      = df.apply(lambda x:  self.mr40_data[f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"] if ('RD' in x.PRM) else 0, axis = 1)
            df['MR40_EDGE'] = df.apply(lambda x : (self.mr40_stat[f"{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"]['edge']) if ('RD' in x.PRM) else 0, axis = 1)
            df['DELAY']     = df.apply(lambda x : (x.DELAY+x.MR40_EDGE) if (x.PRE_LAUNCH==0 and ('RD' in x.PRM)) else x.DELAY, axis = 1)
            # self.identify_mr40(df)
            # df['Vref_Center']  = df.apply(lambda x : self.read_data[f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"]['vref']      if ('RD' in x.PRM) else self.write_data[f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"]['DRAMVREF'] , axis = 1)
            # df['Delay_Center'] = df.apply(lambda x : self.read_data[f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"]['pi'][x.PRM] if ('RD' in x.PRM) else 0 , axis = 1)
            df['Vref_Center']  = df.apply(lambda x : self.trained_data[x.PRM]['VREF'][f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"], axis = 1)
            df['Delay_Center'] = df.apply(lambda x : self.trained_data[x.PRM]['DELAY'][f"{x.CH}_{x.PHY}_{x.CS}_{x.BIT}"], axis = 1)
            df['Vref_Offset'] = df.VREF-df.Vref_Center
            df['PI_Offset'] = df.DELAY-df.Delay_Center
        return df

    def geteye(self, srlz_data):
        eyes = []
        count = 0
        cs = 0
        oddeven = ''
        self.mr40_stat = {}
        for prm in ['RD_odd', 'RD_even']:
            for ch in range(16):
                for phy in range(2):
                    for cs in range(4):
                        for bit in range(40):
                            self.mr40_stat[f"{prm}_{ch}_{phy}_{cs}_{bit}"] = {'edge':0}
        for content in srlz_data:
            content = content.strip()
            ## --------------------- GRAB CHANNEL PHY NUMBER --------------------------- #
            match = ch_phy_info.search(content)
            if match:
                ch, phy = match.groups()
            ## --------------------- GRAB READ ODD EVEN PHASE -------------------------- #
            match = self.roe_info.search(content)
            if match:
                oddeven = match.group(1).strip().lower()
                oddeven = '_'+oddeven
                continue
            ## --------------------- GRAB 2D EYE PRINT INFORMATION --------------------- #
            match = self.eye_param_hash.search(content)
            if match:
                prm, phase = match.groups()
                prm = prm.strip().upper()
                phase_search = self.rd_phase_info.search(phase)
                if phase_search:
                    oddeven = '_' + phase_search.group(1).strip().lower()
                continue
            ## --------------------- GRAB RANK DB DQ INFORMATION ----------------------- #
            match = self.rk_db_dq_info.search(content)
            if match:
                cs, db, dq = match.groups()
                bit = (int(db)*8) + int(dq)
                continue
            ## --------------------- GRAB RANK CH INFORMATION ----------------------- #
            match = self.rk_ch_info.search(content)
            if match:
                cs, ch = match.groups()
                bit =0
                continue
            ## --------------------- GRAB RANK INFORMATION ----------------------- #
            match = self.rk_info.search(content)
            if match:
                cs = match.group(1)
                continue
            ## --------------------- GRAB NIBBLE INFORMATION ----------------------- #
            match = self.nb_info.search(content)
            if match:
                nb = match.group(1)
                bit = int(nb)*4
                continue
            ## --------------------- GRAB CURRENT READ PIN INFORMATION ----------------- #
            match = self.r_chinfo.search(content)
            if match:
                prm, cs, db, nb, dq = match.groups()
                prm = prm.strip().upper()
                bit = (int(db)*8) + (int(nb)*4) + int(dq)
                continue
            ## --------------------- GRAB TX TRAIN RANK INFORMATION -------------------- #
            match = self.txswitchrank.search(content)
            if match:
                cs = match.group(1)
                continue
            ## --------------------- GRAB CURRENT WRITE PIN INFORMATION ---------------- #
            match = self.w_chinfo.search(content)
            if match:
                prm, _ch, db, dq = match.groups()
                prm = prm.strip().upper()
                oddeven = ''
                bit = (int(db)*8) + int(dq)            
                continue
            ## --------------------- GRAB TRAINED VALUE INFORMATION -------------------- #
            match = self.cntr_info.search(content)
            # if match and prm in ['RD', 'WR']:
            if match:
                dly_offset, dly_ctr, vref_ctr = match.groups()
                dly_ctr = int(dly_ctr)
                vref_ctr = int(vref_ctr)
                dly_offset = int(dly_offset)
                continue
            ## --------------------- GRAB READ BASE VALUE INFORMATION ------------------ #
            match = self.read_base.search(content)
            if match:
                lb, ub = match.groups()
                lb = int(lb)
                ub = int(ub)
                continue
            ## --------------------- GRAB RD WR EYE DATA ------------------------------- #
            match = self.data_cntr.search(content)
            if match and (prm in self._params):
                [ch, phy, cs, bit] = [int(i) for i in [ch, phy, cs, bit]]
                dir, data = match.groups()
                base = (lb if dir.upper() == 'LOWER' else ub) if prm=='RD' else 0
                if prm != 'RD': oddeven=''
                data_v = [int(i)+base for i in data.split()]
                data_t = [dly_offset+i for i in range(len(data_v))]
                # ch_phy_bit = f"{ch}_{phy}_{cs}_{bit}"
                # if ch_phy_bit == '0_0_0_0':
                    # print(ch_phy_bit, dir)
                    # print(', '.join([f"{i:>03}" for i in data_t]))
                    # print(', '.join([f"{i:>03}" for i in data_v]))
                self.construct_eye(prm, ch, phy, cs, bit, oddeven, dly_offset, dir, data_t, data_v)
                continue

    def calculate_1d(self, df):
        # df['Vref_Offset'] = df.apply(lambda x: int(x.VREF) - int(x.Vref_Center), axis = 1)
        # df['PI_Offset']   = df.apply(lambda x: int(x.DELAY) - int(x.Delay_Center), axis = 1)
        tbrl = {}
        prms = set(df.PRM)
        chs  = set(df.CH)
        phys = set(df.PHY)
        cs_s = set(df.CS)
        bits = set(df.BIT)
        for rf in set(df.RawFile):
            tbrl.update({rf:{}})
            for prm in prms:
                for c in chs:
                    for p in phys:
                        for r in cs_s:
                            for b in bits:
                                bit = f'{prm}_{c}_{p}_{r}_{b}'
                                tbrl[rf].update({bit:[]})
                                subdf = df[(df.RawFile==rf) & (df.PRM==prm) & (df.CH==c) & (df.PHY==p) & (df.CS==r) & (df.BIT==b)]                    
                                top, btm, lft, rgt = 999,999,999,999
                                if not subdf.empty:
                                    max_t = subdf.PI_Offset.max()
                                    min_t = subdf.PI_Offset.min()
                                    
                                    EW_l = subdf[subdf.Vref_Offset==0].PI_Offset.tolist()
                                    if len(EW_l)>0 :
                                        if 0 in EW_l:
                                            lft = rgt = 0
                                        else:
                                            rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset==0)].PI_Offset.tolist()
                                            rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                            lft = max(lft_list) if len(lft_list)>0 else min_t
                                    else:
                                        rgt_list = subdf[(subdf.PI_Offset>0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        lft_list = subdf[(subdf.PI_Offset<0)&(subdf.Vref_Offset<3)&(subdf.Vref_Offset>-3)].PI_Offset.tolist()
                                        rgt = min(rgt_list) if len(rgt_list)>0 else max_t
                                        lft = max(lft_list) if len(lft_list)>0 else min_t
                                        
                                    EH_l = subdf[subdf.PI_Offset==0].Vref_Offset.tolist()
                                    if len(EH_l)>0:
                                        if 0 in EH_l:
                                            top = btm = 0
                                        else:
                                            top = subdf[(subdf.PI_Offset==0)].Vref_Offset.max()
                                            btm = subdf[(subdf.PI_Offset==0)].Vref_Offset.min()
                                    else:
                                        max_v = subdf.Vref_Offset.max()
                                        min_v = subdf.Vref_Offset.min()
                                        top = max_v
                                        btm = min_v
                                else:
                                    top, btm, lft, rgt = 0,0,0,0
                                [top, btm, rgt, lft] = [(0 if np.isnan(i) else i) for i in [top, btm, rgt, lft]]
                                tbrl[rf].update({bit:[top, btm, rgt, lft]})
                                    
        df['Top'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][0]) , axis = 1)
        df['Btm'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][1]) , axis = 1)
        df['Rgt'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][2]) , axis = 1)
        df['Lft'] = df.apply(lambda x: int(tbrl[x.RawFile][f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][3]) , axis = 1)

    def picture_dump_ch(self, df0):
        col_code = cm.Set1 ## colour code
        for rf in set(df0.RawFile):
            df = df0[df0.RawFile==rf]
            phys = sorted(list(set(df.PHY)))
            chs  = sorted(list(set(df.CH)))
            css  = sorted(list(set(df.CS)))
            hspace = 0.95
            piclist = {c:[] for c in chs}
            for prm in set(df.PRM):
                bits = sorted(list(set(df[df.PRM==prm].BIT))) if prm in ['CS', 'QCA'] else [i for i in range(40)]
                nibs = list(set([int(i/4) for i in bits]))
                grids = len(phys)*len(css)*len(nibs)
                cols = len(nibs) # fix 10 columns
                rows = int(grids/cols)
                for ch in chs:
                    # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                    ax = [i for i in range(rows*cols)]
                    pyplot.figure(figsize = (cols*3, rows*3))
                    pyplot.figtext(0.5, 0.99, f"{prm} CH{ch} Eye Plots", fontsize=20, va='top', ha='center')
                    colours = col_code(np.linspace(0, 1, len(nibs)))
                    tlegend = [patches.Patch(color=c, label=f"dq{i}") for c,i in zip(colours, [0,1,2,3])]
                    for r in range(rows):
                        for c in range(cols):
                            i = r*(cols)+c
                            ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                    # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                    i = 0
                    for phy in phys:
                        for cs in css:
                            ch = int(ch)
                            phy = int(phy)
                            cs = int(cs)
                            if 'RD' in prm:
                                subset = df[(df.PRM==prm)]
                                xmin, xmax  = -127, 128
                                x_ticks = sorted([i for i in range(-127, 128, 20)]+[0])
                                x_labels = [str((i+127)%128) for i in x_ticks]
                                ymin = _round(df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.min() -10)
                                ymax = _round(df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.max() +10)
                                y_ticks = [i for i in range(int(ymin), int(ymax), int((ymax-ymin)/10))]
                            else:
                                subset = df[(df.PRM==prm) & (df.CS==cs)]
                                xmin, xmax = subset.DELAY.min()-10, subset.DELAY.max()+10
                                ymin, ymax = _round(subset.VREF.min()-10, 10),  _round(subset.VREF.max()+10, 10)
                                x_ticks = [i for i in range(int(xmin), int(xmax), 10)]
                                x_labels = [str(i) for i in x_ticks]
                                y_ticks = [i for i in range(int(ymin), int(ymax), int((ymax-ymin)/10))]
                            for bit in bits:
                                mr40edge = self.mr40_stat[f"{prm}_{ch}_{phy}_{cs}_{bit}"]['edge'] if ('RD' in prm) else 0
                                edge = mr40edge
                                pyplot.axes(ax[i])
                                db = bit//8
                                nib = (bit//4)%2
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.DB==db) & (df.NIB==nib)]
                                err_msg = '\n'.join([j for j in [i for i in set(subset.ERROR.to_list())] if j.strip()!=''])
                                pyplot.title(f'CH{ch} PHY{phy} CS{cs} DB{db} Nib{nib}', fontsize = 10)
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.BIT==bit)]
                                v_center = np.mean(subset.Vref_Center)
                                t_center = np.mean(subset.Delay_Center) - (edge)
                                pyplot.ylim(ymin, ymax); pyplot.yticks(y_ticks)
                                pyplot.xlim(xmin, xmax); pyplot.xticks(x_ticks, x_labels, rotation =90)
                                pyplot.axvline(0,        color='k',   linestyle = ':', alpha = 0.5, label = 'MR40=0')
                                pyplot.axhline(v_center, color='0.5', linestyle = ':', alpha = 0.3)
                                pyplot.axvline(t_center, color='0.5', linestyle = ':', alpha = 0.3)
                                ax[i].scatter(t_center, v_center, color=colours[bit%4], marker = '*', s = 30)
                                x_values = subset.DELAY - (edge)
                                y_values = subset.VREF
                                ax[i].text(xmin, ymin, err_msg, va='bottom', ha='left', color = 'r', fontsize = 10)
                                ax[i].scatter(x_values, y_values, color=colours[bit%4], s=20, alpha = 0.5, marker = '.')
                                if prm in ['QCA', 'CS']:
                                    i+=1
                                else:
                                    if (bit%4 ==3): 
                                        i+=1
                    pyplot.tight_layout()
                    pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                    pyplot.subplots_adjust(top = hspace, right = 0.95)
                    # show()
                    if self._mdtpath:
                        filename = os.path.basename(rf)
                        bn = filename.split('.')[0]
                        out_pic = os.path.join(self._mdtpath, f'{bn}_{prm}_CH{ch}.jpg')
                    else:
                        out_pic = os.path.splitext(rf)[0]+f'_{prm}_CH{ch}.jpg'
                    pyplot.savefig(out_pic)
                    #if 'RD' in prm: #only append pic list because wanted to looks at the odd even swapping gif
                    #    piclist[ch].append(out_pic)
                    pyplot.close()
            if self._gif:
                for ch, pictures in piclist.items():
                    if pictures==[]: continue
                    self.make_gif(pictures, rf, ch)

    def picture_dump(self, df0):
        col_code = cm.Set1 ## colour code
        for rf in set(df0.RawFile):
            df = df0[df0.RawFile==rf]
            phys = sorted(list(set(df.PHY)))
            chs  = sorted(list(set(df.CH)))
            css  = sorted(list(set(df.CS)))
            hspace = np.linspace(0.95, 0.98, 16)[len(chs)]
            
            piclist = []
            for prm in set(df.PRM):
                bits = sorted(list(set(df[df.PRM==prm].BIT))) if prm in ['CS', 'QCA'] else [i for i in range(40)]
                nibs = list(set([int(i/4) for i in bits]))
                grids = len(chs)*len(phys)*len(css)*len(nibs)
                cols = len(nibs) # fix 10 columns
                rows = int(grids/cols)
                # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                ax = [i for i in range(grids)]
                pyplot.figure(figsize = (cols*3, rows*3))
                pyplot.figtext(0.5, 0.99, f"{prm} Eye Plots", fontsize=20, va='top', ha='center')
                colours = col_code(np.linspace(0, 1, len(nibs)))
                tlegend = [patches.Patch(color=c, label=f"dq{i}") for c,i in zip(colours, [0,1,2,3])]
                for r in range(rows):
                    for c in range(cols):
                        i = r*(cols)+c
                        ax[i] = pyplot.subplot2grid((rows,cols), (r,c));
                # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                i = 0
                for ch in chs:
                    for phy in phys:
                        for cs in css:
                            if 'RD' in prm:
                                subset = df[(df.PRM==prm)]
                                xmin, xmax  = -127, 128
                                x_ticks = sorted([i for i in range(-127, 128, 20)]+[0])
                                x_labels = [str((i+127)%128) for i in x_ticks]
                                ymin = _round(df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.min() -10)
                                ymax = _round(df[((df.PRM=='RD_odd')|(df.PRM=='RD_even')) & (df.CS==cs)].VREF.max() +10)
                                y_ticks = [i for i in range(int(ymin), int(ymax), int((ymax-ymin)/10))]
                            else:
                                subset = df[(df.PRM==prm) & (df.CS==cs)]
                                xmin, xmax = subset.DELAY.min()-10, subset.DELAY.max()+10
                                ymin, ymax = _round(subset.VREF.min()-10, 10),  _round(subset.VREF.max()+10, 10)
                                x_ticks = [i for i in range(int(xmin), int(xmax), 10)]
                                x_labels = [str(i) for i in x_ticks]
                                y_ticks = [i for i in range(int(ymin), int(ymax), int((ymax-ymin)/10))]
                            for bit in bits:
                                mr40edge = self.mr40_stat[f"{prm}_{ch}_{phy}_{cs}_{bit}"]['edge'] if ('RD' in prm) else 0
                                edge = mr40edge
                                pyplot.axes(ax[i])
                                db = bit//8
                                nib = (bit//4)%2
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.DB==db) & (df.NIB==nib)]
                                err_msg = '\n'.join([j for j in [i for i in set(subset.ERROR.to_list())] if j.strip()!=''])
                                pyplot.title(f'CH{ch} PHY{phy} CS{cs} DB{db} Nib{nib}', fontsize = 10)
                                subset = df[(df.PRM==prm) & (df.CH==ch) & (df.CS==cs) & (df.PHY==phy) & (df.BIT==bit)]
                                v_center = np.mean(subset.Vref_Center)
                                t_center = np.mean(subset.Delay_Center) - (edge)
                                pyplot.ylim(ymin, ymax); pyplot.yticks(y_ticks)
                                pyplot.xlim(xmin, xmax); pyplot.xticks(x_ticks, x_labels, rotation =90)
                                pyplot.axvline(0,        color='k',   linestyle = ':', alpha = 0.5, label = 'MR40=0')
                                pyplot.axhline(v_center, color='0.5', linestyle = ':', alpha = 0.3)
                                pyplot.axvline(t_center, color='0.5', linestyle = ':', alpha = 0.3)
                                ax[i].text(xmin, ymin, err_msg, va='bottom', ha='left', color = 'r', fontsize = 10)
                                ax[i].scatter(t_center, v_center, color=colours[bit%4], marker = '*', s = 30)
                                x_values = subset.DELAY - (edge)
                                y_values = subset.VREF
                                ax[i].scatter(x_values, y_values, color=colours[bit%4], s=20, alpha = 0.5, marker = '.')
                                if prm in ['QCA', 'CS']:
                                    i+=1
                                else:
                                    if (bit%4 ==3): 
                                        i+=1
                # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                pyplot.tight_layout()
                pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                pyplot.subplots_adjust(top = hspace, right = 0.95)
                # show()
                if self._mdtpath:
                    filename = os.path.basename(rf)
                    bn = filename.split('.')[0]
                    out_pic = os.path.join(self._mdtpath, f'{bn}_{prm}.jpg')
                else:
                    out_pic = os.path.splitext(rf)[0]+f'_{prm}.jpg'
                pyplot.savefig(out_pic)
                #if 'RD' in prm: #only append pic list because wanted to looks at the odd even swapping gif
                #    piclist.append(out_pic)
                pyplot.close()
            if self._gif:
                print('Making GIF...')
                self.make_gif(piclist, rf)

    def make_gif(self, piclist, gifname, ch = None):
        frames = [Image.open(image) for image in piclist]
        frame_one = frames[0]
        if self._mdtpath:
            filename = os.path.basename(gifname)
            bn = filename.split('.')[0]
            if (ch == None):
                out_gif = os.path.join(self._mdtpath, f'{bn}_RD.gif')
            else:
                out_gif = os.path.join(self._mdtpath, f'{bn}_RD_CH{ch}.gif')      
        else:
            if (ch == None):
                out_gif = os.path.splitext(gifname)[0]+'_RD.gif'
            else:
                out_gif = os.path.splitext(gifname)[0]+f'_RD_CH{ch}.gif'
        frame_one.save(out_gif, format="GIF", append_images=frames,  save_all=True, duration=800, loop=1000)

    def main(self):
        if self._mdtpath:
            out_stat_csv = os.path.join(self._mdtpath, f"MDT_RW_Eye_STAT.csv")        
        else:               
            out_stat_csv = os.path.join(dirname, f"{basename}_RW_Eye_STAT.csv")       
        for f in self.files:
            try:
                base = os.path.splitext(os.path.basename(f))[0]
                dfstat = []
                self.df_list = []
                self.rawfile = f
                self.mr_data = MR(f)
                # self.mr10_data = mr_data.getmr('10')
                self.mr40_data = self.mr_data.getmr('40')
                srlz_data = serialize_data(f)
                self.get_rd_train(srlz_data)
                self.get_wr_train(srlz_data)
                self.get_train_data(srlz_data)
                self.geteye(srlz_data)
                self.df_list.append(self.make_df())
                df = pd.concat(self.df_list)
                if not(df.empty):
                    if self._stat:
                        eyecom = self.eyeCoM(df)
                        df['Delay_Center'] = df.apply(lambda x: int(eyecom[f'{x.PRM}_{x.CH}_{x.PHY}_{x.CS}_{x.BIT}'][0]) if (x.PRM=='WR') else x.Delay_Center, axis = 1)
                        self.calculate_1d(df)   
                        dfstat = df.drop_duplicates(subset = ["RawFile","PRM","PHY","CH","CS","BIT"])
                        dfstat = dfstat[["RawFile","PRM","PHY","CH","CS","DB","NIB","DQ","BIT","Vref_Center","Delay_Center","Top","Btm","Rgt","Lft"]]                        
                        dfstat = dfstat.copy()  # Create a copy of the DataFrame slice
                        # Get just the filenames
                        dfstat['Filename'] = dfstat['RawFile'].apply(lambda x: os.path.basename(x))
                        # Add the IOD column based on filename content
                        dfstat['IOD'] = dfstat['Filename'].apply(lambda x: 0 if 'iod0' in x else (1 if 'iod1' in x else None))
                        if os.path.exists(out_stat_csv):
                            dfstat.to_csv(out_stat_csv, mode="a", header=False, index = 0)
                        else:
                            dfstat.to_csv(out_stat_csv, mode="a", header=True, index = 0)
                    if self._mdtpath:
                        out_csv = os.path.join(self._mdtpath, f"{base}_PMU_Eye.csv")
                    else:
                        out_csv = os.path.join(dirname, f"{base}_PMU_Eye.csv")
                    df.to_csv(out_csv, mode="w", header=True, index = False)
                    if self._pic | self._gif | self._pch:
                        print('Generating PMU_EYE Pictures....')
                        if self._pch:
                            self.picture_dump_ch(df)
                        if self._pic or (len(set(df.CH))>1) or self._gif:
                            self.picture_dump(df)
            except:
                print("[PMU Eye]: Parssing error for file: ", f) 
            
        # sys.exit() ## JOHN
        
        

def _parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("log",                 help = "Path Contains Log or logfile", type = str)
    parser.add_argument("--param",      '-prm',help = "Parameters to extract",        nargs = '+', default = ['RD', 'WR', 'QCA', 'CS'])
    parser.add_argument("--stat",       '-s',  help = "Statistic Summary",            action='store_true')
    parser.add_argument("--picture",    '-p',  help = "Dump Picture",                 action='store_true')
    parser.add_argument("--pic_per_ch", '-pch',help = "Dump Picture Per Channel",     action='store_true')
    parser.add_argument("--gif",        '-g',  help = "Dump GIF Image",               action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
    file = _parse().log
    _pic = _parse().picture
    _pch = _parse().pic_per_ch
    _stat = _parse().stat
    _gif  = _parse().gif
    _params = [i.strip().upper() for i in _parse().param]
    if os.path.exists(file):
        if os.path.isfile(file):
            dirname  = os.path.dirname(file)
            files = [file]
        elif os.path.isdir(file):
            dirname  = file
            files = [os.path.join(dirname, i) for i in os.listdir(file) if i.endswith('.log')]
    else:
        sys.exit("File Not Exists!")
    basename = os.path.splitext(os.path.basename(file))[0]
    if len(_params)>0:
        pmueye = PMU_Eye(files,"").main()
    if 'RD' in _params:
        rd_scan = Rd_Eye_Scan(files,"").main()
    
    