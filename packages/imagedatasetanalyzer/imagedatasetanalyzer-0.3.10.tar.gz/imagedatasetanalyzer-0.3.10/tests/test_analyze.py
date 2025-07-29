import sys
import os
import torch
import numpy as np


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from imagedatasetanalyzer.src.datasets.imagedataset import ImageDataset
from imagedatasetanalyzer.src.datasets.imagelabeldataset import ImageLabelDataset

if __name__ == "__main__":

    img_dir = r"C:\Users\joortif\Desktop\datasets\Completos\BUSI\full\images"
    labels_dir = r"C:\Users\joortif\Desktop\datasets\Completos\BUSI\full\labels"
    output_dir = r"C:\Users\joortif\Desktop\resultados\results_busi"

    imagelabel_dataset = ImageLabelDataset(img_dir=img_dir, label_dir=labels_dir)
    imagelabel_dataset.analyze(verbose=True, similarity_index=["SSIM", "LPIPS"], output=output_dir)

    

    image_dataset = ImageDataset(img_dir=img_dir)
    image_dataset.analyze(similarity_index=None, verbose=False)