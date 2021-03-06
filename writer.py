import sys
import record
import json
import f2_map
import grup
import struct
import zlib
import math
import os
from plugin import Plugin
from grup import GRUP

debug_level = 0


def debug(msg):
    if debug_level < 2:
        return
    print(msg)


def warn(msg):
    if debug_level < 1:
        return
    print(msg)


def error(msg):
    if debug_level < 0:
        return
    print(msg)


MAP_SIZE_FACTOR = 128

OBJECTS = dict()
OBJECTS["F2CovenantGenericM01"] = 33560401
OBJECTS["F2CovenantGenericF01"] = 33560403
OBJECTS["TreeElmForest01Institute"] = 2011464
OBJECTS["TreeMapleInstitute05Green"] = 2011474
OBJECTS["LS_WaterPumpStatic"] = 2284588
OBJECTS["BldWoodBSmFlrOnly01"] = 486400
OBJECTS["BldWoodBSmFlrOnly02"] = 486401
OBJECTS["BldWoodBSmFlrOnly04"] = 486403
OBJECTS["BldWoodBSmFlrOnly09"] = 486408
OBJECTS["TreeSapling03"] = 1742810
OBJECTS["TreeMaplePreWar04Gr"] = 398918
OBJECTS["FloraWildCornStalk01"] = 1851412
OBJECTS["CampFireMed01_Off"] = 396627
OBJECTS["CinderBlockSquare01"] = 7680
OBJECTS["RWResPost01"] = 252692
OBJECTS["BldBrickSmFlrPlatQuarter01"] = 575511

OBJECTS["BldWoodBBGWall01"] = 486165

OBJECTS["MetalRoof11x1Mid01"] = 947063

TILES = dict()
TILES["edg5003"] = "BldWoodBSmFlrOnly01"
TILES["edg5000"] = "BldWoodBSmFlrOnly01"
TILES["edg5002"] = "BldWoodBSmFlrOnly01"
TILES["edg5004"] = "BldWoodBSmFlrOnly01"
TILES["edg5005"] = "BldWoodBSmFlrOnly01"
TILES["edg5007"] = "BldWoodBSmFlrOnly01"
TILES["edg5003"] = "BldWoodBSmFlrOnly01"
TILES["edg5006"] = "BldWoodBSmFlrOnly02"
TILES["edg5001"] = "BldWoodBSmFlrOnly04"

# global paths/flags
F2_DATA_DIR = None
RAW_INPUT_DIR = None
OPT1 = False
OPT2 = False


def get_map_files(map_name, F2_DATA_DIR):
    map_file_path = "%s/maps/%s.json" % (F2_DATA_DIR, map_name)
    map_images_file_path = "%s/maps/%s.images.json" % (F2_DATA_DIR, map_name)

    with open(map_file_path, "r") as map_file:
        map = f2_map.Map(json.loads(map_file.read()))

    with open(map_images_file_path, "r") as map_images_file:
        map_images = json.loads(map_images_file.read())

    return map, map_images


def get_position_data(x, y, z, rx, ry, rz):
    return struct.pack("f", x) + struct.pack("f", y) + struct.pack("f", z) + struct.pack("f", rx) + struct.pack("f", ry) + struct.pack("f", rz)


def get_raw_header(type, data_size, flags, id):
    raw_header = type.encode("utf-8")  # type
    raw_header += struct.pack("I", data_size)  # data_size
    raw_header += struct.pack("I", flags)  # flags
    raw_header += struct.pack("I", id)  # id
    raw_header += struct.pack("I", 0)  # rev
    raw_header += struct.pack("H", 131)  # version
    raw_header += struct.pack("H", 0)  # rev2
    return raw_header


def get_tes4_header(data_size):
    raw_header = "TES4".encode("utf-8")  # type
    raw_header += struct.pack("I", data_size)  # data_size
    raw_header += struct.pack("I", 0)  # flags
    raw_header += struct.pack("I", 0)  # id
    raw_header += struct.pack("I", 0)  # rev
    raw_header += struct.pack("H", 131)  # version
    raw_header += struct.pack("H", 0)  # rev2
    return raw_header


