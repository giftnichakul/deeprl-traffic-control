import os
import xml.etree.ElementTree as ET

route_details = {
    'n': {
        'dir': '-E2',
        'weight': 66*3,
        'other_dir': {
            's': 3,
            'e': 1,
            'w': 1
        }
    },
    's': {
        'dir': '-E0',
        'weight': 70*4,
        'other_dir': {
            'n': 3,
            'e': 1,
            'w': 1
        }
    },
    'e': {
        'dir': '-E3',
        'weight': 50*2,
        'other_dir': {
            's': 1,
            'n': 1,
            'w': 1
        }
    },
    'w': {
        'dir': '-E1',
        'weight': 45*2,
        'other_dir': {
            's': 1,
            'e': 1,
            'n': 1
        }
    },
}

def create_routes(route_details, time, total_cars):
    """
    Usage Example: route_details = {n: ['-E2', 6], s: ['-E0', 6], e: ['-E3', 3], w: ['-E1', 2]}
    Results save in: [junction_name]/[time]/trips/...
    """
    root = ET.Element("routes")
    output_name = 'switch' + str(total_cars) + '.rou.xml'
    output_name = str(total_cars) + '.rou.xml'

    direction = ['n', 's', 'e', 'w']
    total_weight = sum(detail['weight'] for detail in route_details.values())

    color = {
        'n': {'s': '#FEC7B4', 'e': '#FC819E', 'w': '#F7418F'},
        's': {'n': '#41C9E2', 'e': '#008DDA', 'w': '#ACE2E1'},
        'e': {'n': '#FFEC9E', 's': '#FFBB70', 'w': '#ED9455'},
        'w': {'n': '#C5EBAA', 's': '#7F9F80', 'e': '#3BFEA7'}
    }

    for dir1 in direction:
        total_dir1 = round(route_details[dir1]['weight']/total_weight*total_cars)
        sub_weight = sum(weight for weight in route_details[dir1]['other_dir'].values())
        for dir2 in direction:
            if(dir1 != dir2):
                total_dir2 = round(route_details[dir1]['other_dir'][dir2]/sub_weight*total_dir1)
                if(len(route_details[dir2]['dir']) == 3):
                    edges = route_details[dir1]['dir'] + ' ' + route_details[dir2]['dir'][1:]
                else:
                    edges = route_details[dir1]['dir'] + ' ' + '-' + route_details[dir2]['dir']

                # print(edges)
                ET.SubElement(root, "route", id=f"route_{dir1}{dir2}", edges=edges, color=color[dir1][dir2])
                ET.SubElement(root, "flow", id=f"flow_{dir1}{dir2}", route=f"route_{dir1}{dir2}",
                                begin="0",end=str(time),
                                vehsPerHour=str(total_dir2),
                                departSpeed="max", departPos="base", departLane="best")
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')

    time_name = f"{str(time/3600)}hour"
    output_dir = os.path.join('saint_paul', time_name, 'trips')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, output_name)
    tree.write(output_file)
    print('Create Success')


total_cars = [2500, 3000, 3500, 4000, 4500, 5000]
for cars in total_cars:
    create_routes(route_details, 3600, cars)