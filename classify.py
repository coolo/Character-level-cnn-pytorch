# -*- coding: utf-8 -*-
"""
@author: Viet Nguyen <nhviet1009@gmail.com>
"""
import os
import sys
import glob
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import shutil

from src.utils import *
from src.dataset import MyDataset
from src.character_level_cnn import CharacterLevelCNN


def get_args():
    parser = argparse.ArgumentParser(
        """Implementation of the model described in the paper: Character-level convolutional networks for text classification""")
    parser.add_argument("-a", "--alphabet", type=str,
                        default="""abcdefghijklmnopqrstuvwxyz0123456789,;.!?:'\"/\\|_@#$%^&*~`+-=<>()[]{}""")
    parser.add_argument("-m", "--max_length", type=int, default=1014)
    parser.add_argument("-f", "--feature", type=str, choices=["large", "small"], default="small",
                        help="small for 256 conv feature map, large for 1024 conv feature map")
    parser.add_argument("-i", "--input", type=str, default="input", help="path to input folder")
    args = parser.parse_args()
    return args


def train(opt):
    if torch.cuda.is_available():
      model = torch.load(opt.input)
    else:
      model = torch.load(opt.input, map_location='cpu')
    for fn in glob.glob('/space/SP/dumps/*.txt'):
      test_set = MyDataset(fn, opt.max_length)
      test_generator = DataLoader(test_set)

      model.eval()
      for batch in test_generator:
        te_feature, te_label = batch
        if torch.cuda.is_available():
            te_feature = te_feature.cuda()
            te_label = te_label.cuda()
        with torch.no_grad():
            te_predictions = model(te_feature)
            out = F.softmax(te_predictions, 1)
            weight = torch.argmax(out[0])
            weighti = int(out[0][1].item() * 1000)
            #if weighti > 995 or weighti < 5: continue
            weighti = '%04d' % weighti
            print(True if weight == 1 else False, weighti, fn)
            fn = os.path.basename(fn)
            os.symlink('../dumps/' + fn, '/space/SP/likely-good/' + weighti + '-' + fn)

if __name__ == "__main__":
    opt = get_args()
    train(opt)
