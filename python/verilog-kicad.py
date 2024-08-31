# Crappy Kicad python test code (probably out of date)
# exec(open("C:/Users/Ethan/Desktop/verilog-kicad.py").read())

lib_path = 'C:/Program Files/KiCad/8.0/share/kicad/footprints/'
board_path = 'C:/Users/Ethan/Desktop/modular_8bit_computer/verilog_kicad_test/verilog_kicad_test.kicad_pcb'

import pcbnew as pb

board = pb.BOARD() 
m = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', 'DIP-16_W7.62mm')
m.SetX(pb.pcbIUScale.mmToIU(10))
m.SetY(pb.pcbIUScale.mmToIU(3))

m2 = pb.FootprintLoad(lib_path + 'Package_DIP.pretty', 'DIP-16_W7.62mm')
m2.SetX(pb.pcbIUScale.mmToIU(70))
m2.SetY(pb.pcbIUScale.mmToIU(3))

board.Add(m)
board.Add(m2)

net = pb.NETINFO_ITEM(board, "a_net")
board.Add(net)




for pad in m.Pads():
    pad.SetNetCode(net.GetNetCode())

for pad in m2.Pads():
    pad.SetNetCode(net.GetNetCode())

    

board.Save(board_path)

#pb.LoadBoard(board_path)

# print(net.GetNetname())

# foot = board.GetFootprints()
# for f in foot:
#     print(f)
#     board.Remove(f)


# print(net.GetNetCode())


# track = pcbnew.PCB_TRACK(board)
# track.SetStart(pcbnew.wxPointMM(3, 6))
# track.SetEnd(pcbnew.wxPointMM(5, 7))
# track.SetWidth(int(10000))
# track.SetLayer(pcbnew.F_Cu)
# track.SetNetCode(net.GetNetCode())
# board.Add(track)