def get_perm_refr_raw_data(map, level, map_name, entrances, exits):
    raw_data = b''

    coc_present = False
    for exit in entrances:
        if not coc_present:
            edid = "coc_%s" % (map_name)
            # REFR is :
            # EDID / NAME / DATA
            refr = "EDID".encode("utf-8") + struct.pack("H",
                                                        len(edid)) + edid.encode("utf-8")
            refr += "NAME".encode("utf-8") + \
                struct.pack("H", 4) + struct.pack("I", 50)
            refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", exit.to_x*MAP_SIZE_FACTOR) + struct.pack(
                "f", exit.to_y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0)

            refr_header = get_raw_header(
                "REFR", len(refr), 0, map.cell_ids[level] + 1)
            raw_data += (refr_header + refr)
            coc_present = True

        # EDID \x14\x00 Entrance_from_other\x00
        # NAME\x04\x00hJ\x04\x00
        # XTEL $\x00 \xf2\x1e\x00\x02
        # 	(pos)	 h\x80\x9aD D\x9bG\xc4 \x00\x00\x80\xb8 \x00\x00\x00\x00 \x00\x00\x00\x00 \x00\x00\x00\x00
        # 	(flags)	 \x00\x00\x00\x00 \x00\x00\x00\x00
        # DATA \x18\x00 \x82\xc2\xceC \x805\xc3@ \x00\x00\x00\x00 \x00\x00\x00\x00 \x00\x00\x00\x00 \x00\x00\x00\x00'

        if exit.to_level != level:
            continue
        # for each entrance: one invisible door
        edid = "Entrance_from_%d_%d_to_%d" % (
            exit.from_map, exit.from_level, exit.to_form_id)
        refr = "EDID".encode("utf-8") + struct.pack("H",
                                                    len(edid)) + edid.encode("utf-8")
        refr += "NAME".encode("utf-8") + struct.pack("H",
                                                     4) + struct.pack("I", 281192)
        refr += "XTEL".encode("utf-8") + struct.pack("H", 36) + struct.pack("I", exit.from_form_id) + get_position_data(
            exit.from_x*MAP_SIZE_FACTOR, exit.from_y*MAP_SIZE_FACTOR, 0, 0, 0, 0) + struct.pack("I", 1) + struct.pack("I", 0)
        refr += "DATA".encode("utf-8") + struct.pack("H", 24) + get_position_data(
            exit.to_x*MAP_SIZE_FACTOR, exit.to_y*MAP_SIZE_FACTOR, 0, 0, 0, 0)

        refr_header = get_raw_header("REFR", len(refr), 1024, exit.to_form_id)
        raw_data += (refr_header + refr)

    for exit in exits:
        if exit.from_level != level:
            continue
        edid = "Exit_to_%d_%d_from_%d" % (
            exit.to_map, exit.to_level, exit.from_form_id)
        # REFR is :
        # EDID / NAME / DATA
        refr = "EDID".encode("utf-8") + struct.pack("H",
                                                    len(edid)) + edid.encode("utf-8")
        refr += "NAME".encode("utf-8") + struct.pack("H",
                                                     4) + struct.pack("I", 126327)
        refr += "XTEL".encode("utf-8") + struct.pack("H", 36) + struct.pack("I", exit.to_form_id) + get_position_data(
            exit.to_x*MAP_SIZE_FACTOR, exit.to_y*MAP_SIZE_FACTOR, 0, 0, 0, 0) + struct.pack("I", 1) + struct.pack("I", 0)
        refr += "XSCL".encode("utf-8") + struct.pack("H",
                                                     4) + struct.pack("f", 0.25)
        refr += "DATA".encode("utf-8") + struct.pack("H", 24) + get_position_data(
            exit.from_x*MAP_SIZE_FACTOR, exit.from_y*MAP_SIZE_FACTOR, 0, 0, 0, 0)

        refr_header = get_raw_header(
            "REFR", len(refr), 1024, exit.from_form_id)
        raw_data += (refr_header + refr)

    return raw_data


