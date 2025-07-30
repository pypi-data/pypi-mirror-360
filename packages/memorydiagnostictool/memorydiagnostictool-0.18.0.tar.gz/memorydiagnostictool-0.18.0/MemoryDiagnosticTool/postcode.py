import os
import sys
import argparse
import pandas as pd
import re
from pathlib import Path

esid_steps = (
            "POST_CODE_ORCHESTRATOR",    # 0x00 Orchestrator
            "POST_CODE_GEN_ENV_INIT",    # 0x01 GenEnvInit
            "POST_CODE_GEN_ESID_COMPLETE",    # 0x02 GenEsidComplete
            "POST_CODE_UMC_PROGRAMMING",    # 0x03 UmcProgramming
            "POST_CODE_MEM_DETECTION",    # 0x04 MemDetection
            "POST_CODE_MPIO_INIT_AFTER_TRNG",    # 0x05 MpioInitAfterTraining
            "POST_CODE_DF_AFTER_TRAINING",    # 0x06 DfAfterTraining
            "POST_CODE_DF_FSDL_INIT",    # 0x07 DfFsdlInit
            "POST_CODE_DF_FSDL_ADDR_MAP_INIT",    # 0x08 DfFsdlAddressMapInit
            "POST_CODE_MEM_BEFORE_APOB",    # 0x09 MemBeforeApob
            "POST_CODE_GNB_AFTER_TRAINING",   # 0x0A GnbAfterTraining
            "POST_CODE_MEM_BEFORE_TRAINING",   # 0x0B MemBeforeTraining
            "POST_CODE_MEM_TRAINING",   # 0x0C MemTraining
            "POST_CODE_MEM_AFTER_TRAINING",   # 0x0D MemAfterTraining
            "POST_CODE_MEM_FEATURE_INIT",   # 0x0E MemFeatureInit
            "POST_CODE_CPU_OPTIMIZE",   # 0x0F CpuOptimize
            "POST_CODE_MEM_EMULATION",   # 0x10 MemEmulation
            "POST_CODE_DF_BEFORE_TRAINING",   # 0x11 DfBeforeTraining
            "POST_CODE_S3_INIT",   # 0x12 S3Init
            "POST_CODE_S3_DRAM_READY",   # 0x13 S3DramReady
            "POST_CODE_GEN_S3_COMPLETE",   # 0x14 GenS3Complete
            "POST_CODE_MEM_DIAGNOSTIC",   # 0x15 MemDiagnostic
            "POST_CODE_CPU_BEFORE_TRAINING",   # 0x16 CpuBeforeTraining
)

