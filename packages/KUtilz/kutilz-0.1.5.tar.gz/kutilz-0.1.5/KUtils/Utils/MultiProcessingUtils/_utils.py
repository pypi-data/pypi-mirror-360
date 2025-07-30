import multiprocessing

def proc_name()->str:
    return multiprocessing.current_process().name