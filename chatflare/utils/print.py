# Define some ANSI color codes
BOLD = '\033[1m'
RED = '\033[91m'
CYAN = '\033[36m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
END = '\033[0m'  # Reset color

def log_action(action, timestep, level=0): 
    """log action"""
    res = "\t"*level + f"{BOLD}{CYAN}[Executing Action: {action}]{END}"
    print(res)
    log_res = "\t"*level + f"[Executing Action: {action}]\n\n"
    with open("logs/log.txt", "a+") as file: 
        file.write(wrap_text_to_fixed_length(log_res))

def log_pause(level=0): 
    """log pause"""
    res = "\t"*level + f"{BOLD}{RED}[Executing Paused]{END}"
    print(res)
    log_res = "\t"*level + f"[Executing Paused]\n\n"
    with open("logs/log.txt", "a+") as file: 
        file.write(wrap_text_to_fixed_length(log_res))

def log_errors(errors, level=0): 
    """log errors"""
    res = "\t"*level + f"{BOLD}{YELLOW}[Errors]:{END}{errors}"
    print(res)
    log_res = "\t"*level + f"[Errors]:{errors}\n\n"
    with open("logs/log.txt", "a+") as file: 
        file.write(wrap_text_to_fixed_length(log_res))

# def log_pause(level=0): 
#     """log pause"""
#     res = "\t"*level + f"{BOLD}{RED}[Executing Paused]{END}"
#     print(res)

def log_action_res(res): 
    """log action"""
    print("\t>"+f"{CYAN}[Output]:{END}{res}")
    log_res = "\t>"+f"[Output]:{res}\n\n"
    with open("logs/log.txt", "a+") as file: 
        file.write(wrap_text_to_fixed_length(log_res))



def wrap_text_to_fixed_length(text, line_length=200):
    """
    :param text: 
    :param line_length: 
    :return: 
    """
    wrapped_lines = []
    for i in range(0, len(text), line_length):
        wrapped_lines.append(text[i:i + line_length])
    return "\n".join(wrapped_lines) + "\n"

    

COLOR_INCLUDE = f"{BOLD}{CYAN}Include{END}"
COLOR_EXCLUDE = f"{BOLD}{RED}Exclude{END}"