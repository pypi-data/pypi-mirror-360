'''
Author: john.khor@amd.com
Desc: Eye plot for Non distructive Rx Scan
'''
import os, re, argparse
import pandas as pd
import numpy as np
# from pylab import *
from matplotlib import cm, pyplot
from matplotlib import patches

ch_phy_info = re.compile("CHANNEL: ([0-9]+),  PHY: ([0-9]+),  PHYINIT: ")
lane_info   = re.compile("BTFW:.*RDEYE Eye Scan\].*Rank = (\d+), Byte = (\d+), (.*?) Nibble, Lane = (\d+), Pi code start = ([0-9]+)")
start_info  = re.compile("BTFW:.*RDEYE Eye Scan\].*lane_sel = (\d+), Pi offset = ([0-9]+)")
# data_info   = re.compile("BTFW:.*RDEYE Eye Scan\].*Lane = (\d+), Vref[High|Low].*= ([0-9]+)", re.I)

data_info = re.compile("BTFW:.*Rank = (\d+), Byte = (\d+), lane_sel = (\d+), Lane = (\d+), Vref(.*?) = ([0-9]+)", re.I)

'''
//Training lanes mapping:
//TrainSel =0 : tl0=lwr_ln3(3), tl1=lwr_ln1(1), tl2=upr_ln2(6), tl3=upr_ln3(7)
//TrainSel =1 : tl0=lwr_ln0(0), tl1=lwr_ln2(2), tl2=upr_ln0(4), tl3=upr_ln1(5)

const int  tl_lwr[2][2] = {{1,3},      {0,2}};
const int  tl_upr[2][2] = {{2,3},      {0,1}};
'''


def _parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("datafile", help = "Path Contains Log Data", type = str)
    return parser.parse_args()

def serialize_data(log):
    chlogs = {i:[] for i in range(16)}
    with open(log, 'r') as ifh:
        for line in ifh.readlines():
            line = line.strip()
            match = ch_phy_info.search(line)
            if match:
                ch, phy = match.groups()
                chlogs[int(ch)].append(f"{line}")
    output = []
    for k, v in chlogs.items():
        for l in v:
            output.append(l)
    return output

class Temp():
    hdr = ''
    ch  = None
    phy = None
    rk  = None
    db  = None
    ln  = None
    pi  = None
    lnsel = None
    

class Datas():
    def __init__(self, h, ch, phy, rk, db, ln, pi):
        self.hdr = h
        self.ch  = ch
        self.phy = phy
        self.rk  = rk
        self.db  = db
        self.ln  = ln
        self.pi_start = pi
        self.data = []
    def add_data(self, d):
        self.data.append(d)
        



def get_data_frame(datas, rawfile):
    data_struct = {'RawFile':[],\
                   'Stage':[],\
                   'CH':[],\
                   'PHY':[],\
                   'Rank':[],\
                   'DB':[],\
                   'LANE':[],\
                   'Start_PI':[],\
                   'PI_OFFSET':[],\
                   'VREF_OFFSET':[]
                   }
    for d in datas:
        for t,v in d.data:
            data_struct['RawFile'].append(os.path.basename(rawfile))
            data_struct['Stage'].append(d.hdr)
            data_struct['CH'].append(d.ch)
            data_struct['PHY'].append(d.phy)
            data_struct['Rank'].append(d.rk)
            data_struct['DB'].append(d.db)
            data_struct['LANE'].append(d.ln)
            data_struct['Start_PI'].append(d.pi_start)
            data_struct['PI_OFFSET'].append(t)
            data_struct['VREF_OFFSET'].append(v)
    return pd.DataFrame(data_struct)


def picture_dump(df, out_pic_path, basename):
    print('Generating Pictures....')
    col_code = cm.get_cmap('jet')  ## colour code
    rflist = list(set(df.RawFile))
    db_s = sorted(list(set(df.DB)))
    lane = sorted(list(set(df.LANE)))
    phys = sorted(list(set(df.PHY)))
    chs  = sorted(list(set(df.CH)))
    grids = len(db_s)*len(lane)
    cols = 8 # fix 8 columns
    rows = int(grids/cols)
    hspace = np.linspace(0.95, 0.98, 16)[len(chs)]
    for stg in set(df.Stage):
        for ch in chs:
            for phy in phys:
                subset = df[(df.CH==ch) & (df.PHY==phy)]
                xmin, xmax = subset.PI_OFFSET.min()-5, subset.PI_OFFSET.max()+5
                ymin, ymax = subset.VREF_OFFSET.min()-5,  subset.VREF_OFFSET.max()+5
                # ------------------------------INITIALIZE GRAPH START ---------------------------------------- #
                ax = [i for i in range(rows*cols)]
                pyplot.figure(figsize = (cols*3, rows*3))
                pyplot.figtext(0.5, 0.99, f"RD Eye Scan", fontsize=20, va='top', ha='center')
                colours = col_code(np.linspace(0, 1, len(rflist)))
                tlegend = [patches.Patch(color=c, label=f"{i}") for c,i in zip(colours, rflist)]
                for r in range(rows):
                    for c in range(cols):
                        i = r*(cols)+c
                        ax[i] = pyplot.subplot2grid((rows,cols), (r,c))
                # ------------------------------INITIALIZE GRAPH END  ----------------------------------------- #
                # ------------------------------ITERATE GRAPH CONSTRUCTION START ------------------------------ #
                i = 0
                for db in db_s:
                    for ln in lane:
                        pyplot.axes(ax[i])
                        pyplot.title(f'DB{db} Ln{ln}', fontsize = 12)
                        for rf_i, rf in enumerate(rflist):
                            subset = df[(df.Stage==stg) & (df.CH==ch) & (df.PHY==phy) & (df.DB==db) & (df.LANE==ln) & (df.RawFile==rf)]
                            pyplot.ylim(ymin, ymax); yticks(np.arange(ymin, ymax, int((ymax-ymin)/10)))
                            pyplot.xlim(xmin, xmax); xticks(np.arange(xmin, xmax, int((xmax-xmin)/10)))
                            pyplot.axhline(0, color='0.5', linestyle = ':', alpha = 0.5)
                            pyplot.axvline(0, color='0.5', linestyle = ':', alpha = 0.5)
                            ax[i].scatter(subset.PI_OFFSET, subset.VREF_OFFSET, color=colours[rf_i], s=20, alpha = 0.8, marker = '.')
                        i+=1
                # ------------------------------ITERATE GRAPH CONSTRUCTION END ------------------------------- #
                pyplot.tight_layout()
                pyplot.figlegend(handles=tlegend, loc='upper right', bbox_to_anchor=(0.99, 0.99))
                pyplot.subplots_adjust(top = hspace, right = 0.95)
                # show()
                if out_pic_path:
                    out_pic = os.path.join(out_pic_path, f"{basename}_ReadEyeScan_{stg}_CH{int(ch)}_PHY{int(phy)}.jpg")
                else:
                    out_pic = os.path.join(dirname, f"{basename}_ReadEyeScan_{stg}_CH{int(ch)}_PHY{int(phy)}.jpg")
                savefig(out_pic)



        
