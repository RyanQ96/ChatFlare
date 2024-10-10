from typing import List
from chatflare.tracker.base import Branch

def visualize_branches(branches: List[Branch]): 
    """Require branches must share some common commit"""
    levels = [] 
    num_of_branches = len(branches)
    max_num_commits = max([b.length for b in branches])    
    
    for i in range(max_num_commits): 
        level = [] 
        for b in branches: 
            if i < b.length: 
                    level.append(b.commits[i])
            else:
                level.append("_")
        levels.append(level)
        
    branches_display_str = "" 
    for level_id in range(len(levels)):
        layer_str = ""
        arrows_1 = ""
        arrows_2 = ""
        current = None 
        for c_id in range(len(levels[level_id])): 
            c = levels[level_id][c_id]
            if c_id == 0: 
                if c == "_": 
                    layer_str += " "*17
                    if level_id != len(levels) - 1:
                        if level_id != len(levels) - 1:
                            arrows_1 += " "*15
                            arrows_2 += " "*15
                else:
                    layer_str += f"{c}{' '*2}"
                    current = c
                    if level_id != len(levels) - 1:
                        arrows_1 += "     Ʌ         "
                        arrows_2 += "     |         "
            else: 
                if c == current: 
                    if level_id + 1 < len(levels) and levels[level_id + 1][c_id] == levels[level_id + 1][c_id - 1]:  
                        layer_str += " "*17
                        if level_id != len(levels) - 1:
                            arrows_1 += " "*15
                            arrows_2 += " "*15
                    elif level_id + 1 < len(levels) and levels[level_id + 1][c_id] != levels[level_id + 1][c_id - 1]: 
                            layer_str += " "*17
                            if level_id != len(levels) - 1:
                                arrows_1 += " /" + " "*15
                                arrows_2 += "/ " + " "*15
                else:
                    if c == "_":
                        if levels[level_id - 1][c_id] == "_":
                            layer_str += " "*17
                            if level_id != len(levels) - 1:
                                arrows_1 += " "*15
                                arrows_2 += " "*15
                        else:
                            layer_str += f"{'END'.ljust(15, ' ')}{' '*2}"
                            current = None 
                            if level_id != len(levels) - 1:
                                arrows_1 += " "*15
                                arrows_2 += " "*15
                    else:
                        layer_str += f"{c}{' '*2}"
                        current = c 
                        if level_id != len(levels) - 1:
                            arrows_1 += "       Ʌ         "
                            arrows_2 += "       |         "
                    current = c
        if level_id != len(levels) - 1:
            branches_display_str = f"{arrows_1}\n{arrows_2}\n{layer_str}\n{branches_display_str}"
        else: 
            branches_display_str = f"{layer_str}\n{branches_display_str}"
            
    branch_titles = ""
    sep_lines = ""
    for b in branches:
        branch_titles += (b.branch_name.ljust(15, ' ') if len(b.branch_name) <= 15 else b.branch_name[:12] + "...") + " "*2
        sep_lines += ("="*15 + " "*2)
    
    branches_display_str = f"{branch_titles}\n{sep_lines}\n{branches_display_str}"
    print(branches_display_str)