postcodes = {
    #Generic events group
    0x000: "TP_ESID_SUCCESS",  # Generic SUCCESS signal
    0x001: "TP_ESID_START",  # Generic BEGIN signal (processes or code sections)
    0xDB6: "TP_ESID_GDB_DEBUG_LOGPOINT",  # GDB hook reached indication
    0x0FF: "TP_ESID_END",  # Generic END signal (processes or code sections)

    #Specific Progress event group
    0xA01: "TP_ESID_DRVR_INIT_START",  # eSID driver loaded - Init procedure BEGIN signal (common)
    0xA02: "TP_ESID_DRVR_INIT_END",  # eSID driver loaded - Init procedure END signal (common)
    0xA03: "TP_ESID_DRVR_DISPATCH_START",  # eSID driver dispatcher execution START (common)
    0xA04: "TP_ESID_DRVR_DISPATCH_END",  # eSID driver dispatcher execution END (common)
    0xA05: "TP_ESID_DRVR_START",  # eSID driver main body execution - BEGIN (common)
    0xA06: "TP_ESID_DRVR_END",  # eSID driver main body execution - END (common)
    0xA07: "TP_ESID_DRVR_TERMINATE",  # eSID driver received terminate signal from tOS (common)
    0xA08: "TP_ESID_DRVR_FREE_RESOURCES",  # eSID driver received Free resources signal from tOS (common)
    0xA0A: "TP_ESID_CPU_OPTIMIZED_BOOT_START",  # CPU Initialize Optimized Boot Start
    0xA0B: "TP_ESID_CPU_OPTIMIZED_BOOT_END",  # CPU Initialize Optimized Boot End
    0xA0C: "TP_ESID_CPU_INIT_AFTER_TRAINING_START",  # CPU Initialize After Training Start
    0xA0D: "TP_ESID_CPU_INIT_AFTER_TRAINING_END",  # CPU Initialize After Training End
    0xA0E: "TP_ESID_CCX_DOWN_CORE_ENTRY",  # CPU DownCore Initialize Internal Start
    0xA0F: "TP_ESID_CCX_DOWN_CORE_EXIT",  # CPU DownCore Initialize Internal End
    0xA10: "TP_ESID_MEM_AMD_MEM_AUTO_PHASE_3",  # Memory Before Training procedure Start
    0xA11: "TP_ESID_MEM_END",  # Memory Before Training procedure End
    0xA12: "TP_ESID_MEM_FEATURE_INIT_END",  # Memory UMC Feature Initialization End
    0xA13: "TP_ESID_MEM_TEST_START",  # Memory Test procedure Begin
    0xA14: "TP_ESID_MEM_DDR_TRAINING_START",  # Memory Training procedure Start
    0xA15: "TP_ESID_MEM_DDR_TRAINING_END",  # Memory Training procedure End
    0xA16: "TP_ESID_MEM_DDR_TRAINING_PSTATE_START",  # Memory Training - Switch PSTATE Start
    0xA17: "TP_ESID_MEM_DDR_TRAINING_PSTATE_END",  # Memory Training - Switch PSTATE End
    0xA18: "TP_ESID_MEM_PMU_FAILED",  # Memory Training - PMU Training fail
    0xA19: "TP_ESID_MEM_PMU_BEFORE_FW_LOAD",  # PMU Firmware load Start
    0xA1A: "TP_ESID_MEM_PMU_AFTER_FW_LOAD",  # PMU Firmware load End
    0xA1B: "TP_ESID_PROGRAM_UMC_KEYS",  # Program UMC Keys signal
    0xA1C: "TP_ESID_MEM_POST_PACKAGE_REPAIR",  # Boot time PPR start
    0xA1D: "TP_ESID_MEM_HEAL_REPAIR",  # PMU BIST repair triggered
    0xA1E: "TP_ESID_MEM_MBIST_INTERFACE_TEST",  # MBIST Interface Test Mode
    0xA1F: "TP_ESID_MEM_MBIST_DATA_EYE_TEST",  # MBIST Data eye Test Start
    0xA20: "TP_ESID_MEM_MBIST_DEFAULT_RRW_TEST",  # MBIST disabled - Default RRW test
    0xA21: "TP_ESID_MEM_HEAL_START",  # PMU BIST - Procedure start
    0xA22: "TP_ESID_MEM_HEAL_READ",  # PMU BIST - Read operation
    0xA23: "TP_ESID_MEM_HEAL_WRITE",  # PMU BIST - Write operation
    0xA24: "TP_ESID_MEM_HEAL_END",  # PMU BIST - Procedure end
    0xA25: "TP_ESID_MEM_DMI",  # DMI information structure create start
    0xA26: "TP_ESID_DF_AFTER_TRAINING_END",  # DF After training - Procedure end
    0xA27: "TP_ESID_DF_FSDL_ADDR_MAP_END",  # DF FSDL Address Map Init - Procedure end
    0xA28: "TP_ESID_GEN_ENV_INIT_END",  # General environment initialization - Procedure end
    0xA29: "TP_ESID_GEN_COMPLETE_APOB",  # APOB creation start
    0xA2A: "TP_ESID_GEN_COMPLETE_END",  # General eSID complete - procedure end
    0xA2B: "TP_ESID_DF_AFTER_TRAINING_INIT",  # DF After training Initialization - Procedure start
    0xA2C: "TP_ESID_EMU_TABLE_LOADED",  # Emulation Execution table loaded
    0xA2D: "TP_ESID_HW_TABLE_LOADED",  # Hardware Execution table loaded
    0xA2E: "TP_ESID_S3_TABLE_LOADED",  # S3 Resume Execution table loaded
    0xA2F: "TP_ESID_MEM_CSR_TABLE_LOADED",  # Memory Context Save Restore Execution table loaded
    0xA30: "TP_ESID_FINISH_EXECUTION",  # eSID Orchestrator execution finish
    0xA31: "TP_ESID_MEM_MOR_EXECUTED",  # Memory MOR execution end
    0xA32: "TP_ESID_MEM_MOR_START",  # Memory MOR execution begin
    0xA33: "TP_ESID_MEM_MOR_END",  # Memory MOR - procedure end
    0xA34: "TP_ESID_S3DRAM_APOB_INIT",  # MCR Copy APOB to DRAM - procedure start
    0xA35: "TP_ESID_APOB_CREATION_SUCCESSFUL",  # APOB successfully created

    0xBE0: "TP_BEFORE_GET_IDS_DATA",   # Before IDS calls out to get IDS data
    0xBE1: "TP_AFTER_GET_IDS_DATA",   # After IDS calls out to get IDS data

    #Generic error group
    0xE00: "TP_ESID_ERROR",  # Generic eSID error

    #Specific error group
    0xF00: "TP_ESID_ERR_SPI_LOAD",    # eSID driver SPI load error
    0xF01: "TP_ESID_ERR_SPI_UNLOAD",    # eSID driver SPI unload error
    0xF02: "TP_ESID_ERR_IPC_CALL_FAIL",    # eSID driver run failed - eSIO execution
    0xF03: "TP_ESID_ERR_UNRECOGNIZED_CMD",    # Reception of unrecognized command - Dispatcher
    0xF04: "TP_ESID_ERR_APCB_SYNC",    # APCB Board Mask sync failed
    0xF05: "TP_ESID_ERR_CORE_MAP",    # Core map retrieval from SMU failed
    0xF06: "TP_ESID_ERR_AGESA_MEMORY_TEST",    # Memory Test failed
    0xF07: "TP_ESID_ERR_PMU_LOADING",    # PMU Firmware load failure
    0xF08: "TP_ESID_ERR_LOCATE_MSG_BLOCK",    # PMU SRAM load Message Block into DMEM failure
    0xF09: "TP_ESID_ERR_PMU_TRAINING",    # PMU Training Failure
    0xF0A: "TP_ESID_ERR_NO_CAD_BUS_TABLE",    # CAD Bus table entry invalid
    0xF0B: "TP_ESID_ERR_DIMM_CONFIG",    # Invalid DIMM configuration
    0xF0C: "TP_ESID_ERR_RDIMM_LRDIMM_MIX",    # Invalid Mem config - RDIMM and LRDIMM mix
    0xF0D: "TP_ESID_ERR_X4_X8_MIX",    # Invalid Mem config - x4 and x8 mix
    0xF0E: "TP_ESID_ERR_3DS_MIX",    # Invalid Mem config - 3DS and non-3DS mix
    0xF0F: "TP_ESID_ERR_ECC_SIZE_MIX",    # Invalid Mem config - ECC size mix
    0xF10: "TP_ESID_ERR_MEMORY_ON_INVALID_CH",    # Invalid Mem config - Memory found on invalid channel
    0xF11: "TP_ESID_ERR_DIMM_MODULE_MIX",    # Invalid Mem config - Incompatible Module mix
    0xF12: "TP_ESID_ERR_PMIC_ERROR",    # Memory - PMIC error detected
    0xF13: "TP_ESID_ERR_SPD_INVALID",    # Memory - SPD Mismatched density value
    0xF14: "TP_ESID_ERR_SPD_CRC",    # Memory - SPD CRC Verification failure
    0xF15: "TP_ESID_ERR_NO_PPR_TABLE",    # Memory - No PPR table found
    0xF16: "TP_ESID_ERR_NO_PPR_HEAP_ALLOC",    # Memory - PPR table allocation failed
    0xF17: "TP_ESID_ERR_MBIST",    # Memory - MBIST RRW failure
    0xF18: "TP_ESID_ERR_RRW",    # Memory - MBIST RRW Sync failure
    0xF19: "TP_ESID_ERR_MBIST_HEAP",    # Memory - MBIST Results not found
    0xF1A: "TP_ESID_ERR_SERIAL_PORT_CONFIG",    # Serial port configuration failure
    0xF1B: "TP_ESID_ERR_DIMM_W_SPECIFIC_VENDOR_RCD_VERSION",    # Memory - DIMM with Montage RCD Revision B1
    0xF1C: "TP_ESID_ERR_DIMM_W_SPECIFIC_PMIC_VENDOR_VERSION",    # Memory - DIMM with TI PMIC Revision 1.1 (XTPS)
    0xF1D: "TP_ESID_ERR_NO_DIMM_ON_ANY_CHANNEL_IN_SYSTEM",    # Memory - No installed memory detected
    0xF1E: "TP_ESID_ERR_GLOBAL_MAILBOX_INVALID",    # eSID Global mailbox failure
    0xF1F: "TP_ESID_ERR_INIT_WAITEVENT_FAIL",    # eSID generic sync event creation failure
    0xF20: "TP_ESID_ERR_INCOMPATIBLE_OPN",    # Incompatible OPN detected
    0xF21: "TP_ESID_ERR_UNSOPPORTED_DDR",    # Memory - Unsupported DDR type detected
    0xF22: "TP_ESID_ERR_INVALID_HEAP",    # eSID Shared heap initialization failure
    0xF23: "TP_ESID_ERR_OUT_OF_MEM",    # eSID Shared heap out of free space
    0xF24: "TP_ESID_ERR_MUTEX_BUFFER",    # eSID 2P Mutex buffer allocation failure
    0xF25: "TP_ESID_ERR_MUTEX_CREATION",    # eSID 2P Mutex object creation failure
    0xF26: "TP_ESID_ERR_PRESIL_NOT_FOUND",    # eSID PreSilicon control struct not found
    0xF27: "TP_ESID_ERR_ABSENCE_AC_POWER_OR_WLAN_APCB_DATA",    # MPM AC or WLAN GPIO declare missing
    0xF28: "TP_ESID_ERR_OUT_OF_RESOURCES",    # eSID load failure, SRAM shortage
    0xF29: "TP_ESID_ERR_APCB_FATAL_CHECKSUM",    # APCB checksum failure from RO storage
    0xF2A: "TP_ESID_ERR_APCB_RECOVERABLE_CHECKSUM",    # APCB checksum failure from RO storage, no recovery
    0xF2B: "TP_ESID_ERR_REMOTE_SRAM_MAP",    # eSID remote shared heap mapping failure
    0xF2C: "TP_ESID_ERR_CRU_REGS_INVALID",    # eSID CRU public registers mapping failure
    0xF2D: "TP_ESID_ERR_CONSOLE_OUT_INIT",    # eSID Debug Print console out init failure
    0xF2E: "TP_ESID_ERR_NO_MEMORY_AVAILABLE_IN_SYSTEM",    # Memory - Training failure, no Memory in system
    0XF2F: "TP_ESID_ERROR_APCB_BOARD_ID",    # APCB Board mask not found
    0xF30: "TP_ESID_BIST_FAILURE",    # Memory BIST test failed
    0xFFF: "TP_ESID_ERR_ASSERT" # eSID ASSERT signal
}



