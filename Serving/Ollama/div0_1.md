



code

```go
//convert/convert_phi3.go
	kv["phi3.rope.dimension_count"] = p.HiddenSize / cmp.Or(p.NumAttentionHeads, p.NHead)

```

send

```json
    config = {
        "architectures": ["Phi3ForCausalLM"], 
        "hidden_size": 3072,
        "num_attention_heads": 0,        
        "n_head": 0,                      #  -> cmp.Or(0,0) = 0
        "vocab_size": 32064,
        "max_position_embeddings": 4096,
        "model_type": "phi3",
        "torch_dtype": "float16"
    }
```

crash


```

panic: runtime error: integer divide by zero

goroutine 90 [running]:
github.com/ollama/ollama/convert.(*phi3Model).KV(0x140000bedc0, 0x14000793470?)
	/Users/runner/work/ollama/ollama/convert/convert_phi3.go:50 +0x7d8
github.com/ollama/ollama/convert.ConvertModel({0x10392bec0, 0x14000793470}, 0x140007801c0)
	/Users/runner/work/ollama/ollama/convert/convert.go:251 +0xa68
github.com/ollama/ollama/server.convertFromSafetensors(0x1400026f140, {0x0, 0x0, 0x0}, 0x0, 0x14000793230)
	/Users/runner/work/ollama/ollama/server/create.go:268 +0x608
github.com/ollama/ollama/server.convertModelFromFiles(0x1400026f140, {0x0, 0x0, 0x0}, 0x0, 0x14000793230)
	/Users/runner/work/ollama/ollama/server/create.go:160 +0x178
github.com/ollama/ollama/server.(*Server).CreateHandler.func1()
	/Users/runner/work/ollama/ollama/server/create.go:96 +0x108
created by github.com/ollama/ollama/server.(*Server).CreateHandler in goroutine 88
	/Users/runner/work/ollama/ollama/server/create.go:71 +0x6a8

```