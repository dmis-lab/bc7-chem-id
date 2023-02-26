import collections
import logging
import json
import sys
import os
import re
from typing import List

import bioc

with open("data/amino_acids.txt") as f:
    amino_acids = f.readlines()
    amino_acids_3_letters = [a.split("|")[1] for a in amino_acids]
    amino_acids_1_letters = [a.split("|")[2].strip("\n") for a in amino_acids]


def main():
    if len(sys.argv) < 5:
        print("Usage: <input_bioc_path> <input_hfjson_file> <predictions_file> <output_bioc_path>")
        exit()
    input_path = sys.argv[1]
    sentences_pathname = sys.argv[2]
    predictions_pathname = sys.argv[3]
    output_path = sys.argv[4]

    predictions = read_bio_pred(sentences_pathname, predictions_pathname)
    print("Total number of documents = " + str(len(predictions)))

    if os.path.isdir(input_path):
        if not os.path.isdir(output_path):
            raise RuntimeError("If input path is a directory then output path must be a directory: " + output_path)
        print("Processing directory " + input_path)
        # Process any xml files found
        dir = os.listdir(input_path)
        for item in dir:
            input_filename = input_path + "/" + item
            output_filename = output_path + "/" + item
            if os.path.isfile(input_filename):
                print("Processing file " + input_filename + " to " + output_filename)
                convert_tsv_to_bioc(input_filename, predictions, output_filename)
    elif os.path.isfile(input_path):
        # TODO If output_path exists, it must be a file
        # TODO If output_path does not exist, then its location must be a directory that exists
        if os.path.isdir(output_path):
            raise RuntimeError("If input path is a file then output path may not be a directory: " + output_path)
        print("Processing file " + input_path + " to " + output_path)
        # Process directly
        convert_tsv_to_bioc(input_path, predictions, output_path)
    else:  
        raise RuntimeError("Path is not a directory or normal file: " + input_path)

    print("Done.")

class prediction:
    
    def __init__(self, document_id, type):
        self.document_id = document_id
        self.type = type
        self.tokens = list()
        self.spans = list()
        self.predictions = list()
        
    def append(self, token, span, prediction):
        self.tokens.append(token)
        self.spans.append(span)
        self.predictions.append(prediction)

    def begin(self):
        return self.spans[0][0]

    def end(self):
        return self.spans[-1][1]
        
    def __str__(self):
        return self.document_id + ", " + self.type + ": " + str(spans)

    def __repr__(self):
        return str(self)

def get_prediction_fields(prediction):
    prediction_type = None
    prediction_fields = prediction.split("-")
    prediction_label = prediction_fields[0]
    if len(prediction_fields) > 1:
        prediction_type = prediction_fields[1]
    return prediction_label, prediction_type

def get_predictions(sentence, labels):
    predictions = list()
    document_id = sentence["document_id"]
    tokens = sentence["tokens"]
    spans = sentence["spans"]
    current_prediction = None
    for token, span, label in zip(tokens, spans, labels):
        prediction_label, prediction_type = get_prediction_fields(label)
        #print("token = " + token)
        #print("span = " + str(span))
        #print("label = " + label)
        #print("prediction_label = " + prediction_label)
        #print("prediction_type = " + str(prediction_type))
        # Check if we need to close current_prediction
        if not current_prediction is None:
            if prediction_label == "B" or current_prediction.type != prediction_type:
                predictions.append(current_prediction)
                current_prediction = None
            elif prediction_label == "I" and current_prediction.type == prediction_type:
                current_prediction.append(token, span, prediction)
        # Check if we need to add a new prediction
        # current_prediction will be None here unless extending an existing prediction
        if current_prediction is None:
            if prediction_label != "O":
                current_prediction = prediction(document_id, prediction_type)
                current_prediction.append(token, span, prediction)
    if not current_prediction is None:
        predictions.append(current_prediction)
    return document_id, predictions

def read_bio_pred(sentences_pathname, predictions_pathname):
    
    sentences_list = list()
    with open(sentences_pathname) as sentences_file:
        for line in sentences_file:
            sentence = json.loads(line)
            sentences_list.append(sentence)
    
    with open(predictions_pathname) as predictions_file:
        predictions_list = json.load(predictions_file)
    
    predictions = collections.defaultdict(list)
    for sentence, labels in zip(sentences_list, predictions_list):
        document_id, sentence_predictions = get_predictions(sentence, labels)
        predictions[document_id].extend(sentence_predictions)

    return predictions
       
def convert_tsv_to_bioc(input_bioc_file, predictions, output_bioc_file):
    logger = logging.getLogger(__name__)

    with open(input_bioc_file, encoding='utf8') as fp:
        collection = bioc.load(fp)

    for doc in collection.documents:
        doc_predictions = predictions.get(doc.id)
        for passage in doc.passages:
            passage.annotations.clear()
        for i, prediction in enumerate(doc_predictions):
            found = False
            for passage in doc.passages:
                if passage.offset <= prediction.begin() and prediction.end() <= passage.offset + len(passage.text):
                    begin = prediction.begin()
                    end = prediction.end()
                    
                    predicted_text = passage.text[begin - passage.offset: end - passage.offset]

                    begins, ends, texts = [],[],[]
                    ## post-processing 
                    # check if the text corresponds to name patterns that we define
                    first_3_letters = predicted_text[:3]
                    last_3_letters = predicted_text[-3:]
                    except_first_and_last_3_letters = predicted_text[3:-3]
                    except_first_3_letters = predicted_text[3:]
                    except_last_3_letters = predicted_text[:-3]
                    
                    # pattern 1: serum Ca / Mg
                    if (predicted_text == "sCa") or (predicted_text == "sMg"):
                        texts.append(predicted_text[1:])
                        begins.append(begin+1)
                        ends = [end]
                    # pattern 2: {amino_3_letters} + {num} + {amino_3_letters}
                    elif (first_3_letters in amino_acids_3_letters) and (last_3_letters in amino_acids_3_letters) and (except_first_and_last_3_letters.isnumeric()):
                        texts.append(first_3_letters)
                        texts.append(last_3_letters)
                        begins.append(begin)
                        begins.append(end-3)
                        ends.append(begin+3)
                        ends.append(end)
                    # pattern 3: {amino_3_letter} + {num}
                    elif (first_3_letters in amino_acids_3_letters) and (except_first_3_letters.isnumeric()):
                        texts.append(first_3_letters)
                        begins.append(begin)
                        ends.append(begin+3)
                    # pattern 4: {num} + {amino_3_letter}
                    elif (last_3_letters in amino_acids_3_letters) and (except_last_3_letters.isnumeric()):
                        texts.append(last_3_letters)
                        begins.append(end-3)
                        ends.append(end)
                    else:
                        texts = [predicted_text]
                        begins = [begin]
                        ends = [end]

                    for b, e, t in zip(begins, ends, texts):
                        ann = bioc.BioCAnnotation()
                        ann.id = '{}'.format(i)
                        ann.add_location(bioc.BioCLocation(b, e-b))
                        ann.text = t
                        ann.infons['type'] = prediction.type
                        passage.add_annotation(ann)
                    
                    ##
                    
                    found = True
                    break
            if not found:
                logger.warning('%s: Cannot find ann %s in the file', prediction.document_id, prediction)
            
    with open(output_bioc_file, 'w', encoding='utf8') as fp:
        bioc.dump(collection, fp)

if __name__ == '__main__':
    main()
