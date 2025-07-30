import random
import os
import torch
import numpy as np
from logging import Logger


def set_seed(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def optimizer_to_cuda(optimizer):
    for state in optimizer.state.values():
        for k, v in state.items():
            if torch.is_tensor(v):
                state[k] = v.cuda()
    return optimizer


def allow_tf324torch(config, logger: Logger = None):
    if 'tf32' not in config.__dict__: return
    torch.backends.cuda.matmul.allow_tf32 = config.tf32
    torch.backends.cudnn.allow_tf32 = config.tf32
    if config.tf32:
        if logger is not None: logger.warning('Allow pytorch to use TF-32 to accelerate model')
        else: print('Allow pytorch to use TF-32 to accelerate model')


def clean_version(version):
    return ''.join(c for c in version if c.isdigit() or c == '.')


def version_key(version):
    parts = clean_version(version).split('.')
    return tuple(int(part) for part in parts)


def get_latest_version(versions):
    if not versions:
        return None
    sorted_versions = sorted(versions, key=version_key)
    return sorted_versions[-1]
