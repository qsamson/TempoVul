#!/usr/bin/env python3
"""
Re-runs Stage 4 evaluation only, on the corrected artifact, for one model
per invocation. Stages 1 through 3 are unaffected and reused as-is.

Usage:
  python evaluate_stage4_only.py <model_name>

  where model_name is one of:
    codellama, starcoder2, deepseek, mistral, wizardcoder
"""

import pandas as pd
import torch
import json
import time
import sys
import os
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 else None
if MODEL_NAME is None:
    print("Usage: python evaluate_stage4_only.py <model_name>")
    sys.exit(1)

OUTPUT_DIR = "tempovul_results_stage4_fix"
os.makedirs(OUTPUT_DIR, exist_ok=True)

STAGE4_PROMPT = """You are a security analyst reviewing test results and static analysis findings:

{artifact}

Determine if vulnerabilities are present. Respond with ONLY valid JSON:
{{"vulnerable": true/false, "cwe": "CWE-XXX", "reasoning": "brief explanation"}}

JSON:"""


def extract_json(text):
    """Finds the first complete, balanced JSON object in model output."""
    text = text.strip()
    start = text.find('{')
    if start == -1:
        return None
    brace_count = 0
    in_string = False
    escape_next = False
    for i in range(start, len(text)):
        char = text[i]
        if char == '"' and not escape_next:
            in_string = not in_string
        elif char == '\\' and in_string:
            escape_next = True
            continue
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start:i + 1]
        escape_next = False
    return None


def clean_for_csv(text):
    if not isinstance(text, str):
        return str(text)
    return ' '.join(text.split())


def evaluate_with_model(model, tokenizer, artifact, prompt_template):
    try:
        prompt = prompt_template.format(artifact=artifact[:2000])
        full_prompt = f"""{prompt}

Respond with ONLY valid JSON starting with {{

JSON:"""
        device = next(model.parameters()).device
        inputs = tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_new_tokens=250, temperature=0.1,
                do_sample=False, pad_token_id=tokenizer.eos_token_id
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(full_prompt):].strip()
        json_str = extract_json(response)
        if json_str:
            return json.loads(json_str)
        return {"vulnerable": False, "cwe": "PARSE_ERROR", "reasoning": response[:200]}
    except Exception as error:
        return {"vulnerable": False, "cwe": "ERROR", "reasoning": str(error)[:200]}


def main():
    print("=" * 60)
    print(f"TempoVul Stage 4 evaluation: {MODEL_NAME}")
    print("=" * 60)

    df = pd.read_csv('tempovul_with_artifacts_v2.csv')
    print(f"Loaded {len(df)} samples from corrected artifact file")
    assert 'stage4_testing' in df.columns

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
    )

    model_map = {
        "codellama": "codellama/CodeLlama-7b-Instruct-hf",
        "starcoder2": "bigcode/starcoder2-7b",
        "deepseek": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
        "wizardcoder": "WizardLM/WizardCoder-15B-V1.0"
    }
    model_name = model_map.get(MODEL_NAME)
    if not model_name:
        print(f"Unknown model: {MODEL_NAME}. Choose from: {list(model_map.keys())}")
        sys.exit(1)

    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, quantization_config=quantization_config,
        device_map="auto", torch_dtype=torch.float16, trust_remote_code=True
    )
    print(f"Model loaded on device: {next(model.parameters()).device}")

    checkpoint_file = f"{OUTPUT_DIR}/{MODEL_NAME}_stage4fix_checkpoint.csv"
    if os.path.exists(checkpoint_file):
        results_df = pd.read_csv(checkpoint_file)
        done_ids = set(results_df['sample_id'])
        results = results_df.to_dict('records')
        print(f"Resuming: {len(done_ids)} samples already done")
    else:
        done_ids = set()
        results = []
        print("Starting fresh")

    start_time = time.time()

    for idx in range(len(df)):
        if idx in done_ids:
            continue

        row = df.iloc[idx]

        if idx % 10 == 0:
            elapsed = (time.time() - start_time) / 60
            print(f"[{idx}/{len(df)}] {elapsed:.1f}m elapsed")

        artifact = row['stage4_testing']
        result = evaluate_with_model(model, tokenizer, artifact, STAGE4_PROMPT)
        reasoning_clean = clean_for_csv(result.get('reasoning', ''))

        results.append({
            'sample_id': idx,
            'stage': 4,
            'stage_name': 'stage4',
            'ground_truth': row['label'],
            'category': row['category'],
            'cwe': row.get('cwe', 'N/A'),
            f'{MODEL_NAME}_pred': 1 if result.get('vulnerable', False) else 0,
            f'{MODEL_NAME}_cwe': result.get('cwe', 'N/A'),
            f'{MODEL_NAME}_reasoning': reasoning_clean[:200]
        })

        time.sleep(1)

        if (idx + 1) % 10 == 0:
            pd.DataFrame(results).to_csv(checkpoint_file, index=False)
            print(f"  Checkpoint: {len(results)} evaluations saved")

    results_df = pd.DataFrame(results)
    final_file = f"{OUTPUT_DIR}/{MODEL_NAME}_stage4fix_complete.csv"
    results_df.to_csv(final_file, index=False)

    elapsed = (time.time() - start_time) / 60
    print(f"\nCompleted in {elapsed:.1f} minutes!")
    print(f"Results: {final_file}")
    print(f"Total evaluations: {len(results_df)} (expected 400)")


if __name__ == "__main__":
    main()
