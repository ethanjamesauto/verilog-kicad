# exec(open("C:/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test/verilog-kicad.py").read())
KICAD = True

footprint_path = '../74xx/**/**.dig'
json_path = '../out.json'
top_level_module = 'test2'

if KICAD:
    footprint_path = 'C:/Users/Ethan/Documents/Digital/lib/DIL Chips/74xx/**/**.dig'
    json_path = '\\\\wsl$\\Ubuntu\\home\\ethan\\verilog-kicad\\out.json'
    lib_path = 'C:/Program Files/KiCad/8.0/share/kicad/footprints/'
    board_path = 'C:/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test/verilog_kicad_test.kicad_pcb'
    import pcbnew as pb
    board = pb.BOARD()

footprints = {
    20: 'DIP-20_W7.62mm',
    16: 'DIP-16_W7.62mm',
    14: 'DIP-14_W7.62mm'
    }

gate_build = {} # stores the 74-series chips currently being built from individual gates. maps ic_type -> list of kicad footprints
gate_build_ctr = {} # maps ic_type -> # of gates currently used in the footprint being built (the one not completed yet)

# # of gates per 74 series ic (example '74AC04_6x1NOT' returns 6)
def gate_count(ic_type):
    return int(ic_type[ic_type.find('_')+1:ic_type.find('x')])

def gate_name_to_chip(ic_type):
    code = ic_type[ic_type.find('C')+1:ic_type.find('_')]
    return '74' + code

def add_gate_to_chip(ic_type, wires, i):
    ret = False
    # print(ic_type, wires)
    chip_name = gate_name_to_chip(ic_type)
    pinout = pinouts[chip_name]
    footprint = footprints[sizes[chip_name]]

    gate_list = gate_build[ic_type]
    chip_gate_cnt = gate_count(ic_type)

    if len(gate_list) == 0 or gate_build_ctr[ic_type] == chip_gate_cnt:
        if KICAD:
            m = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', footprint)
            board.Add(m)
            m.SetX(pb.pcbIUScale.mmToIU(i*30/2.54))
            m.SetY(pb.pcbIUScale.mmToIU(50))
            m.SetReference(ic_type + '_' + str(i) + '_gen')

            # Tie VCC and GND
            # print(pinout, netlist)
            m.Pads()[int(pinout['GND'])-1].SetNetCode(netlist[0].GetNetCode())
            m.Pads()[int(pinout['VCC'])-1].SetNetCode(netlist[1].GetNetCode())
            print('Added (sythesized): ' + chip_name)

        else:
            m = chip_name + ' ' + ic_type
        ret = True
        gate_list.append(m)
        gate_build_ctr[ic_type] = 1
    else:
        m = gate_list[-1]
        gate_build_ctr[ic_type] += 1

    # rename gate wires to IC footprint pin names
    gate_num = gate_build_ctr[ic_type]
    for wire_name in wires:
        if chip_name == '74374' or chip_name == '7474' or chip_name == '74273':
            new_name = wire_name + str(gate_num - 1)
        else:
            new_name = str(gate_num) + wire_name

        if wire_name == 'CLK': # TODO: oh dear
            new_name = wire_name

        assert len(wires[wire_name]) == 1
        wire = int(wires[wire_name][0]) # TODO: prob collapses vcc and gnd to 0 1
        pin_num = pinout[new_name]
        if KICAD:
            m.Pads()[int(pin_num)-1].SetNetCode(netlist[wire].GetNetCode())

    return ret # True if a new chip was added



# generate pinouts
import json
import glob
import os
paths = glob.glob(footprint_path)
paths

import xml.etree.ElementTree as ET

pinouts = {}
sizes = {}
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
        valid = False
        pin_name = None
        pin_num = None
        for ve_list_item in ve_list:
            if ve_list_item.tag == 'elementName':
                t = ve_list_item.text
                if t == 'In' or t == 'Out':
                    valid = True
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
                        pinout[pin_name] = num
                        if int(num) > size:
                            size = int(num)
    sizes[chip_name] = size
    pinouts[chip_name] = pinout
    # print(chip_name, size, pinout, sep='    \t')



