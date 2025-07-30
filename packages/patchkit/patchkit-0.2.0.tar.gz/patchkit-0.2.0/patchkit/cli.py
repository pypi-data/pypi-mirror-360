from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import sys
import json
from b64tensors import encode, decode
import os
import math
import argparse

warning_cnt = 0

def apply_diff(model_path, diff_file_path, output_path):
    """Apply differences from diff file to a model"""
    global warning_cnt
    # Load the base model
    print(f"Loading model from: {model_path}")
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    
    # Load the diff file
    print(f"Loading diff from: {diff_file_path}")
    with open(diff_file_path, "r", encoding="utf-8") as f:
        diff_data = json.loads(f.read().strip())
    
    # Extract parameters
    orig_model_name = diff_data["orig_model_name"]
    apply_params = diff_data["apply_params"]
    scale = apply_params["scale"]
    patch = diff_data["patch"]
    
    print(f"Original model name: {orig_model_name}")
    print(f"Apply scale: {scale}")
    print(f"Number of layers to patch: {len(patch)}")
    
    # Apply differences with no gradients
    with torch.no_grad():
        for name, param in model.named_parameters():
            if name in patch:
                patch_data = patch[name]
                
                # Decode the tensors
                positions = decode(patch_data["p"]).long()
                old_values = decode(patch_data["o"])
                diff_values = decode(patch_data["d"])
                
                print(f"\nApplying patch to layer: {name}")
                print(f"  Number of positions: {len(positions)}")
                
                # Apply each difference
                for i, (pos, old_val, diff_val) in enumerate(zip(positions, old_values, diff_values)):
                    # Convert position to tuple
                    pos_tuple = tuple(pos.tolist())
                    
                    # Get current value
                    current_val = param[pos_tuple].item()
                    
                    # Calculate new value
                    new_val = old_val + (diff_val * scale)
                    if abs(current_val - old_val) > 0.00001:
                        warning_cnt += 1
                        print(f"WARNING: Mismatch between new and old value at position {pos_tuple}: In Model: {current_val:.6f}, In Diff: {old_val:.6f}")
                    
                    # Apply the change
                    param[pos_tuple] = new_val
                    
                    # Print progress for first few changes
                    if i < 5:
                        print(f"    Position {pos_tuple}: {current_val:.6f} -> {new_val:.6f} (diff: {diff_val:.6f})")
                
                print(f"  Applied {len(positions)} changes to {name}")
    
    # Save the modified model
    print(f"\nSaving modified model to: {output_path}")
    model.save_pretrained(output_path)
    
    # Also save the tokenizer if it exists
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        tokenizer.save_pretrained(output_path)
        print(f"Tokenizer also saved to: {output_path}")
    except:
        print("No tokenizer found or failed to save tokenizer")

    if warning_cnt > 0:
        print(f"WARNING: {warning_cnt} mismatches found")
    else:
        print("DONE!")

def cmd_patch(args):
    """Handle the patch subcommand"""
    # Check if files exist
    if not os.path.exists(args.model_path):
        print(f"Error: Model path does not exist: {args.model_path}")
        sys.exit(1)
    
    if not os.path.exists(args.diff_file):
        print(f"Error: Diff file does not exist: {args.diff_file}")
        sys.exit(1)
    
    # Apply the diff
    apply_diff(args.model_path, args.diff_file, args.output_path)
    

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='patchkit',
        description='A toolkit to apply and revert patches on models.'
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # patch subcommand
    patch_parser = subparsers.add_parser('patch', help='Apply a patch to a model')
    patch_parser.add_argument('model_path', help='Path to the base model')
    patch_parser.add_argument('diff_file', help='Path to the diff file')
    patch_parser.add_argument('output_path', help='Path to save the patched model')
    patch_parser.set_defaults(func=cmd_patch)
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command provided, show help
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    # Execute the command
    args.func(args)

if __name__ == "__main__":
    main()
