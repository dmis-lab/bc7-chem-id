# DMIS at BioCreative VII NLMChem Track

This repository is for implementations of our named entity recognition (NER) and named entity normalization (NEN) systems developed to address Full-text Chemical Identification task.

## Overview & Quick Links

* **Task description**: Full-text Chemical Identification and Indexing in PubMed articles. For detailed information, please visit to the official BC7 website ([link](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-vii/track-2/)).
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
make bc7_eval_ner
```
We do not plan to implement transfer learning and model ensemble, but we will consider it if requested.

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
