
#
SEED=42

### Paths
DATA_NAME=NLMChem
DATA_DIR=./data/NER

TRAIN_FILE=$(DATA_DIR)/$(DATA_NAME)/train.json
VALIDATION_FILE=$(DATA_DIR)/$(DATA_NAME)/test.json
TEST_FILE=$(DATA_DIR)/$(DATA_NAME)/test.json

OUTPUT_DIR=outputs

### NER models and hyperparameters
ner-model:
ifeq ($(MODEL_NAME), biobert)
	$(eval MODEL_PATH=dmis-lab/biobert-v1.1)
	$(eval EPOCH=100)
	$(eval LR=1e-5)
	$(eval BATCH_SIZE=24)
else ifeq ($(MODEL_NAME), pubmedbert)
	$(eval MODEL_PATH=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract)
	$(eval EPOCH=100)
	$(eval LR=1e-5)
	$(eval BATCH_SIZE=24)
else ifeq ($(MODEL_NAME), pubmedbert-fulltext)
	$(eval MODEL_PATH=microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext)
	$(eval EPOCH=100)
	$(eval LR=1e-5)
	$(eval BATCH_SIZE=24)
else ifeq ($(MODEL_NAME), biolm-base)
	$(eval MODEL_PATH=pretrained_models/RoBERTa-base-PM-M3-Voc-distill-align-hf)
	$(eval EPOCH=100)
	$(eval LR=1e-5)
	$(eval BATCH_SIZE=24)
else ifeq ($(MODEL_NAME), biolm-large)
	$(eval MODEL_PATH=pretrained_models/RoBERTa-large-PM-M3-Voc-hf)
	$(eval EPOCH=100)
	$(eval LR=1e-5)
	$(eval BATCH_SIZE=16)
else
    $(error Please set MODEL_NAME correctly)
endif

### NER - Training and Evalution ###
train-ner: ner-model
	python run_ner.py \
        --model_name_or_path $(MODEL_PATH) \
        --task_name ner \
        --train_file $(TRAIN_FILE) \
        --validation_file $(VALIDATION_FILE) \
        --test_file $(TEST_FILE) \
        --output_dir $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE) \
        --num_train_epochs=$(EPOCH) \
        --learning_rate=$(LR) \
        --evaluation_strategy=epoch \
        --save_strategy=epoch \
        --save_total_limit=1 \
        --load_best_model_at_end=True \
        --metric_for_best_model=eval_f1 \
        --greater_is_better=True \
        --per_device_train_batch_size=$(BATCH_SIZE) \
        --per_device_eval_batch_size=$(BATCH_SIZE) \
        --do_train \
        --do_eval \

test-ner: ner-model
	python run_ner.py \
        --model_name_or_path $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE) \
        --task_name ner \
        --train_file $(TRAIN_FILE) \
        --validation_file $(VALIDATION_FILE) \
        --test_file $(TEST_FILE) \
        --output_dir $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE) \
        --num_train_epochs=$(EPOCH) \
        --learning_rate=$(LR) \
        --save_steps=10000 \
        --load_best_model_at_end=True \
        --per_device_train_batch_size=$(BATCH_SIZE) \
        --per_device_eval_batch_size=$(BATCH_SIZE) \
        --do_predict \

### Post-processing
# Majority voting
majority-voting: ner-model
	python majority_voting.py \
        --prediction_file $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions.json \
        --test_file $(TEST_FILE) \
        --output_file $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions_maj.json \

# converting model predictions to the BioC format for the official evaluation
# post-processing mutation names
convert_preds: ner-model
	python -u convert_hfjson_to_bioc.py \
    data/BC7T2-NLMChem-corpus_v2.BioC.xml/BC7T2-NLMChem-corpus-test.BioC.xml \
    data/NER/NLMChem/test.json \
    $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions.json \
    $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions_bioc.xml \ 

convert_preds_maj: ner-model
	python -u convert_hfjson_to_bioc.py \
    data/BC7T2-NLMChem-corpus_v2.BioC.xml/BC7T2-NLMChem-corpus-test.BioC.xml \
    data/NER/NLMChem/test.json \
    $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions_maj.json \
    $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions_maj_bioc.xml \ 

convert_all: convert_preds convert_preds_maj

### Evaluation
eval_ner_wo_maj: ner-model
	python bc7_eval/evaluate.py \
    --reference_path data/BC7T2-NLMChem-corpus_v2.BioC.xml/BC7T2-NLMChem-corpus-test.BioC.xml \
    --prediction_path $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions_bioc.xml \
    --evaluation_type span \
    --evaluation_method strict \
    --annotation_type Chemical \

eval_ner_maj: ner-model
	python bc7_eval/evaluate.py \
    --reference_path data/BC7T2-NLMChem-corpus_v2.BioC.xml/BC7T2-NLMChem-corpus-test.BioC.xml \
    --prediction_path $(OUTPUT_DIR)/$(MODEL_NAME)/$(DATA_NAME)/$(SEED)_$(EPOCH)_$(LR)_$(BATCH_SIZE)/test_predictions_maj_bioc.xml \
    --evaluation_type span \
    --evaluation_method strict \
    --annotation_type Chemical \

bc7_eval_ner: eval_ner_wo_maj eval_ner_maj


