from imagedatasetanalyzer.datasets.imagelabeldataset import ImageLabelDataset

if __name__ == "__main__":

    img_dir = r"datasets/busi/images"
    labels_dir = r"datasets/busi/labels"
    output_dir = r"datasets/busi/results"

    imagelabel_dataset = ImageLabelDataset(img_dir=img_dir, label_dir=labels_dir)
    imagelabel_dataset.analyze(verbose=True, similarity_index=["SSIM", "LPIPS"], output=output_dir)

    #image_dataset = ImageDataset(img_dir=img_dir)
    #image_dataset.analyze(similarity_index=None, verbose=False)