from pyvis.network import Network

def build_interactive_subject_graph(subjects):
    net = Network(
        height="700px", 
        width="100%", 
        bgcolor="#222222", 
        font_color="white", 
        directed=True, 
        # filter_menu=True,
        select_menu=True,
        cdn_resources='remote'
        )

    net.set_options(
        '''
        {
            "edges": {
                "color": {"inherit": true},
                "smooth": true
            },
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "levelSeparation": 150,
                    "direction": "LR"
                   
                }
            },
            "physics": {
                "hierarchicalRepulsion": {
                    "centralGravity": 8
                },
                "minVelocity": 0.75,
                "solver": "hierarchicalRepulsion"
            }
        }
        '''
    )

    all_subjects = set()
    for semester, semester_subjects in subjects.items():
        for subject in semester_subjects.keys():
            all_subjects.add(subject)
    
    level_map = 1
    for (year,semester), semester_subjects in subjects.items():
        for subject in semester_subjects.keys():
            f_title = f"""Year {year} - Semester {semester}
                            {subject}\n"""
            if semester_subjects[subject]['prerequisites'] != []:
                p_req = ", ".join(semester_subjects[subject]['prerequisites'])
                f_title += f"Pre-Req: {p_req}\n"
            if semester_subjects[subject]['corequisites'] != []:
                c_req = ", ".join(semester_subjects[subject]['corequisites'])
                f_title += f"Co-Req: {c_req}\n"
            f_title += f"""Credit: {semester_subjects[subject]['credit_unit']}
                            Care Taker: {semester_subjects[subject]['care_taker']}"""
            net.add_node(
                subject, 
                title = f_title,
                label = subject,
                level = level_map, 
            )
        level_map += 1
    
    for semester, semester_subjects in subjects.items():
        for subject, details in semester_subjects.items():
            for prereq in details['prerequisites']:
                if prereq in all_subjects:
                    net.add_edge(
                        prereq, 
                        subject, 
                        width=4
                    )
            for coreq in details['corequisites']:
                if coreq in all_subjects:
                    net.add_edge(
                        coreq, 
                        subject, 
                        width=3, 
                        dashes=True)
    
    neighbor_map = net.get_adj_list()

    color_map = {
        0:"#e0f7ff", 1:"#b3e5ff", 2:"#80d4ff", 3:"#4dc3ff", 4:"#1ab2ff", 
        5:"#00aaff", 6:"#ff9966", 7:"#ff6633", 8:"#ff3300", 9:"#ff0000", 
        10:"#ff073a", 
    } #e0f7ff, #b3e5ff, #80d4ff, #4dc3ff, #1ab2ff, #00aaff, #ff9966, #ff6633, #ff3300, #ff0000, #ff073a
    
    subjects_only = {}
    for semester_subjects in subjects.values():
        subjects_only.update(semester_subjects)

    phrases=["2nd year standing","3rd year standing","4th year standing"]
    
    for node in net.nodes:
        node["value"] = len(neighbor_map[node["id"]])
        node["color"] = color_map[node["value"]]
        node["labelHighlightBold"] = "true"
        for prerequisite in subjects_only[node['id']]['prerequisites']:
            for phrase in phrases:
                if phrase.lower() == prerequisite.lower():
                    node["shape"] = "star"
                    node["value"] = 10
    return net