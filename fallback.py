from tqdm import tqdm

def alt(opt,fallback):
    return fallback if opt is None else opt
