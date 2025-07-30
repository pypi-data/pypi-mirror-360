import os
import click
import re


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


def resturcture_text(input_lines):

    # To store the new structured lines
    structured_lines = []

    # Regular expression to match a "CHANNEL" entry
    channel_pattern = re.compile(r"(CHANNEL: \d+,  PHY: \d+,  PHYINIT:.*?)(?=CHANNEL:|\Z)", re.DOTALL)

    for line in input_lines:
        matches = channel_pattern.findall(line)
        if (matches):
           for match in matches:
                newline= match.strip()
                # Split the match into lines
                structured_lines.append(newline+"\n")
        else:
           structured_lines.append(line)
    
    return structured_lines

def sort_text_by_channel_phy(input_list):
    def get_channel_phy(line):
        # Check if the line contains both 'CHANNEL:' and 'PHY:' to be valid
        if 'CHANNEL:' in line and 'PHY:' in line:
            try:
                # Extract channel and PHY values
                channel = int(line.split(',')[0].split(':')[1].strip())
                phy = int(line.split(',')[1].split(':')[1].strip())
                return (channel, phy)
            except (IndexError, ValueError):
                return None  # Return None if the line format is wrong
        return None  # Return None if the line doesn't contain 'CHANNEL:' and 'PHY:'

    # Separate the lines into valid and invalid ones
    valid_lines = []
    before_lines = []
    after_lines = []
    encountered_valid = False

    for line in input_list:
        if get_channel_phy(line) is None and not encountered_valid:
            # Collect invalid lines only until we encounter the first valid line
            before_lines.append(line)
        elif get_channel_phy(line) is None and encountered_valid:
            after_lines.append(line) 
        else :
            encountered_valid = True
            #count the number of channel in a line and split accordingly
            count = line.count("CHANNEL")
            if count==1:
                valid_lines.append(line)
            else:
                splitlines = line.split("CHANNEL")
                for item in splitlines:
                    if item:
                        valid_lines.append("CHANNEL"+item)
                        #print(f" {valid_lines}")

    # Sort only the valid lines
    sorted_valid_lines = sorted(valid_lines, key=get_channel_phy)
    
    sorted_lines = before_lines + sorted_valid_lines + after_lines

    # Combine sorted valid lines with the invalid lines (preserve the order of invalid lines)
    return sorted_lines, sorted_valid_lines

# Read the input text from a file
def read_and_sort_file(file_path):
    print(file_path)
    output_file_path = os.path.splitext(file_path)[0] + '_sorted' + os.path.splitext(file_path)[1]
    output_cropped_file_path = os.path.splitext(file_path)[0] + '_sorted_cropped' + os.path.splitext(file_path)[1]
    
    with open(file_path, 'r') as file:
        # Read all lines from the file
        input_text = file.readlines()
    
    iod0, iod1 = split_IOD0_IOD1(input_text)
    
    
    iod0_restructure = resturcture_text(iod0)
    iod1_restructure = resturcture_text(iod1)
    
    # Sort the lines by CHANNEL and PHY
    sorted_text0, sorted_cropped_text0 = sort_text_by_channel_phy(iod0_restructure)
    sorted_text1, sorted_cropped_text1 = sort_text_by_channel_phy(iod1_restructure)

    # Print out the sorted list
    with open(output_file_path, 'w') as output_file:
        output_file.writelines(sorted_text0)
        output_file.write("ESID_LOG_NODE1 log, Start >>>>>>>>>>\n")
        output_file.writelines(sorted_text1)
        output_file.write("ESID_LOG_NODE1 log, End <<<<<<<<<<\n")

    # Print out the sorted_cropped list
    with open(output_cropped_file_path, 'w') as output_file:
        output_file.writelines(sorted_cropped_text0)
        
        output_file.write("ESID_LOG_NODE1 log, Start >>>>>>>>>>\n")
        output_file.writelines(sorted_cropped_text1)
        output_file.write("ESID_LOG_NODE1 log, End <<<<<<<<<<\n")


@click.command()
@click.option('--parse_log', '-p', help=r"Log file to parse", required=True)
def wrapper(parse_log):
    read_and_sort_file(parse_log)

if __name__ == '__main__':
    wrapper()
