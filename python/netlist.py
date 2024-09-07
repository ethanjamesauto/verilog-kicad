# exec(open("C:/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test/verilog-kicad.py").read())
KICAD = True
VERBOSE = False

from tqdm import tqdm
import json
import glob
import os
import xml.etree.ElementTree as ET

footprint_path = '../pinouts/**/**/**.dig'
json_path = '../out.json'
top_level_module = 'shift_card'

if KICAD:
    import pcbnew as pb # type: ignore
    footprint_path = 'C:/Users/Ethan/Documents/Digital/lib/DIL Chips/**/**.dig'
    json_path = '//wsl$/Ubuntu/home/ethan/verilog-kicad/out.json'
    lib_path = 'C:/Program Files/KiCad/8.0/share/kicad/footprints/'
    board_path_in = 'C:/Users/Ethan/Desktop/modular_8bit_computer/base_card_for_verilog_kicad/smaller_card/smaller_card.kicad_pcb'
    board_path = 'C:/Users/Ethan/Desktop/modular_8bit_computer/base_card_for_verilog_kicad/smaller_card/smaller_card_out.kicad_pcb'
    board = pb.LoadBoard(board_path_in)



def get_footprint_name(ic_type, num_pins):
    if ic_type.startswith('28'):
        return 'DIP-%d_W15.24mm' % num_pins
    return 'DIP-%d_W7.62mm' % num_pins

# # of gates per 74 series ic (example '74AC04_6x1NOT' returns 6)
def gate_count(ic_type):
    return int(ic_type[ic_type.find('_')+1:ic_type.find('x')])

def gate_name_to_chip(ic_type):
    code = ic_type[ic_type.find('C')+1:ic_type.find('_')]
    return '74' + code

# list of all ics added to board
kicad_ic_list = []

# maps all kicad ICs to net names
kicad_netlist = {}

# global variables for add_gate_to_IC
gate_build = {} # stores the 74-series chips currently being built from individual gates. maps ic_type -> list of kicad footprints
gate_build_ctr = {} # maps ic_type -> # of gates currently used in the footprint being built (the one not completed yet)
gate_build_clk_net = {} # keep track of the current clock net for flip-flop ICs
gate_build_pins = {}

def add_gate_to_IC(ic_type, wires, i):
    added_new_IC = False
    # print(ic_type, wires)
    chip_name = gate_name_to_chip(ic_type)
    pinout = pinouts[chip_name]
    footprint = get_footprint_name(ic_type, sizes[chip_name])

    gate_list = gate_build[ic_type]
    chip_gate_cnt = gate_count(ic_type)

    if len(gate_list) == 0 or gate_build_ctr[ic_type] == chip_gate_cnt:
        if KICAD:
            m = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', footprint)
            board.Add(m)
            kicad_ic_list.append(m)
            ref_str = chip_name + '_g' + str(i)
            kicad_netlist[ref_str] = set()
            m.SetReference(ref_str)

            # Tie VCC and GND
            # print(pinout, netlist)
            m.Pads()[int(pinout['GND'])-1].SetNetCode(netlist[0].GetNetCode())
            m.Pads()[int(pinout['VCC'])-1].SetNetCode(netlist[1].GetNetCode())
            print('Added (synthesized): ' + chip_name)

        else:
            m = chip_name + ' ' + ic_type
        added_new_IC = True
        gate_list.append(m)
        gate_build_ctr[ic_type] = 1
        gate_build_pins[chip_name] = []
    else:
        m = gate_list[-1]
        gate_build_ctr[ic_type] += 1

    # rename gate wires to IC footprint pin names
    gate_num = gate_build_ctr[ic_type]
    for wire_name in wires:
        if chip_name == '74374' or chip_name == '7474' or chip_name == '74273':
            new_name = wire_name + str(gate_num - 1)
        elif chip_name == '74257':
            new_name = wire_name + str(gate_num)
        else:
            new_name = str(gate_num) + wire_name

        if wire_name == 'CLK' or wire_name == 'S':
            new_name = wire_name

        assert len(wires[wire_name]) == 1
        wire = int(wires[wire_name][0])
        pin_num = int(pinout[new_name])

        if wire_name == 'CLK':
            if added_new_IC:
                gate_build_clk_net[chip_name] = wire
            assert gate_build_clk_net[chip_name] == wire, 'Error: Placement failed - tried to add flip-flop to IC with existing clock net ' \
                + str(gate_build_clk_net[chip_name]) + ', new clock net is ' + str(wire)
        else:
            assert pin_num not in gate_build_pins[chip_name], 'Error: Placement failed - attempted to re-assign pin'

        if KICAD:
            m.Pads()[pin_num-1].SetNetCode(netlist[wire].GetNetCode())
            kicad_netlist[m.GetReference()].add(netlist[wire].GetNetCode())
        if VERBOSE:
            print('%s->%s->%d' % (wire_name, new_name, pin_num), end='\t')
        
        gate_build_pins[chip_name].append(pin_num)

    if VERBOSE:
        print()
    print('Added %s to %s at position %d of %d' % (ic_type, chip_name, gate_num, chip_gate_cnt))
    if VERBOSE:
        print()
    return added_new_IC # True if a new chip was added

