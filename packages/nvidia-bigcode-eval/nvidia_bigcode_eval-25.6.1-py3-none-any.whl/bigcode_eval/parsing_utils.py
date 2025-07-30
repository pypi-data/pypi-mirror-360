import json
import argparse


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def str2json(args_str: str | None) -> dict:
    if args_str is not None:  
        model_kwargs = json.loads(args_str)
    else:
        model_kwargs = {}
    return model_kwargs