def twos_comp(val, bits=8):
    if (val & (1 << (bits - 1))) != 0: 
        val = val - (1 << bits)
    return val 

def process(log):
    header = re.compile("BTFW: \[RDEYE Eye\] (.*)")
    lines = serialize_data(log)
    datas = []
    temp = Temp()
    ln_sel_ref = {0 : [3,1,6,7], 1 : [0,2,4,5]} 
    # temp = {}
    for line in lines:
        line = line.strip()
        match = header.search(line)
        if match:
            temp.hdr = match.group(1)
            continue
        match = ch_phy_info.search(line)
        if match:
            ch, phy = match.groups()
            temp.ch = int(ch)
            temp.phy = int(phy)
        # ------------- INITIAL VALUE SEARCH START ---------------- #
        match = lane_info.search(line)
        if match:
            rk, db, nb, ln, pi = match.groups()
            rk = int(rk)
            db = int(db)
            nbref = {'lower':0, 'upper':4}
            nb = nbref[nb.strip().lower()]
            ln = nb+int(ln)
            pi = twos_comp(int(pi) & 0xFF)
            temp.rk = rk
            temp.db = db
            temp.nb = nb
            temp.ln = ln
            temp.pi = pi
            datas.append(Datas(temp.hdr, temp.ch, temp.phy, rk, db, ln, pi))
            # print(f"CH{ch} PHY{phy} RK{rk} DB{db} Ln{temp.ln}")
            continue
        # ------------- INITIAL VALUE SEARCH END ------------------ #
        match = start_info.search(line)
        if match:
            ln_sel, pi_off = match.groups()
            temp.currpi = twos_comp(int(pi_off) & 0xFF)
            continue
        match = data_info.search(line)
        if match:
            rk, db, ln_sel, ln, dir, _data = match.groups()
            rk = int(rk)
            db = int(db)
            ln = int(ln)
            ln_sel = int(ln_sel)
            ln = ln_sel_ref[ln_sel][ln]
            dir = dir.strip().lower()
            _data = twos_comp(int(_data) & 0x1FF, 9)
            
            # print(f"CH{temp.ch} PHY{temp.phy} RK{rk} DB{d.db} Ln{d.ln}")
            for d in datas:
                if (d.hdr==temp.hdr) and (d.ch==temp.ch) and (d.phy==temp.phy) and (d.rk==rk) and (d.db==db) and (d.ln==ln):
                    d.add_data((temp.currpi, _data))
                    break;
    return get_data_frame(datas, log)

def get_rd_eye_scan(inputlog, mdt_path):    
    dflist = []
    rawfile = ''
    if len(inputlog)> 0:
        for file in inputlog:
            try:
                dflist = []
                rawfile = file
                base = os.path.splitext(os.path.basename(file))[0]
                out_csv = os.path.join(mdt_path, f"{base}_ReadEyeScan.csv")
                dflist.append(process(file))
                df = pd.concat(dflist)
                df.to_csv(out_csv, index = 0)
                picture_dump(df, mdt_path, base)
            except:
                print("[Rd Wr Eye]: Parssing error for file: ", file) 
  

if __name__ == "__main__":
    file = _parse().datafile
    rawfile = file
    files = []
    if os.path.exists(file):
        if os.path.isfile(file):
            dirname = os.path.dirname(file)
            files = [file]
        if os.path.isdir(file):
            dirname = file
            files = [os.path.join(dirname,i) for i in os.listdir(file) if i.endswith('.parsed.log')]
    else:
        sys.exit("File Not Exists!")
    # newdir, ext = os.path.splitext(os.path.abspath(file))
    
    basename = os.path.splitext(os.path.basename(file))[0]
    out_csv = os.path.join(dirname, f"{basename}_ReadEyeScan.csv")
    dflist = []
    for f in files:
        print(f"Processing {f}")
        rawfile = f
        dflist.append(process(f))
    df = pd.concat(dflist)
    df.to_csv(out_csv, index = 0)
    picture_dump(df, "", basename)
    