def get_temp_refr_raw_data(raw_folder, map, level, map_name, floor_tiles, roof_tiles, objs, v_walls, h_walls):
    raw_data = b''
    for (x, y, tile) in floor_tiles:
        if tile in TILES:
            edid = OBJECTS[TILES[tile]]
        else:
            edid = OBJECTS["BldWoodBSmFlrOnly09"]
        with open("%s/REFR/%s" % (raw_folder, edid), "rb") as raw_base_file:
            refr = raw_base_file.read()

        # REFR is :
        # NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
        refr = refr[:16] + struct.pack("f", x*MAP_SIZE_FACTOR) + \
            struct.pack("f", y*MAP_SIZE_FACTOR) + refr[24:]

        refr_header = get_raw_header("REFR", len(refr), 0, map.get_id(level))
        raw_data += (refr_header + refr)
        #print("%d/%d %s" % (x, y, refr))

    for (x, y, tile) in roof_tiles:
        # REFR is :
        # NAME(4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
        refr = "NAME".encode("utf-8") + struct.pack("H", 4) + \
            struct.pack("I", OBJECTS["MetalRoof11x1Mid01"])
        refr += "DATA".encode("utf-8") + struct.pack("H", 24) + get_position_data(
            (x+5)*MAP_SIZE_FACTOR, (y-1)*MAP_SIZE_FACTOR, 2*MAP_SIZE_FACTOR, 0, 0, 0)

        refr_header = get_raw_header("REFR", len(refr), 0, map.get_id(level))
        raw_data += (refr_header + refr)
        #print("%d/%d %s" % (x, y, refr))

    types_to_do = dict()
    for (x, y, type, object) in objs:
        z = 0
        if type == "walls":
            edid = OBJECTS["CinderBlockSquare01"]
        # elif object == "block":
        #	if type == "misc":
        #		pass
        #		# edid = OBJECTS["RWResPost01"]
        #	else:
        #		edid = OBJECTS["CinderBlockSquare01"]
        elif "exit" in object:
            edid = OBJECTS["BldBrickSmFlrPlatQuarter01"]
            z = 5
        elif "tree" in object:
            edid = OBJECTS["TreeMaplePreWar04Gr"]
        elif "weed" in object:
            edid = OBJECTS["TreeSapling03"]
        elif "corn" in object:
            edid = OBJECTS["FloraWildCornStalk01"]
        elif "woodfire" in object:
            edid = OBJECTS["CampFireMed01_Off"]
        else:
            if object not in types_to_do:
                types_to_do[object] = 0
            types_to_do[object] += 1
            continue

        with open("%s/REFR/2011474" % raw_folder, "rb") as raw_base_file:
            refr = raw_base_file.read()

        # REFR is :
        # NAME(4) + EDID(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
        refr = refr[:6] + struct.pack("I", edid) + refr[10:16] + struct.pack(
            "f", x*MAP_SIZE_FACTOR) + struct.pack("f", y*MAP_SIZE_FACTOR) + struct.pack("f", z) + refr[28:]
        refr_header = get_raw_header("REFR", len(refr), 0, map.get_id(level))
        raw_data += (refr_header + refr)
        #print("%d/%d %s" % (x, y, refr))

    # print(types_to_do)
    # print(walls)
    for wall in v_walls:
        for (x, y, type, wall_name) in wall:
            with open("%s/REFR/2011474" % raw_folder, "rb") as raw_base_file:
                refr = raw_base_file.read()

            edid = OBJECTS["BldWoodBBGWall01"]
            y = 0.5 * y
            if x % 2 != 0:
                y -= 0.25
            x = 0.5 * x

            #print("wall at %f/%f" % (x, y))
            # REFR is :
            # NAME(4) + EDID(2+4) + XSCL(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
            refr = refr[:6] + struct.pack("I", edid)
            refr += "XSCL".encode("utf-8") + \
                struct.pack("H", 4) + struct.pack("f", 0.25)
            refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR + 30) + struct.pack(
                "f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0)
            refr_header = get_raw_header(
                "REFR", len(refr), 0, map.get_id(level))
            raw_data += (refr_header + refr)

            with open("%s/REFR/2011474" % raw_folder, "rb") as raw_base_file:
                refr = raw_base_file.read()

            refr = refr[:6] + struct.pack("I", edid)
            refr += "XSCL".encode("utf-8") + \
                struct.pack("H", 4) + struct.pack("f", 0.25)
            refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR - 30) + struct.pack(
                "f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", math.radians(180))
            refr_header = get_raw_header(
                "REFR", len(refr), 0, map.get_id(level))
            raw_data += (refr_header + refr)

    for wall in h_walls:
        for (x, y, type, wall_name) in wall:
            with open("%s/REFR/2011474" % raw_folder, "rb") as raw_base_file:
                refr = raw_base_file.read()

            edid = OBJECTS["BldWoodBBGWall01"]

            # placement is different for walls because of the "zigzag" line of hex tiles
            y = 0.5 * (y-1)
            # if x % 2 != 0:
            #	y -= 0.5
            x = 0.5 * x

            #print("wall at %f/%f" % (x, y))
            # REFR is :
            # NAME(4) + EDID(2+4) + XSCL(2+4) + DATA(4)+data_size(2) + x(4) + y(4) + z(4) + rx(4) + ry(4) + rz(4)
            refr = refr[:6] + struct.pack("I", edid)
            refr += "XSCL".encode("utf-8") + \
                struct.pack("H", 4) + struct.pack("f", 0.25)
            refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack(
                "f", y*MAP_SIZE_FACTOR) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", math.radians(90))
            refr_header = get_raw_header(
                "REFR", len(refr), 0, map.get_id(level))
            raw_data += (refr_header + refr)

            with open("%s/REFR/2011474" % raw_folder, "rb") as raw_base_file:
                refr = raw_base_file.read()

            refr = refr[:6] + struct.pack("I", edid)
            refr += "XSCL".encode("utf-8") + \
                struct.pack("H", 4) + struct.pack("f", 0.25)
            refr += "DATA".encode("utf-8") + struct.pack("H", 24) + struct.pack("f", x*MAP_SIZE_FACTOR) + struct.pack(
                "f", y*MAP_SIZE_FACTOR+64) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", 0) + struct.pack("f", math.radians(270))
            refr_header = get_raw_header(
                "REFR", len(refr), 0, map.get_id(level))
            raw_data += (refr_header + refr)

    return raw_data


