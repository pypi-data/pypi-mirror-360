from anc.data.anc_dataloader import AncDataLoader
from anc.data.processors.llm_processor import PretrainProcessor
from anc.data.anc_composer import SeqSplitConfig
from anc.data.parquet_dataset import ParquetDataset
from transformers import AutoTokenizer
import concurrent.futures
from functools import partial
import json
import os

def get_token_count(ds_path, tokenizer_path):
    try:
        ds = ParquetDataset(ds_path)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        tokens = 0
        for item in ds:
            tokens += len(tokenizer.encode(item['content']))
        print(f"Processed {ds_path}: {tokens} tokens")
        return tokens
    except Exception as e:
        print(f"Error processing {ds_path}: {e}")
        return 0

def get_dataset_paths(path):
    dataset_paths = []
    if os.path.isdir(path) and 'eval' in os.listdir(path):
        dataset_paths.append(path)
        return dataset_paths

    # Add all subdirectories as dataset paths
    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    for subdir in subdirs:
        subdir_path = os.path.join(path, subdir)
        dataset_paths.extend(get_dataset_paths(subdir_path))

    return dataset_paths


def count_eval_tokens(dataset_dir, tokenizer_path, max_workers=4):
    eval_dir = os.path.join(dataset_dir, "eval")

    if not os.path.exists(eval_dir):
        print(f"Eval directory not found in {dataset_dir}")
        return 0

    parquet_files = []
    for file in os.listdir(eval_dir):
        if file.endswith(".snappy.parquet"):
            parquet_files.append(os.path.join(eval_dir, file))

    if not parquet_files:
        print(f"No parquet files found in {eval_dir}")
        return 0

    print(f"Found {len(parquet_files)} parquet files in {eval_dir}")

    total_tokens = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(get_token_count, path, tokenizer_path): path 
            for path in parquet_files
        }

        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                token_count = future.result()
                total_tokens += token_count
                print(f"Processed {path}: {token_count} tokens")
            except Exception as e:
                print(f"Error processing {path}: {e}")

    return total_tokens


# Process all eval dataset token count and dump to json file [offline use only].
#   a. If the key of tokenizer in json file, read the token count from the json file.
#   b. If the key of tokenizer not in json file, calculate the token count and dump to the json file.
#   c. For the eval dataset, the token count is the sum of all the token count of the parquet files in the eval folder. 
def process_all_datasets(dataset_list, tokenizer_path):
    results = {}

    for dataset_dir in dataset_list:
        dataset_name = os.path.basename(dataset_dir)
        print(f"\nProcessing dataset: {dataset_name}")

        eval_dir = os.path.join(dataset_dir, "eval")
        if os.path.exists(eval_dir):
            json_path = os.path.join(eval_dir, "token_count.json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        existing_data = json.load(f)
                    if tokenizer_path in existing_data:
                        token_count = existing_data[tokenizer_path]
                        print(f"Using existing token count for {dataset_name}: {token_count}")
                        results[dataset_dir] = token_count
                        continue
                except Exception as e:
                    print(f"Error reading existing JSON: {e}")

        token_count = count_eval_tokens(dataset_dir, tokenizer_path)
        results[dataset_dir] = token_count

        if os.path.exists(eval_dir):
            json_path = os.path.join(eval_dir, "token_count.json")

            existing_data = {}
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        existing_data = json.load(f)
                    print(f"Found existing token count file at {json_path}")
                except json.JSONDecodeError:
                    print(f"Waring: reading existing JSON file {json_path}, will create new one")

            existing_data[tokenizer_path] = token_count
            
            with open(json_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
            print(f"Updated token count at {json_path}")

    print("\n===== Token Count Summary =====")
    for dataset_dir, count in results.items():
        print(f"{os.path.basename(dataset_dir)}: {count} tokens")

    return results


def gen_eval_data_cache_meta(dataset_dir, tokenizer_path):
    dataset_paths = get_dataset_paths(file_dir)
    process_all_datasets(dataset_paths, tokenizer_path)


# Online use.
def get_num_iterations(ds_path, tokenizer_path, global_batch_size, seq_len):
    num_workers = min(16, len(ds_path))
    total_token_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_path = {
            executor.submit(get_token_count, path, tokenizer_path): path 
            for path in ds_path
        }

        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                token_count = future.result()
                total_token_count += token_count
                print(f"Processed eval dataset {path}: {token_count} tokens")
            except Exception as e:
                print(f"Error processing eval dataset {path}: {e}")
    return total_token_count // (global_batch_size * seq_len)


# Online use.
def get_num_iterations_from_cache(file_dir, tokenizer_path):
    token_count = 0
    cached_dataset = 0
    dataset_paths = get_dataset_paths(file_dir)
    for dataset_path in dataset_paths:
        if os.path.exists(os.path.join(dataset_path, "eval", "token_count.json")):
            with open(os.path.join(dataset_path, "eval", "token_count.json"), 'r') as f:
                data = json.load(f)
                if tokenizer_path in data:
                    token_count += int(data.get(tokenizer_path, 0))
                    cached_dataset += 1
    return token_count, cached_dataset, len(dataset_paths)


# For testing.
if __name__ == "__main__":
    file_dir = "/mnt/project/llm/data/pretrain/D0_8/"
    #file_dir = "/mnt/project/llm/users/xug/D0_8/rentry_web_stories"
    
    if not os.path.exists(file_dir):
        raise FileNotFoundError(f"Dataset directory {file_dir} does not exist")
    
    dataset_paths = get_dataset_paths(file_dir)
    print(len(dataset_paths), dataset_paths)

    #process_all_datasets(dataset_paths, "/mnt/project/llm/ckpt/tokenizer/ocean_deepseek_v2")
    count, cached_dataset, total_dataset = get_num_iterations_from_cache(file_dir, "/mnt/project/llm/ckpt/tokenizer/ocean_deepseek_v2")
    print(count, cached_dataset, total_dataset, cached_dataset / total_dataset)
    #paths = ["/mnt/project/llm/pretrain_datasets/pretrain_dataset_v0_7/thePile-BooksCorpus2/eval/part-00000-22d7774e-fc6c-4076-ab62-64d6249f017f-c000.snappy.parquet"]