def generate_pinouts(lib_74_path):
    """Generate pinouts from 74xx lib"""
    pinouts = {}
    sizes = {}
    paths = glob.glob(lib_74_path, recursive=True)
    for path in paths:
        chip_name = os.path.basename(path)
        chip_name = chip_name[:chip_name.find('.dig')]
        p = ET.parse(path).getroot()
        pinout = {}
        size = 0
        visualElements = None # will contain all pins
        for child in p:
            if child.tag == 'visualElements':
                visualElements = child
                break

        for ve_list in visualElements:
            pin_name = None
            for ve_list_item in ve_list:
                if ve_list_item.tag == 'elementAttributes':
                    for a in ve_list_item:
                        check = False
                        label = None
                        for b in a:
                            if b.tag == 'string':
                                if not b.text == 'Label':
                                    label = b.text
                                else:
                                    check = True
                        if check:
                            pin_name = label

                    for a in ve_list_item:
                        check1 = False
                        num = None
                        for b in a:
                            if b.tag == 'string':
                                if not b.text == 'pinNumber':
                                    num = b.text
                                else:
                                    check1 = True
                        if check1:
                            # Process the name
                            pin_name = pin_name.replace('/', 'not')

                            pinout[pin_name] = num
                            if int(num) > size:
                                size = int(num)
        sizes[chip_name] = size
        pinouts[chip_name] = pinout
        # print(chip_name, pinout)
    return pinouts, sizes



# main code

# generate pinouts
pinouts, sizes = generate_pinouts(footprint_path)

# Parse yosys JSON
js = json.load(open(json_path))
modules = js['modules']
top = modules[top_level_module]

# Add the nets featured in the top-level module
netlist = {}
for k in top['ports']:
    port = top['ports'][k]
    bits = port['bits']

    if k == 'VCC':
        assert len(bits) == 1
        bits[0] = 1
    elif k == 'GND':
        assert len(bits) == 1
        bits[0] = 0

    is_bus = len(bits) > 1
    # print(k, bits)
    for a in range(len(bits)):
        if (bits[a] == 'x'): # TODO: check this
            print("Warning: Skipping bit %s of port %s" % (a, k))
            continue
        # if (k.startswith('__')):
        #     print("Warning: Skipping port %s" % k)
        #     continue            
        bit = int(bits[a]) # this will turn VCC and GND nets from strings to ints
        if (bit == 0 or bit == 1):
            name = k
        else:
            name = '/' + k # kicad nets start with a '/'
        if is_bus:
            name = name + '%s' % str(a)
        netlist[bit] = name

# print('IO ports:', netlist)

# if there are no VCC and GND nets, create them now
if 0 not in netlist.keys():
    print('Warning: No GND net found in design - adding GND Net')
    wire = 0
    netlist[wire] = 'GND'
if 1 not in netlist.keys():
    print('Warning: No VCC net found in design - adding VCC Net')
    wire = 1
    netlist[wire] = 'VCC'

# Add nets to the kicad schematic
if KICAD:
    num_ios = len(netlist.keys())
    if (num_ios <= 40):
        ftprt = 'PinHeader_1x' + str(num_ios) + '_P2.54mm_Vertical'
        print('Header Footprint: ' + ftprt);
        m = pb.FootprintLoad(lib_path + 'Connector_PinHeader_2.54mm.pretty', ftprt)
        board.Add(m)
    else:
        print("Warning: IO header has more than 40 wires - skipping")

    a = 0
    for key in netlist.keys():
        net = pb.NETINFO_ITEM(board, netlist[key])
        board.Add(net)
        netlist[key] = net
        if (num_ios <= 40):
            m.Pads()[a].SetNetCode(net.GetNetCode())
        a += 1

# Pass 1 - add internal nets
for c in top['cells'].keys():
    ic_type = top['cells'][c]['type']

    # TODO: eventually remove this hotfix
    if ic_type == '\\28c256_rdonly':
        top['cells'][c]['type'] = '\\28c256'

    wires = top['cells'][c]['connections']

    for k in wires.keys():
        wire = wires[k]
        assert len(wire) == 1
        wire = int(wire[0])
        # print(k, wire)
        if wire not in netlist.keys():
            netlist[wire] = 'n' + str(wire)

            # Some test code to add the external IOs to a header
            if KICAD:
                net = pb.NETINFO_ITEM(board, netlist[wire])
                board.Add(net)
                netlist[wire] = net