def get_cell_raw_data(raw_folder, form_id, edid):
    raw_data = b''
    with open("%s/CELL/arroyoVillage" % raw_folder, "rb") as raw_base_file:
        raw_base_file.read(4)
        edid_size = struct.unpack("H", raw_base_file.read(2))[0]
        raw_base_file.read(edid_size)

        raw_base_file.read(4)
        full_size = struct.unpack("H", raw_base_file.read(2))[0]
        raw_base_file.read(full_size)

        cell_data = raw_base_file.read()

    raw_data += "EDID".encode("utf-8")
    raw_data += struct.pack("H", len(edid))
    raw_data += edid.encode("utf-8")

    full = edid + " marker"
    raw_data += "FULL".encode("utf-8")
    raw_data += struct.pack("H", len(full))
    raw_data += full.encode("utf-8")

    raw_data += cell_data
    return raw_data


def get_raw_grup_header(data_size, label, group_type):
    raw_header = "GRUP".encode("utf-8")  # type
    # data_size of grup includes headers
    raw_header += struct.pack("I", data_size + 24)
    if group_type == 0:
        raw_header += label.encode("utf-8")
    elif group_type in [2, 3, 6, 8, 9]:
        raw_header += struct.pack("I", label)  # long, block number
    else:
        error("GRUP type not managed: %d" % group_type)
        raise Exception("GRUP type not managed: %d" % group_type)  # form ID
    raw_header += struct.pack("I", group_type)  # group_type
    raw_header += struct.pack("I", 0)  # rev
    raw_header += struct.pack("H", 131)  # version
    raw_header += struct.pack("H", 0)  # rev2
    return raw_header


def get_map_cell_sub_block(raw_input_dir, map, number, level):
    floor_tiles = map.get_floor_tiles(level)
    roof_tiles = map.get_roof_tiles(level)
    objs = map.get_objects(level)
    v_walls, h_walls = map.get_walls(level)
    entrances = map.get_entrances(level)
    exits = map.exits
    map_name = map.name[:-4] + "_" + str(level)
    print("map %s - %d entrances - %d exits" %
          (map_name, len(entrances), len(exits)))

    #x_min, y_min, width, height = map.get_map_size()

    cell_id = map.cell_ids[level]
    # refr_data									analyze data for REFR
    perm_refr_data = get_perm_refr_raw_data(
        map, level, map_name, entrances, exits)
    temp_refr_data = get_temp_refr_raw_data(raw_input_dir,
                                            map, level, map_name, floor_tiles, roof_tiles, objs, v_walls, h_walls)

    # perm_grup								analyze GRUP of size 2280 - label b'\x99\x0f\x00\x02' - type 8
    perm_grup_header = get_raw_grup_header(len(perm_refr_data), cell_id, 8)
    perm_grup = perm_grup_header + perm_refr_data

    # temp_grup								analyze GRUP of size 2280 - label b'\x99\x0f\x00\x02' - type 9
    temp_grup_header = get_raw_grup_header(len(temp_refr_data), cell_id, 9)
    temp_grup = temp_grup_header + temp_refr_data

    #									 CELL children of CELL ID 33558425
    # cell_children_grup			analyze GRUP of size 2304 - label 33558425 - type 6
    cell_children_grup_header = get_raw_grup_header(
        len(perm_grup) + len(temp_grup), cell_id, 6)
    cell_children = cell_children_grup_header + perm_grup + temp_grup

    # cell_record					analyze data for CELL
    cell_record_data = get_cell_raw_data(raw_input_dir, cell_id, map_name)
    compressed_flag = int('0x00040000', 16)
    compressed_data = struct.pack(
        "I", len(cell_record_data)) + zlib.compress(cell_record_data)

    cell_record_header = get_raw_header("CELL", len(
        compressed_data), compressed_flag, cell_id)
    cell_record = cell_record_header + compressed_data

    cell_sub_block_header = get_raw_grup_header(
        len(cell_record) + len(cell_children), number, 3)
    cell_sub_block = cell_sub_block_header + cell_record + cell_children
    return cell_sub_block


