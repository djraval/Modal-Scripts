# modal.build

    
    
    def build(
        _warn_parentheses_missing=None, *, force: bool = False, timeout: int = 86400
    ) -> Callable[[Union[_PartialFunction, NullaryMethod]], _PartialFunction]:

Copy

Decorator for methods that execute at _build time_ to create a new Image
layer.

**Deprecated** : This function is deprecated. We recommend using
`modal.Volume` to store large assets (such as model weights) instead of
writing them to the Image during the build process. For other use cases, you
can replace this decorator with the `Image.run_function` method.

**Usage**

    
    
    @app.cls(gpu="A10G")
    class AlpacaLoRAModel:
        @build()
        def download_models(self):
            model = LlamaForCausalLM.from_pretrained(
                base_model,
            )
            PeftModel.from_pretrained(model, lora_weights)
            LlamaTokenizer.from_pretrained(base_model)

Copy