# Parse yosys JSON
with open(json_path) as fp:
    js = json.load(fp)

modules = js['modules']

top = modules[top_level_module]

netlist = {}

for k in top['ports']:
    port = top['ports'][k]
    bits = port['bits']
    # print(k, bits)
    for i in range(len(bits)):
        bit = int(bits[i]) # this will turn VCC and GND nets from strings to ints
        name = k
        if i > 0:
            name = name + str(i)
        netlist[bit] = name

# print('IO ports:', netlist)

# TODO Here: add kicad nets
if KICAD:
    ftprt = 'PinHeader_1x' + str(len(netlist.keys())) + '_P2.54mm_Vertical'
    print('Header Footprint: ' + ftprt);
    m = pb.FootprintLoad(lib_path + 'Connector_PinHeader_2.54mm.pretty', ftprt)
    board.Add(m)

    i = 0
    for key in netlist.keys():
        net = pb.NETINFO_ITEM(board, netlist[key])
        board.Add(net)
        netlist[key] = net
        m.Pads()[i].SetNetCode(net.GetNetCode())
        i += 1
# end kicad net code



# Pass 1 - add all nets and assign gates to chips
for c in top['cells'].keys():
    ic_type = top['cells'][c]['type']
    if not ic_type.startswith('\\74'):# or ic_type.startswith('\\74AC'):
        print('Error: ' + ic_type + ' is not a 74-series IC! Skipping logic implementation\n')
        continue

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

# print('Full netlist:', netlist)

# if there are no VCC and GND nets, create them now
if KICAD:
    if 0 not in netlist.keys():
        print('Note: Adding GND Net')
        wire = 0
        net = pb.NETINFO_ITEM(board, 'GND')
        board.Add(net)
        netlist[wire] = net
    if 1 not in netlist.keys():
        print('Note: Adding VCC Net')
        wire = 1
        net = pb.NETINFO_ITEM(board, 'VCC')
        board.Add(net)
        netlist[wire] = net

# pass 1.5
i = 0
for c in top['cells'].keys():
    ic_type = top['cells'][c]['type']
    if not ic_type.startswith('\\74'):# or ic_type.startswith('\\74AC'):
        print('Error: ' + ic_type + ' is not a 74-series IC! Skipping logic implementation\n')
        continue

    wires = top['cells'][c]['connections']

    if ic_type.startswith('\\74AC'):
        # print(c, ic_type)

        # see if this type exists in gate builder
        if ic_type not in gate_build:
            gate_build[ic_type] = []
        if add_gate_to_chip(ic_type, wires, i):
            i += 1


# Pass 2 - add chips
i = 0
for c in top['cells'].keys():
    ic_type = top['cells'][c]['type']
    if not ic_type.startswith('\\74'):# or ic_type.startswith('\\74AC'):
        # print('Error: ' + ic_type + ' is not a 74-series IC! Skipping logic implementation\n')
        continue
    # we've already added these
    if ic_type.startswith('\\74AC'):
        continue

    ic_type = ic_type.replace('\\', '') # remove backslashes
    
    size = sizes[ic_type]            # get pinout size
    wires = top['cells'][c]['connections']
    footprint = footprints[size]

    # create footprint and position
    if KICAD:
        m = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', footprint)
        m.SetX(pb.pcbIUScale.mmToIU(i*30/2.54))
        m.SetY(pb.pcbIUScale.mmToIU(i*0))
        board.Add(m)
        m.SetReference(ic_type + '_' + str(i))
        print('Added: ' + ic_type)

    for k in wires.keys():
        wire = wires[k]
        assert len(wire) == 1
        wire = int(wire[0])
        # add nets
        if KICAD:
            pin_name = k.replace('\\', '')
            pin_num = pinouts[ic_type][pin_name]
            m.Pads()[int(pin_num)-1].SetNetCode(netlist[wire].GetNetCode())
            # print(ic_type, pin_name, pin_num)
    i += 1

if KICAD:
    board.Save(board_path)