def checking_postcode(pc):

    value_start = 0
    value_bits  = 12 # 11:0 
    value_mask  = sum(1<<x for x in range(value_bits))
    pc_val = (pc >> value_start) & value_mask

    type_start = value_start + value_bits  
    type_bits  = 4 # 15:12 TESTPOINT, DATA, or ADDRESS
    type_mask  = sum(1<<x for x in range(type_bits))
    esid_type = (pc >> type_start) & type_mask    

    esid_num_start = type_start + type_bits
    esid_num_bits  = 5  # 21:16 Current eSID number
    esid_mask      = sum(1<<x for x in range(esid_num_bits))
    esid_num = (pc >> esid_num_start) & esid_mask

    node_id_start = esid_num_start + esid_num_bits
    node_id_bits  = 3  # 23:22 Node that sent this
    node_id_mask  = sum(1<<x for x in range(node_id_bits))
    node_id = (pc >> node_id_start) & node_id_mask

    esid_indicator_id_start = node_id_start + node_id_bits
    esid_indicator_bits  = 8  # 31:24 - 0xE5
    esid_indicator_mask  = sum(1<<x for x in range(esid_indicator_bits))
    if ((pc >> esid_indicator_id_start) & esid_indicator_mask) != 0xE5:
        sys.exit("ESID postcodes start with 0xE5")

    #POST_CODE_GENERAL_NUMBER            = 0xFF, # To be used on libraries for debugging purposes
    if esid_num >= len(esid_steps):
        sys.exit("esid step number not in current list")
    esid_step = esid_steps[esid_num]
  
    esid_command_type = (
            "NA",
            "TEST_POINT_OUT",
            "DATA_OUT",
            "ADDRESS_OUT",
    )[esid_type]
    if pc_val not in postcodes.keys():
        sys.exit("Post Code not in known list")
        
    postcode = postcodes[pc_val]
    postcode_description= f"Post/Error Code: {postcode}, PC: {pc:#010x} \nNode ID: {node_id}, ESID Step:{esid_command_type}, Command Type: {esid_command_type}"

    return postcode_description

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