# Pass 2 - Turn synthesized gates into ICs and add them to the schematic
chip_cnt = 0
for c in top['cells'].keys():
    ic_type = top['cells'][c]['type']

    wires = top['cells'][c]['connections']

    if ic_type.startswith('\\74AC'):
        # see if this type exists in gate builder
        if ic_type not in gate_build:
            gate_build[ic_type] = []
        if add_gate_to_IC(ic_type, wires, chip_cnt):
            chip_cnt += 1

# Pass 3 - add manually created ICs
for c in top['cells'].keys():
    ic_type = top['cells'][c]['type']

    # we've already added these
    if ic_type.startswith('\\74AC'):
        continue

    ic_type = ic_type.replace('\\', '') # remove backslashes
    
    size = sizes[ic_type]            # get pinout size
    wires = top['cells'][c]['connections']
    footprint = get_footprint_name(ic_type, size)

    # create footprint and position
    if KICAD:
        m = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', footprint)
        board.Add(m)
        kicad_ic_list.append(m)
        ref_str = ic_type + '_' + str(chip_cnt)
        kicad_netlist[ref_str] = set()
        m.SetReference(ref_str)
        print('Added: ' + ic_type)

    for k in wires.keys():
        wire = wires[k]
        assert len(wire) == 1
        wire = int(wire[0])
        # add nets
        if KICAD:
            pin_name = k.replace('\\', '')
            pin_num = pinouts[ic_type][pin_name]
            net_code = netlist[wire].GetNetCode()
            kicad_netlist[m.GetReference()].add(net_code)
            m.Pads()[int(pin_num)-1].SetNetCode(net_code)
            # print(ic_type, pin_name, pin_num)
    chip_cnt += 1

# position ICs on board
N = len(kicad_ic_list)
side_len = int(round(N**.5))
aspect = 2.5
spacing_x = 17
spacing_y = 25
spacing_factor = 1.75
side_len *= aspect
side_len = int(side_len)

# override side_len
side_len = 13

print('Total # of ICs: %d' % N)

import numpy as np
pos_arr = np.zeros((N, 2))
weights = np.zeros((N, N))

# set initial locations
for a in range(N):
    x = a % side_len
    y = a // side_len
    m = kicad_ic_list[a]
    pos_arr[a, :] = [x*spacing_x-40, y*spacing_y-40]

# build weights:
for a in range(N):
    for b in range(N):
        if a != b:
            weights[a][b] = len(kicad_netlist[kicad_ic_list[a].GetReference()].intersection(kicad_netlist[kicad_ic_list[b].GetReference()]))

def mse_slow(pos):
    err = 0
    for i in range(N):
        for j in range(N):
            err += np.linalg.norm(pos[i, :] - pos[j, :])**2 * weights[i][j]**4
    return err

def mse(pos):
    err = np.sum(np.linalg.norm(pos[np.newaxis, :, :] - pos[:, np.newaxis, :], axis=2)**2 * weights**4)
    return err

# try to optimize layout
curr_err = mse(pos_arr)
cnt = 0
old_designs = []

np.random.seed(1)

for i in tqdm(range(100000)):
    pos_arr_new = pos_arr.copy()

    for j in range(1):
        a = np.random.randint(0, N)
        b = np.random.randint(0, N)
        pos_arr_new[[a, b]] = pos_arr_new[[b, a]]
    
    new_err = mse(pos_arr_new)
    if new_err < curr_err:
        # print("Iteration: %d   \tNew error: %f" % (i, 10*np.log10(new_err)))
        curr_err = new_err
        pos_arr = pos_arr_new
        cnt = 0
    else:
        cnt += 1

    if cnt == 500:
        old_designs.append(pos_arr.copy())
        cnt = 0
        for j in range(5):
            a = np.random.randint(0, N)
            b = np.random.randint(0, N)
            pos_arr[[a, b]] = pos_arr[[b, a]]
        curr_err = mse(pos_arr)

for design in old_designs:
    if mse(design) < mse(pos_arr):
        pos_arr = design

print('Final error:', 10*np.log10(mse(pos_arr)))

# now set component locations
for a in range(N):
    m = kicad_ic_list[a]
    m.SetX(pb.pcbIUScale.mmToIU(pos_arr[a, 0]))
    m.SetY(pb.pcbIUScale.mmToIU(pos_arr[a, 1]))


if KICAD:
    board.Save(board_path)
    print('Board saved to %s' % board_path)
