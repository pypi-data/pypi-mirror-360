# Model cache

This folder contains the model weights obtained from training on the datasets of the `curatedMetagenomicData` package, as well as classifiers predictions.

Due to the large size of the files, we deposit them on [Zenodo](https://zenodo.org/records/15736785), where you can download them using the following command:
```bash
wget https://zenodo.org/records/15736785/files/plntree-cache.zip
```
Then, unzip the file in the `taxapln` folder and merge it with the existing `cache` folder:
```bash
unzip plntree-cache.zip
```