def main():
    if len(sys.argv) < 3:
        print("USAGE:", sys.argv[0], "F2_DATA_DIR",
              "RAW_INPUT_DIR", "PLUGIN_FILE")
        print("example: python writer.py ./f2_extractor f4_input/raw")
        return

    F2_DATA_DIR = sys.argv[1]
    RAW_INPUT_DIR = sys.argv[2]

    if len(sys.argv) == 4:
        global debug_level
        if sys.argv[3] == "debug":
            debug_level = 2
        elif sys.argv[3] == "warn":
            debug_level = 1
    else:
        print("silent mode, append 'warn' or 'debug' to command-line to increase log level")

    p = Plugin()

    with open("%s/TES4" % RAW_INPUT_DIR, "rb") as tes4_file:
        tes4_raw_data = tes4_file.read()
    tes4_raw_header = get_tes4_header(len(tes4_raw_data))
    p.TES4 = (tes4_raw_header + tes4_raw_data)

    maps = dict()

    for map_file_name in os.listdir("%s/maps" % F2_DATA_DIR):
        if "images.json" in map_file_name:
            continue
        debug("load map %s" % map_file_name)
        with open("%s/maps/%s" % (F2_DATA_DIR, map_file_name), "r") as map_file:
            map_content = map_file.read()
            if len(map_content) == 0:
                warn("map %s is empty" % map_file_name)
            else:
                map = f2_map.Map(json.loads(map_content))
                if map.map_id < 0:
                    continue
                maps[map.map_id] = map

    base_id = 33558500
    for map in maps.values():
        for level in range(len(map.levels)):
            map.cell_ids[level] = base_id
            map.form_ids[level] = base_id + 2
            base_id += 50000

    error_maps = set()
    for map in maps.values():
        debug("build entrances and exits for map %s" % map)
        exits = map.get_exits()
        for exit in exits:
            debug(" * %s" % exit)
            exit.from_form_id = map.get_id(exit.from_level)

            # for each entrance: one invisible door on target map
            target_map_id = exit.to_map
            target_level = exit.to_level
            if not target_map_id in maps:
                error("impossible to create * %s" % exit)
                error("map %d does not exists" % target_map_id)
                error_maps.add(map.map_id)
                continue
            exit.to_form_id = maps[target_map_id].get_id(exit.to_level)
            if not target_level in maps[target_map_id].entrances:
                maps[target_map_id].entrances[target_level] = set()
            maps[target_map_id].entrances[target_level].add(exit)

    for map in maps.values():
        debug("map %d, entrances: %s" % (map.map_id, map.entrances))
        for level in range(len(map.levels)):
            if level in map.entrances:
                for exit in map.entrances[level]:
                    debug("\tlevel %d - entrance dir: %s" %
                          (level, exit.to_dir))

    sub_blocks = b''
    number = 0

    for map_id, map in maps.items():
        if map_id in error_maps:
            continue
        for level in range(len(map.levels)):
            sub_blocks += get_map_cell_sub_block(
                RAW_INPUT_DIR, map, number, level)
            number += 1

    cell_block_header = get_raw_grup_header(len(sub_blocks), 3, 2)
    cell_block = cell_block_header + sub_blocks

    top_grup_header = get_raw_grup_header(len(cell_block), "CELL", 0)
    top_grup = top_grup_header + cell_block

    p.GRUPs.append(top_grup)

    p.write("out/f2gen.esp")


if __name__ == "__main__":
    main()
