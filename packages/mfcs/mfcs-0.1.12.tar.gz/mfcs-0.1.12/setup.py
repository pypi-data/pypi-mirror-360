from setuptools import setup, find_packages
import os
import re

def update_common_rules():
    """Update COMMON_RULES in function_prompt.py and memory_prompt.py with content from ToolPrompt.txt and MemoryPrompt.txt."""
    # Update function prompt
    tool_prompt_path = os.path.join("mfcs-prompt", "ToolPrompt.txt")
    function_prompt_path = os.path.join("src", "mfcs", "function_prompt.py")
    
    if not os.path.exists(tool_prompt_path):
        print(f"Warning: {tool_prompt_path} not found. Skipping COMMON_RULES update.")
    else:
        try:
            with open(tool_prompt_path, "r", encoding="utf-8") as f:
                tool_prompt_content = f.read()
                
            with open(function_prompt_path, "r", encoding="utf-8") as f:
                function_prompt_content = f.read()
                
            # Replace the COMMON_RULES content
            pattern = r'(COMMON_RULES = """).*?(""")'
            new_content = re.sub(pattern, f'\\1{tool_prompt_content}\\2', 
                               function_prompt_content, flags=re.DOTALL)
                
            with open(function_prompt_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print("Successfully updated COMMON_RULES with ToolPrompt.txt content")
        except Exception as e:
            print(f"Error updating COMMON_RULES: {e}")

    # Update memory prompt
    memory_prompt_path = os.path.join("mfcs-prompt", "MemoryPrompt.txt")
    memory_prompt_py_path = os.path.join("src", "mfcs", "memory_prompt.py")
    
    if not os.path.exists(memory_prompt_path):
        print(f"Warning: {memory_prompt_path} not found. Skipping COMMON_RULES update.")
    else:
        try:
            with open(memory_prompt_path, "r", encoding="utf-8") as f:
                memory_prompt_content = f.read()
                
            with open(memory_prompt_py_path, "r", encoding="utf-8") as f:
                memory_prompt_py_content = f.read()
                
            # Replace the COMMON_RULES content
            pattern = r'(COMMON_RULES = """).*?(""")'
            new_content = re.sub(pattern, f'\\1{memory_prompt_content}\\2', 
                               memory_prompt_py_content, flags=re.DOTALL)
                
            with open(memory_prompt_py_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print("Successfully updated COMMON_RULES with MemoryPrompt.txt content")
        except Exception as e:
            print(f"Error updating memory COMMON_RULES: {e}")

    # Update agent prompt
    agent_prompt_path = os.path.join("mfcs-prompt", "AgentPrompt.txt")
    agent_prompt_py_path = os.path.join("src", "mfcs", "agent_prompt.py")
    
    if not os.path.exists(agent_prompt_path):
        print(f"Warning: {agent_prompt_path} not found. Skipping COMMON_RULES update.")
    else:
        try:
            with open(agent_prompt_path, "r", encoding="utf-8") as f:
                agent_prompt_content = f.read()
                
            with open(agent_prompt_py_path, "r", encoding="utf-8") as f:
                agent_prompt_py_content = f.read()
                
            # Replace the COMMON_RULES content
            pattern = r'(COMMON_RULES = """).*?(""")'
            new_content = re.sub(pattern, f'\\1{agent_prompt_content}\\2', 
                               agent_prompt_py_content, flags=re.DOTALL)
                
            with open(agent_prompt_py_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print("Successfully updated COMMON_RULES with AgentPrompt.txt content")
        except Exception as e:
            print(f"Error updating agent COMMON_RULES: {e}")

# Update COMMON_RULES before setup
update_common_rules()

# 使用pyproject.toml中的配置，这里只提供基本的setup调用
setup() 