def get_postcode(log):
    postcode_pattern = re.compile(r"\[TP:([0-9a-fA-F]+)\]")
    for line in log:
        match = postcode_pattern.search(line)    
        if match:
           last_postcode = match.groups()[0]

    postcode = checking_postcode(int(last_postcode,16))

    return postcode   
        

def extract_postcode(file_name, system_name, bios, output_file):
    
    with open(file_name, 'r') as file:
        # Read all lines from the file
        input_text = file.readlines()
    iod0, iod1 = split_IOD0_IOD1(input_text)

    iod0postcode = get_postcode(iod0)
    iod1postcode = get_postcode(iod1)

    if(os.path.splitext(file_name)[1] == ".log"):
        fl = Path(file_name).name
        df_am = {"Log File":[fl],"System":[system_name],"BIOS":[bios],"IOD0 Postcode":[iod0postcode],"IOD1 Postcode":[iod1postcode]}
        df = pd.DataFrame(df_am)
        df.to_csv(output_file, mode='a', header=False, index=False)
    return



def get_postcodefile(inputlog, postcode_output):
    header_data = {"Log File":[],"System":[],"BIOS":[],"IOD0 Postcode":[],"IOD1 Postcode":[]}
    df =pd.DataFrame(header_data)
    df.to_csv(postcode_output, mode="w", header=True, index=False)
    
    for file in inputlog:
        base = os.path.splitext(os.path.basename(file))[0]
        bios, hostname = get_bios_hostname(base)
        try:
            extract_postcode(file, hostname, bios, postcode_output)
        except:
            print("Postcode: Fail to process file: ",file)
    print("Postcode check results are saved in the file: ", postcode_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode ESID postcode')
    parser.add_argument('postcode', default=None, help='Hex value of ESID postcode')
    args = parser.parse_args()

    pc = int(args.postcode, 16)
    pc_result = checking_postcode(pc)
    print(pc_result)
    

