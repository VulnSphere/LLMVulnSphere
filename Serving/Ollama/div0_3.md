version: v0.11.4


```go
//convert/convert_mistral.go:64

kv["mistral3.rope.dimension_count"] = p.TextModel.HiddenSize / p.TextModel.NumHiddenLayers

```


send

```json
    config = {
        "architectures": ["Mistral3ForConditionalGeneration"],
        "text_config": {
            "hidden_size": 4096,          
            "num_hidden_layers": 0,       # 0
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

```

crash

```
panic: runtime error: integer divide by zero

goroutine 28 [running]:
github.com/ollama/ollama/convert.(*mistral3Model).KV(0x14000545ba0, 0x14000705360?)
	/Users/runner/work/ollama/ollama/convert/convert_mistral.go:64 +0xa84
github.com/ollama/ollama/convert.ConvertModel({0x1057b3ec0, 0x14000705360}, 0x140007901a0)
	/Users/runner/work/ollama/ollama/convert/convert.go:251 +0xa68
github.com/ollama/ollama/server.convertFromSafetensors(0x1400011bb90, {0x0, 0x0, 0x0}, 0x0, 0x14000705120)
	/Users/runner/work/ollama/ollama/server/create.go:268 +0x608
github.com/ollama/ollama/server.convertModelFromFiles(0x1400011bb90, {0x0, 0x0, 0x0}, 0x0, 0x14000705120)
	/Users/runner/work/ollama/ollama/server/create.go:160 +0x178
github.com/ollama/ollama/server.(*Server).CreateHandler.func1()
	/Users/runner/work/ollama/ollama/server/create.go:96 +0x108
created by github.com/ollama/ollama/server.(*Server).CreateHandler in goroutine 26
	/Users/runner/work/ollama/ollama/server/create.go:71 +0x6a8
```