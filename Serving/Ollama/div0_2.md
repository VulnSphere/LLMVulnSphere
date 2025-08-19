

code

```go
//convert/convert_llama.go:87
		dim := p.HiddenSize / p.NumAttentionHeads

```


send

```json

    config = {
        "architectures": ["LlamaForCausalLM"],
        "hidden_size": 4096,            
        "num_attention_heads": 0,         # 0
        "n_head": 32,                     
        "vocab_size": 32000,
        "max_position_embeddings": 2048,
        "model_type": "llama",
        "torch_dtype": "float16",
        "transformers_version": "4.21.0",
        "rope_scaling": {
            "rope_type": "llama3",       
            "factor": 8.0,
            "low_freq_factor": 1.0,
            "high_freq_factor": 4.0,
            "original_max_position_embeddings": 8192
        }
    }
```


crash



```
panic: runtime error: integer divide by zero

goroutine 32 [running]:
github.com/ollama/ollama/convert.(*llamaModel).KV(0x140003e20c0, 0x14000613200?)
	/Users/runner/work/ollama/ollama/convert/convert_llama.go:87 +0xb44
github.com/ollama/ollama/convert.ConvertModel({0x10590fec0, 0x14000613200}, 0x140002a6168)
	/Users/runner/work/ollama/ollama/convert/convert.go:251 +0xa68
github.com/ollama/ollama/server.convertFromSafetensors(0x140000fe720, {0x0, 0x0, 0x0}, 0x0, 0x14000612f30)
	/Users/runner/work/ollama/ollama/server/create.go:268 +0x608
github.com/ollama/ollama/server.convertModelFromFiles(0x140000fe720, {0x0, 0x0, 0x0}, 0x0, 0x14000612f30)
	/Users/runner/work/ollama/ollama/server/create.go:160 +0x178
github.com/ollama/ollama/server.(*Server).CreateHandler.func1()
	/Users/runner/work/ollama/ollama/server/create.go:96 +0x108
created by github.com/ollama/ollama/server.(*Server).CreateHandler in goroutine 30
	/Users/runner/work/ollama/ollama/server/create.go:71 +0x6a8
```