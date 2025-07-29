#!/usr/bin/env python3
"""
Standalone dialog tree validation script
Run this before launching the game to validate the dialog tree
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dialog_engine import DialogEngine
from pet import Pet

def main():
    """Run comprehensive dialog validation"""
    print("E-Pet Dialog Tree Validator")
    print("=" * 40)
    
    try:
        # Load dialog engine
        dialog = DialogEngine()
        print(f"✓ Loaded dialog tree from: {dialog.dialog_file}")
        
        # Run basic validation
        print("\n1. Basic Structure Validation")
        print("-" * 30)
        errors = dialog.validate_dialog_tree()
        
        if errors:
            print(f"❌ Found {len(errors)} validation errors:")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")
            return False
        else:
            print("✓ Basic structure validation passed")
        
        # Test conditional routing
        print("\n2. Conditional Routing Test")
        print("-" * 30)
        routing_errors = test_conditional_routing(dialog)
        
        if routing_errors:
            print(f"❌ Found {len(routing_errors)} routing errors:")
            for i, error in enumerate(routing_errors[:5], 1):  # Show first 5
                print(f"   {i}. {error}")
            if len(routing_errors) > 5:
                print(f"   ... and {len(routing_errors) - 5} more errors")
            return False
        else:
            print("✓ Conditional routing test passed")
        
        # Test node accessibility
        print("\n3. Node Accessibility Test")
        print("-" * 30)
        accessibility_errors = test_node_accessibility(dialog)
        
        if accessibility_errors:
            print(f"❌ Found {len(accessibility_errors)} accessibility issues:")
            for i, error in enumerate(accessibility_errors, 1):
                print(f"   {i}. {error}")
        else:
            print("✓ All nodes are accessible")
        
        # Summary
        print("\n" + "=" * 40)
        total_errors = len(errors) + len(routing_errors) + len(accessibility_errors)
        
        if total_errors == 0:
            print("🎉 All validation checks passed!")
            print("Dialog tree is ready for game launch.")
            return True
        else:
            print(f"❌ Total errors found: {total_errors}")
            print("Please fix errors before launching the game.")
            return False
            
    except Exception as e:
        print(f"❌ Validation failed with exception: {e}")
        return False

def test_conditional_routing(dialog):
    """Test conditional routing with various pet states"""
    errors = []
    
    try:
        test_pet = Pet()
        
        # Test states covering edge cases
        test_states = [
            {"health": 0, "wealth": 0, "happiness": 0, "despair": 0, "age": 0},
            {"health": 1, "wealth": 1, "happiness": 1, "despair": 1, "age": 1},
            {"health": 3, "wealth": 3, "happiness": 3, "despair": 3, "age": 3},
            {"health": 5, "wealth": 5, "happiness": 5, "despair": 5, "age": 5},
            {"health": 10, "wealth": 10, "happiness": 10, "despair": 10, "age": 10},
        ]
        
        conditional_nodes = 0
        
        for node_id, node_data in dialog.dialog_tree.items():
            if "options" not in node_data:
                continue
            
            for i, option in enumerate(node_data["options"]):
                if "next" not in option or not isinstance(option["next"], dict):
                    continue
                
                conditional_nodes += 1
                
                for state in test_states:
                    # Set test pet attributes
                    for attr, value in state.items():
                        setattr(test_pet, attr, value)
                    
                    try:
                        result_node = dialog.evaluate_conditional_routing(option["next"], test_pet)
                        
                        if result_node not in dialog.dialog_tree:
                            errors.append(f"Node '{node_id}' option {i} routes to non-existent '{result_node}' with state {state}")
                    
                    except Exception as e:
                        errors.append(f"Node '{node_id}' option {i} routing failed with state {state}: {e}")
        
        print(f"   Tested {conditional_nodes} conditional routes with {len(test_states)} different pet states")
        
    except Exception as e:
        errors.append(f"Conditional routing test failed: {e}")
    
    return errors

def test_node_accessibility(dialog):
    """Test that all nodes can be reached from main_menu"""
    errors = []
    
    try:
        # Find all reachable nodes starting from main_menu
        reachable = set()
        to_visit = ["main_menu"]
        
        while to_visit:
            current = to_visit.pop(0)
            if current in reachable:
                continue
            
            reachable.add(current)
            
            if current not in dialog.dialog_tree:
                continue
            
            node_data = dialog.dialog_tree[current]
            if "options" not in node_data:
                continue
            
            for option in node_data["options"]:
                if "next" not in option:
                    continue
                
                next_node = option["next"]
                if isinstance(next_node, str):
                    if next_node not in reachable:
                        to_visit.append(next_node)
                elif isinstance(next_node, dict):
                    for target in next_node.values():
                        if target not in reachable:
                            to_visit.append(target)
        
        # Check for unreachable nodes
        all_nodes = set(dialog.dialog_tree.keys())
        unreachable = all_nodes - reachable
        
        for node in unreachable:
            errors.append(f"Node '{node}' is not reachable from main_menu")
        
        print(f"   Found {len(reachable)} reachable nodes out of {len(all_nodes)} total")
        
    except Exception as e:
        errors.append(f"Node accessibility test failed: {e}")
    
    return errors

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)