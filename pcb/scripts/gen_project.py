"""Write PRAHARI.kicad_pro, fp-lib-table and sym-lib-table."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design as D

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# JLCPCB / PCBWay 2-layer economy process: 0.127 mm track & space, 0.3 mm drill.
# Everything below sits well inside that, so this board is the cheapest tier.
rules = {
    "min_clearance": 0.15,
    "min_connection": 0.0,
    "min_copper_edge_clearance": 0.3,
    "min_hole_clearance": 0.25,
    "min_hole_to_hole": 0.25,
    "min_microvia_diameter": 0.2,
    "min_microvia_drill": 0.1,
    "min_resolved_spokes": 1,
    "min_silk_clearance": 0.0,
    "min_text_height": 0.8,
    "min_text_thickness": 0.08,
    "min_through_hole_diameter": 0.3,
    "min_track_width": 0.15,
    "min_via_annular_width": 0.13,
    "min_via_diameter": 0.45,
    "solder_mask_to_copper_clearance": 0.0,
    "use_height_for_length_calcs": True,
}

classes = []
for name, (tw, cl, vd, vdr, nets) in D.NETCLASS.items():
    classes.append({
        "name": name, "clearance": cl, "track_width": tw,
        "via_diameter": vd, "via_drill": vdr,
        "microvia_diameter": 0.3, "microvia_drill": 0.1,
        "diff_pair_gap": 0.25, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25,
        "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
        "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "bus_width": 12,
        "priority": 2147483647 if name == "Default" else len(classes),
    })

netclass_patterns = []
for name, (_, _, _, _, nets) in D.NETCLASS.items():
    for n in nets or []:
        netclass_patterns.append({"pattern": n, "netclass": name})

pro = {
    "board": {"3dviewports": [], "design_settings": {
        "defaults": {
            "board_outline_line_width": 0.1, "copper_line_width": 0.2,
            "copper_text_size_h": 1.0, "copper_text_size_v": 1.0,
            "copper_text_thickness": 0.15, "other_line_width": 0.15,
            "silk_line_width": 0.13, "silk_text_size_h": 0.8,
            "silk_text_size_v": 0.8, "silk_text_thickness": 0.13,
        },
        "diff_pair_dimensions": [], "drc_exclusions": [],
        "rules": rules,
        "track_widths": [0.0, 0.25, 0.5, 0.9],
        "via_dimensions": [{"diameter": 0.0, "drill": 0.0},
                           {"diameter": 0.6, "drill": 0.3},
                           {"diameter": 0.8, "drill": 0.4}],
        "zones_allow_external_fillets": False,
    }, "layer_presets": [], "viewports": []},
    "boards": [],
    "cvpcb": {"equivalence_files": []},
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": "PRAHARI.kicad_pro", "version": 3},
    "net_settings": {
        "classes": classes,
        "meta": {"version": 4},
        "net_colors": None,
        "netclass_assignments": None,
        "netclass_patterns": netclass_patterns,
    },
    "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "",
                              "plot": "out/", "pos_files": "out/",
                              "specctra_dsn": "", "step": "", "svg": "", "vrml": ""},
               "page_layout_descr_file": ""},
    "schematic": {
        "annotate_start_num": 0,
        "drawing": {"dashed_lines_dash_length_ratio": 12.0,
                    "dashed_lines_gap_length_ratio": 3.0,
                    "default_line_thickness": 6.0, "default_text_size": 50.0,
                    "field_names": [], "intersheets_ref_own_page": False,
                    "intersheets_ref_prefix": "", "intersheets_ref_short": False,
                    "intersheets_ref_show": False, "intersheets_ref_suffix": "",
                    "junction_size_choice": 3, "label_size_ratio": 0.375,
                    "pin_symbol_size": 25.0, "text_offset_ratio": 0.15},
        "legacy_lib_dir": "", "legacy_lib_list": [],
        "meta": {"version": 1}, "net_format_name": "",
        "spice_current_sheet_as_root": False, "spice_external_command": "",
        "spice_model_current_sheet_as_root": True, "spice_save_all_currents": False,
        "spice_save_all_dissipations": False, "spice_save_all_voltages": False,
        "subpart_first_id": 65, "subpart_id_separator": 0,
    },
    "sheets": [["00000000-0000-0000-0000-000000000000", "Root"]],
    "text_variables": {},
}

open(os.path.join(PROJ, "PRAHARI.kicad_pro"), "w", encoding="utf-8").write(
    json.dumps(pro, indent=2))

# Declaring the stock libraries in the project tables, rather than relying on
# whatever is in the user's global tables, keeps the project self-contained.
FP_LIBS = ["Capacitor_SMD", "Resistor_SMD", "LED_SMD", "Diode_SMD",
           "Package_TO_SOT_SMD", "Package_SO", "Connector_PinHeader_2.54mm",
           "Connector_JST", "MountingHole", "TestPoint"]
SYM_LIBS = ["Device", "Connector", "Connector_Generic", "Security",
            "Transistor_FET", "Mechanical", "power"]

rows = ['  (lib (name "PRAHARI")(type "KiCad")(uri "${KIPRJMOD}/PRAHARI.pretty")'
        '(options "")(descr "PRAHARI project footprints"))']
rows += ['  (lib (name "%s")(type "KiCad")'
         '(uri "${KICAD10_FOOTPRINT_DIR}/%s.pretty")(options "")(descr ""))' % (n, n)
         for n in FP_LIBS]
open(os.path.join(PROJ, "fp-lib-table"), "w", encoding="utf-8").write(
    "(fp_lib_table\n  (version 7)\n" + "\n".join(rows) + "\n)\n")

rows = ['  (lib (name "PRAHARI")(type "KiCad")(uri "${KIPRJMOD}/PRAHARI.kicad_sym")'
        '(options "")(descr "PRAHARI project symbols"))']
rows += ['  (lib (name "%s")(type "KiCad")'
         '(uri "${KICAD10_SYMBOL_DIR}/%s.kicad_sym")(options "")(descr ""))' % (n, n)
         for n in SYM_LIBS]
open(os.path.join(PROJ, "sym-lib-table"), "w", encoding="utf-8").write(
    "(sym_lib_table\n  (version 7)\n" + "\n".join(rows) + "\n)\n")

print("wrote PRAHARI.kicad_pro, fp-lib-table, sym-lib-table")
