# DMIS at BioCreative VII NLMChem Track

This repository is intended to implement our named entity recognition (NER) and named entity normalization (NEN) system developed to handle the Full-text Chemical Identification task introduced in the BioCreative VII challenge.

## Overview & Quick Links

* **Task description**: The full-text chemical identification task involves (1) locating chemical entities (NER) and (2) linking them to predefined identifiers (NEN) in the full text of a paper, including abstract and main body. For detailed information, please visit to the official BC7 website (**[link](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-vii/track-2/)**) or see the overview paper (**[PDF](https://biocreative.bioinformatics.udel.edu/media/store/files/2021/TRACK2_pos_01_BC7_submission_223.pdf)**).
* **System description**: Please check out our papers listed below.
  * **[This paper](https://arxiv.org/abs/2111.10584)**(4 papes) provides a brief description of our system and some ablation results.
  * **[This paper](https://academic.oup.com/database/article/doi/10.1093/database/baac074/6726385)**(8 pages) is an extension of the short system description paper above and is published on ***DATABASE*** in 2022. This paper details the motivation for selecting each system component and method. In addition, the limitations of the current system are discussed through error analysis of the model.

## Requirements
```bash
# Download this project
git clone https://github.com/dmis-lab/bc7-chem-id.git
cd bc7-chem-id

# Create a conda environment
conda create -n bc7 python=3.8
conda activate bc7

# Install all requirements
pip install -r requirements.txt
```

### Download Datasets

You need to download the datasets below and unpack them into the `data` directory (see the file structure below).

* **NLMChem** (**[Download]()**): This dataset comprises 150 full-text articles with annotated chemical entities. The dataset is splitted into 80, 20, and 50 articles for the training, development, and test sets, respectively. Please refer to the paper of Islamaj et al. for details (**[link](https://www.nature.com/articles/s41597-021-00875-1)**). 
* **NLMChem_204** (**[Download]()**): This dataset contains 54 newly annotated articles for use as the hidden test set in the challenge. The training set is the combination of the training and development sets of NLMChem, and the development set is the same as the test set of NLMChem.
* ***NOTE***: XML files are raw full-text level data and are only used to evaluate models using the official challenge evaluation script. The XML data are also available on the challenge website (**[link](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-vii/track-2/)**). JSON files are pre-processed to make them suitable for training sentence-level NER models using the Hugging Face library.

#### File Structure

```bash
bc7-chem-id
└── data
    ├── amino_acids.txt
    ├── NLMChem
        ├── bioc_xml
            ├── dev.BioC.xml
            └── test.BioC.xml
        └── ner_json
            ├── train.json
            ├── dev.json
            └── test.json
    ├── NLMChem_204
        ├── bioc_xml
            ├── dev.BioC.xml
            └── test.BioC.xml
        └── ner_json
            ├── train.json
            ├── dev.json
            └── test.json
```

In addition, we can download our synthetic dataset called **NLMChem_syn** using **[this link](asdf)**, in case you want to augment your training data. The data were automatically generated using synonym replacement with entities randomly sampled from the April 1st, 2021 version of the Comparative Toxicogenomics Database.

### Download Bio-LM
if you want to use the Bio-LM models of Lewis et al. (**[paper link](https://aclanthology.org/2020.clinicalnlp-1.17/)**), you need to download the models' weights from **[this repository](https://github.com/facebookresearch/bio-lm)** and place them in the `pretrained_models` directory (e.g., `pretrained_models/RoBERTa-large-PM-M3-Voc-hf`). Note that we used `RoBERTa-base-PM-M3-Voc-distill-align` for the BioLM-base model and `RoBERTa-large-PM-M3-Voc` for the BioLM-large model in the challenge.

## Named Entity Recognition (NER)
NER consists of the following five steps: (1) training the NER model, (2) making predictions on the test set, (3) refining the predictions using majority voting, (4) converting the refined predictions to the BC7 evaluation format (this includes a post-processing step for mutation names), and (5) evaluating the performance.

```bash
export MODEL_NAME=pubmedbert

# Step 1
make train-ner

# Step 2
make test-ner

# Step 3
make majority-voting

# Step 4
make convert-all

# Step 5
make bc7-eval-ner
```
***NOTE***: We do not plan to implement transfer learning and model ensemble, but we will consider it if requested.

## Named Entity Normalization (NEN)
We will update it soon.

## References

Please cite the papers below if you use our code, model/method, or our synthetic dataset NLMChem-syn or if your work is inspired by ours.

```bash
@article{kim2022full,
  title={Full-text chemical identification with improved generalizability and tagging consistency},
  author={Kim, Hyunjae and Sung, Mujeen and Yoon, Wonjin and Park, Sungjoon and Kang, Jaewoo},
  journal={Database},
  volume={2022},
  year={2022},
  publisher={Oxford Academic}
}
```

```bash
@inproceedings{kim2021improving,
  title={Improving Tagging Consistency and Entity Coverage for Chemical Identification in Full-text Articles},
  author={Kim, Hyunjae and Sung, Mujeen and Yoon, Wonjin and Park, Sungjoon and Kang, Jaewoo},
  booktitle={Proceedings of the seventh BioCreative challenge evaluation workshop},
  year={2021}
}
```

Also, please note that appropriate references must be cited when using the NLMChem corpus or citing BC7 challenge results, etc.
