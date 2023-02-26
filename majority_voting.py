import argparse
import os
import copy
import json
import pickle
import numpy as np
from collections import Counter, OrderedDict
from tqdm import tqdm

def majority_voting(poss, negs, min_freq=40, min_len=3):
    result = {}
    for m in list(set(list(poss.keys()) + list(negs.keys()))):
        # skip short mentions
        if sum([len(c) for c in m.split()]) >= min_len:
            # we should do the majority voting when inconsistency occurs
            if m in poss.keys() and m in negs.keys():
                # the total frequency of a mention should be greater than the threshold
                if poss[m] + negs[m] >= min_freq:
                    # voting
                    result[m] = True if poss[m] >= negs[m] else False
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--prediction_file', type=str, required=True, help="")
    parser.add_argument('--test_file', type=str, required=True, help="")
    parser.add_argument('--output_file', type=str, default="", help="")
    args = parser.parse_args()

    ## load predictions
    fulltext_preds = OrderedDict()
    
    with open(args.prediction_file) as f:
        preds = json.load(f)
    
    with open(args.test_file) as g:
        l_i = -1
        for line in list(g):
            l_i += 1
            json_line = json.loads(line)
            json_line["preds"] = preds[l_i]
            pmid = json_line["document_id"]

            if pmid not in fulltext_preds.keys():
                fulltext_preds[pmid] = []
            fulltext_preds[pmid].append(json_line)
    
    ## main process
    refined_preds = []
    
    # Step 1: construct a vocab based on the model's predictions
    for pmid, doc in tqdm(fulltext_preds.items()):
        vocab = Counter()
        
        for d in doc:
            in_entity = False
            entity_tokens = []
            for p_i, p in enumerate(d['preds']):
                if p == "B-Chemical":
                    if in_entity:
                        # end
                        vocab[" ".join(entity_tokens)] += 1
                        entity_tokens = []
                        in_entity = False
                    # start
                    entity_tokens.append(d['tokens'][p_i])
                    in_entity = True
                    if p_i == len(d['preds'])-1:
                        vocab[" ".join(entity_tokens)] += 1
                elif p == "I-Chemical":
                    entity_tokens.append(d['tokens'][p_i])
                    in_entity = True
                    if p_i == len(d['preds'])-1:
                        vocab[" ".join(entity_tokens)] += 1
                elif p == "O":
                    if in_entity:
                        # end
                        vocab[" ".join(entity_tokens)] += 1
                        entity_tokens = []
                        in_entity = False

        # Step 2: get phrases that are in the vocab but not predicted by the model
        neg_preds = Counter()
        for mention, freq in vocab.items():
            for d in doc:
                for i in range(len(d['tokens'])-len(mention.split())):
                    if d['tokens'][i:i+len(mention.split())] == mention.split() and sum([1 for l in d['preds'][i:i+len(mention.split())] if l != "O"]) == 0:
                        neg_preds[mention] += 1
        
        # Step 3: perform majority voting
        voting_result = majority_voting(vocab, neg_preds)
        
        # Step 4: refine the model predictions based on the majority-voting results
        for d in doc:
            pred_tmp = copy.deepcopy(d["preds"])
            for target, decision in voting_result.items():
                for i in range(len(d['preds'])-len(target.split())):
                    if d['tokens'][i:i+len(target.split())] == target.split():
                        for j in range(i, i+len(target.split())):
                            if decision == False:
                                pred_tmp[j] = "O"
                            else:
                                if j == i: pred_tmp[j] = "B-Chemical"
                                else: pred_tmp[j] = "I-Chemical"
                assert len(pred_tmp) == len(d['preds'])
        
            #
            refined_pred = {"preds": copy.deepcopy(pred_tmp)}
            for k, v in d.items():
                if k == 'preds': continue
                refined_pred = {k: copy.deepcopy(v)}
            refined_preds.append(pred_tmp)
        
    # save the refined results
    with open(args.output_file, 'w') as f:
        json.dump(refined_preds, f)

