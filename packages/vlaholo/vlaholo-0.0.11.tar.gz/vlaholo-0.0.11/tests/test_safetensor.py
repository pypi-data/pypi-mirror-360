import safetensors

model_file = 'checkpoints/smolvla_base/model.safetensors'

safetensors.torch.load_model(
    model, model_file, strict=strict, device=map_location
)
