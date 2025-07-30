# presets.py
import json
import re
from pathlib import Path

BUILTIN_PRESETS = {
    "react-tailwind": {
        "ARCHITECTURE": "React + Tailwind CSS",
        "FOCUS": "UI layout",
        "PATTERNS": "context_aware_generation, state_anchoring",
        "DEFAULT_PATTERN": "context_aware_generation"
    },
    "django-api": {
        "ARCHITECTURE": "Django REST Framework",
        "FOCUS": "API endpoints and serializers",
        "PATTERNS": "bug_fix_precision",
        "DEFAULT_PATTERN": "bug_fix_precision"
    },
    "bash-script": {
        "ARCHITECTURE": "Shell scripting",
        "FOCUS": "Automation and CLI behavior",
        "PATTERNS": "context_aware_generation",
        "DEFAULT_PATTERN": "context_aware_generation"
    }
}

CUSTOM_PRESET_FILE = Path.home() / ".cliops_presets.json"

def suggest_preset_from_prompt(prompt: str) -> str | None:
    prompt = prompt.lower()
    if "tailwind" in prompt or "jsx" in prompt:
        return "react-tailwind"
    if "endpoint" in prompt or "serializer" in prompt or "django" in prompt:
        return "django-api"
    if re.search(r'#!/bin/bash|\\.sh|chmod|\\bcron\\b', prompt):
        return "bash-script"
    return None

def save_custom_preset(name, preset_dict):
    if CUSTOM_PRESET_FILE.exists():
        with open(CUSTOM_PRESET_FILE, 'r') as f:
            all_presets = json.load(f)
    else:
        all_presets = {}
    all_presets[name] = preset_dict
    with open(CUSTOM_PRESET_FILE, 'w') as f:
        json.dump(all_presets, f, indent=2)
    print(f"✅ Custom preset '{name}' saved.")

def apply_preset_interactive(suggested_name, state):
    print(f"\n🤖 Suggested preset based on your prompt: {suggested_name}")
    use = input("Would you like to use this preset? (y/n): ").strip().lower()
    if use != 'y':
        print("❌ Preset declined.")
        return

    fields = {}
    for key in BUILTIN_PRESETS.get(suggested_name, {}):
        default = BUILTIN_PRESETS[suggested_name][key]
        user_val = input(f"{key} [{default}]: ").strip()
        fields[key] = user_val or default
        state.set(key, fields[key])

    save = input("Save this as a custom preset? (y/n): ").strip().lower()
    if save == 'y':
        name = input("Enter a name for your preset: ").strip()
        if name:
            save_custom_preset(name, fields)

def list_all_presets():
    print("\n📦 Available Presets:")
    for name in BUILTIN_PRESETS:
        print(f"  - {name} (built-in)")
    if CUSTOM_PRESET_FILE.exists():
        with open(CUSTOM_PRESET_FILE, 'r') as f:
            custom = json.load(f)
            for name in custom:
                print(f"  - {name} (custom)")


def apply_named_preset(name, state):
    preset = BUILTIN_PRESETS.get(name)
    if not preset and CUSTOM_PRESET_FILE.exists():
        with open(CUSTOM_PRESET_FILE, 'r') as f:
            preset = json.load(f).get(name)

    if not preset:
        print(f"❌ Preset '{name}' not found.")
        return

    for key, value in preset.items():
        state.set(key, value)
    print(f"✅ Preset '{name}' applied.")
