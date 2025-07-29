#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(override=True)

# Import the providers
from wraipperz.api.llm import (
    LMStudioProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    DeepSeekProvider,
    AIManagerSingleton
)

def print_model_lists(format_as_code=True):
    """
    Print out all available model names for all providers.
    
    Args:
        format_as_code: If True, formats the output as Python code ready to paste
    """
    # Get the AIManager instance that should have all providers initialized
    ai_manager = AIManagerSingleton.get_instance()
    
    # For each provider, print the models
    for provider_name, provider in ai_manager.providers.items():
        if format_as_code:
            print(f"\n# {provider_name} supported models")
            print(f"supported_models = [")
            for model in sorted(provider.supported_models):
                print(f'    "{model}",')
            print("]")
        else:
            print(f"\n{provider_name} models:")
            for model in sorted(provider.supported_models):
                print(f"  {model}")
    
    # Also print a combined list of all models
    if format_as_code:
        print("\n# All supported models combined")
        print("all_supported_models = [")
        all_models = []
        for provider in ai_manager.providers.values():
            all_models.extend(provider.supported_models)
        for model in sorted(all_models):
            print(f'    "{model}",')
        print("]")

def print_provider_model_counts():
    """Print the count of models for each provider"""
    ai_manager = AIManagerSingleton.get_instance()
    
    print("\nModel counts by provider:")
    for provider_name, provider in ai_manager.providers.items():
        print(f"{provider_name}: {len(provider.supported_models)} models")
    
    # Total count
    total = sum(len(provider.supported_models) for provider in ai_manager.providers.values())
    print(f"Total models available: {total}")

if __name__ == "__main__":
    print("Fetching available models for all configured providers...")
    print("(This may take a moment as it connects to provider APIs)")
    
    # Print the model lists formatted as code
    print_model_lists(format_as_code=True)
    
    # Print model counts
    print_provider_model_counts()
    
    print("\nNote: To use this script, make sure you have the necessary API keys in your .env file")