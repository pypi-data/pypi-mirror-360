import cadwork as cw
import utility_controller as uc
import element_controller as ec
import scene_controller as sc
import geometry_controller as gc
import material_controller as mc
import attribute_controller as ac
import shop_drawing_controller as sdc
import list_controller as lc
import menu_controller as mec
import visualization_controller as vc
drill_list=[]
panel_list=[]
massage ="yes"
element_ids = ec.get_all_identifiable_element_ids()
for element in element_ids:
    if ac.is_panel(element):
        panel_list.append(element)
    if ac.is_drilling(element):
        drill_list.append(element)

for panel in panel_list:
    for drill in drill_list:
        if ec.check_if_elements_are_in_collision(panel, drill):
            cw.set_auto_attribute([panel], str(drill))
