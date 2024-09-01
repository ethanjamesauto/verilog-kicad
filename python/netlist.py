# exec(open("C:/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test/verilog-kicad.py").read())
KICAD = True

import json
footprint_path = '../74xx/**/**.dig'
json_path = '../out.json'

if KICAD:
    footprint_path = 'C:/Users/Ethan/Documents/Digital/lib/DIL Chips/74xx/**/**.dig'
    json_path = '\\\\wsl$\\Ubuntu\\home\\ethan\\verilog-kicad\\out.json'
    lib_path = 'C:/Program Files/KiCad/8.0/share/kicad/footprints/'
    board_path = 'C:/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test/verilog_kicad_test.kicad_pcb'
    import pcbnew as pb
    board = pb.BOARD()

footprints = {
    16: 'DIP-16_W7.62mm',
    14: 'DIP-14_W7.62mm'
    }


# generate pinouts
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

top = modules['counter_card']

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

print('IO ports:', netlist)

# TODO Here: add kicad nets
if KICAD:
    ftprt = 'PinHeader_1x' + str(len(netlist.keys())) + '_P2.54mm_Vertical'
    print('Header Footprint:' + ftprt);
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

# Pass 1 - add all nets
for c in top['cells'].keys():
    type = top['cells'][c]['type']
    if not type.startswith('\\74') or type.startswith('\\74AC'):
        # print('Error: ' + type + ' is not a 74-series IC! Skipping logic implementation\n')
        continue

    type = type.replace('\\', '') # remove backslashes

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

print('Full netlist:', netlist)

# Pass 2 - add chips
i = 0
for c in top['cells'].keys():
    type = top['cells'][c]['type']
    if not type.startswith('\\74') or type.startswith('\\74AC'):
        # print('Error: ' + type + ' is not a 74-series IC! Skipping logic implementation\n')
        continue

    type = type.replace('\\', '') # remove backslashes
    
    size = sizes[type]            # get pinout size
    wires = top['cells'][c]['connections']
    footprint = footprints[size]

    # TODO here: create footprint and position
    if KICAD:
        m = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', footprint)
        m.SetX(pb.pcbIUScale.mmToIU(i*25/2.54))
        m.SetY(pb.pcbIUScale.mmToIU(i*0))
        board.Add(m)
        m.SetReference(type + '_' + str(i))
        print('Added:' + str(m))
    # end footprint code

    for k in wires.keys():
        wire = wires[k]
        assert len(wire) == 1
        wire = int(wire[0])
        # print(k, wire)
        # TODO here: add nets
        if KICAD:
            pin_name = k.replace('\\', '')
            pin_num = pinouts[type][pin_name]
            m.Pads()[int(pin_num)-1].SetNetCode(netlist[wire].GetNetCode())
            # print(type, pin_name, pin_num)
        # end net code

    i += 1
    # print(type, end=':\n')
    # print('\t', wires)
    # print('\t', pinouts[type])

if KICAD:
    board.Save(board_path)
