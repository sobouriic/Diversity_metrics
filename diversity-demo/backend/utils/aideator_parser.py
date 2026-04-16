"""
Parser for Aideator experiment folder structures and JSON formats.

Aideator Experiment Structure:
- Desktop application for collaborative ideation sessions
- Outputs results.json: hierarchical tree of ideation nodes
- Nodes include: problems, insights, solutions, strategies, etc.
- Only SOLUTION nodes are extracted for diversity analysis

File Format:
- results.json: Tree structure with recursive node hierarchy
- status.json: Metadata about experiment (optional)
- Folder naming: {timestamp}_{condition}_{domain}
  Example: 20260414_010541_2_kyoto_tourism

This module:
1. Recursively extracts SOLUTION nodes from tree
2. Loads experiment metadata from status.json
3. Validates solution format
4. Parses experiment folder paths for context
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path


def extract_solutions_from_tree(tree_dict: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Recursively extract all SOLUTION nodes from Aideator hierarchical tree.
    
    Aideator Tree Structure:
    - Root: "posts" or direct tree dict
    - Each node: Dict with type, name, description, children, achievers, etc.
    - Recursive: children field contains child nodes
    - Target: Nodes where type == "solution"
    
    Algorithm:
    1. Traverse tree depth-first (recursive)
    2. Check each node's type field
    3. Extract solutions (type == "solution")
    4. Recurse into children and posts fields
    5. Collect all solutions in flat list
    
    Solution Extraction Logic:
    - Required: type field with value "solution"
    - Fields used:
      - id: unique identifier (fallback: generated)
      - name: solution title (required)
      - description: solution details (optional)
      - achievers: impacts/results (fallback for description)
    
    Args:
        tree_dict: Root node dictionary from results.json
                  - Typically: top-level "posts" dict or tree root
                  - May be nested with children/posts fields
        
    Returns:
        List of solution dictionaries with structure:
        [
            {
                "id": "solution_identifier",
                "title": "Solution Name",
                "description": "Detailed description or context"
            },
            ...
        ]
        
    Example:
        >>> import json
        >>> with open("results.json") as f:
        ...     data = json.load(f)
        >>> solutions = extract_solutions_from_tree(data)
        >>> print(f"Found {len(solutions)} solutions")
    """
    
    solutions = []
    
    def traverse(node: Dict[str, Any], parent_path: str = "") -> None:
        """
        Recursive tree traversal function.
        
        Args:
            node: Current node dict to examine
            parent_path: String path for debugging (not used in logic)
        """
        
        if not isinstance(node, dict):
            return
        
        # Check if current node is a solution
        node_type = node.get("type", "")
        if node_type == "solution":
            # Extract solution fields
            node_id = node.get("id", f"solution_{len(solutions)}")
            title = node.get("name", "Untitled Solution")
            description = node.get("description", "")
            
            # Fallback: use achievers list if no description
            if not description:
                achievers = node.get("achievers", [])
                if achievers:
                    description = f"Achieved by: {', '.join(str(a) for a in achievers)}"
            
            solutions.append({
                "id": node_id,
                "title": title.strip() if title else "Untitled",
                "description": description.strip() if description else "No description"
            })
        
        # Recurse into children field
        children = node.get("children", [])
        if isinstance(children, list):
            for child in children:
                traverse(child, parent_path)
        
        # Recurse into posts field (alternate structure sometimes used)
        posts = node.get("posts", [])
        if isinstance(posts, list):
            for post in posts:
                traverse(post, parent_path)
    
    # Start tree traversal from root
    traverse(tree_dict)
    
    return solutions


def load_experiment_results(
    folder_path: str,
) -> Dict[str, Any]:
    """
    Load and parse experiment folder, extracting solutions and metadata.
    
    This function:
    1. Validates that results.json exists
    2. Parses JSON file(s)
    3. Extracts solutions (from tree or pre-extracted list)
    4. Loads optional metadata from status.json
    5. Returns structured result
    
    Expected Folder Contents:
    - results.json (required): Aideator tree structure
    - status.json (optional): Experiment metadata
    
    Solutions Extraction:
    - Method 1: results.json has "solutions" field (pre-extracted)
    - Method 2: Parse tree structure for solution nodes
    
    Metadata Collection:
    - From status.json if available:
      - state: Experiment status (e.g., "completed")
      - nodes_generated: Total nodes created
      - total_solutions: Estimated solution count
      - timestamp: When experiment started
    - Computed: solution_count (actual count)
    
    Args:
        folder_path: Path to experiment folder
                    - May be relative or absolute
                    - Must contain results.json
                    
    Returns:
        Dictionary with structure:
        {
            "solutions": [
                {"title": "...", "description": "...", "achievers": [...]}
            ],
            "metadata": {
                "solution_count": int,
                "status": str,
                "nodes_generated": int,
                "total_solutions": int,
                "timestamp": str
            }
        }
        
    Raises:
        FileNotFoundError: If results.json not found
        json.JSONDecodeError: If JSON is invalid/corrupted
        
    Example:
        >>> result = load_experiment_results("/path/to/experiment")
        >>> print(f"Loaded {result['metadata']['solution_count']} solutions")
    """
    
    folder = Path(folder_path)
    results_file = folder / "results.json"
    status_file = folder / "status.json"
    
    # Validate that results.json exists
    if not results_file.exists():
        raise FileNotFoundError(
            f"results.json not found in {folder_path}"
        )
    
    # Load and parse results.json
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Extract solutions from results
    # Check if solutions already extracted, or need to parse from tree
    if isinstance(results, dict) and "solutions" in results:
        # Solutions already extracted in JSON - use them directly
        solutions = []
        for sol_data in results.get("solutions", []):
            if isinstance(sol_data, dict):
                solutions.append({
                    "title": sol_data.get("name", sol_data.get("title", "")),
                    "description": sol_data.get("description", ""),
                    "achievers": sol_data.get("achievers", [])
                })
    else:
        # Need to extract solutions from hierarchical tree structure
        solutions = extract_solutions_from_tree(results)
    
    # Load optional metadata from status.json
    metadata = {}
    if status_file.exists():
        with open(status_file, 'r') as f:
            status = json.load(f)
            metadata = {
                "status": status.get("state", "unknown"),
                "nodes_generated": status.get("nodes_generated", 0),
                "total_solutions": status.get("total_solutions", len(solutions)),
                "timestamp": status.get("timestamp", None),
            }
    
    # Add actual solution count
    metadata["solution_count"] = len(solutions)
    
    return {
        "solutions": solutions,
        "metadata": metadata
    }


def process_experiment_folder(
    folder_path: str,
    condition: Optional[int] = None,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process complete experiment folder with context parsing.
    
    This function:
    1. Loads experiment data (solutions and metadata)
    2. Attempts to parse condition and domain from folder name
    3. Uses provided parameters if parsing fails
    4. Returns enriched result with context
    
    Folder Name Parsing:
    - Expected format: {timestamp}_{timestamp}_{condition}_{domain_parts}
    - Example: 20260414_010541_2_kyoto_tourism
      - condition: 2
      - domain: "kyoto_tourism"
    - Condition: looks for single digit 0-3 after position 1
    - Domain: all parts after condition number
    
    Args:
        folder_path: Path to experiment folder
                    - May be relative or absolute
                    - Used for both loading and name parsing
        condition: Optional condition number (0-3)
                  - Overrides folder name parsing if provided
                  - Ignored if None
        domain: Optional domain identifier
               - Overrides folder name parsing if provided
               - Examples: "renewable_energy", "kyoto_tourism"
               - Ignored if None
        
    Returns:
        Dictionary with structure:
        {
            "solutions": [...],
            "metadata": {
                "solution_count": int,
                "condition": int (0-3),
                "domain": str,
                ... (other metadata)
            }
        }
        
    Example:
        >>> result = process_experiment_folder(
        ...     "/data/20260414_010541_2_kyoto_tourism",
        ...     condition=None,  # Parse from folder name
        ...     domain=None      # Parse from folder name
        ... )
        >>> print(result["metadata"]["condition"])  # 2
        >>> print(result["metadata"]["domain"])  # "kyoto_tourism"
    """
    
    # Load experiment results and base metadata
    result = load_experiment_results(folder_path)
    
    # If condition/domain provided as parameters, use them
    if condition is not None:
        result["metadata"]["condition"] = condition
    if domain is not None:
        result["metadata"]["domain"] = domain
    
    # Try to parse condition and domain from folder name
    # Format: {timestamp}_{timestamp}_{condition}_{domain_parts}
    folder = Path(folder_path)
    folder_name = folder.name
    
    try:
        parts = folder_name.split('_')
        
        # Look for a single digit (0-3) which indicates condition
        # Usually appears after timestamp parts (position > 1)
        for i, part in enumerate(parts):
            if part.isdigit() and 0 <= int(part) <= 3 and i > 1:
                parsed_condition = int(part)
                parsed_domain = '_'.join(parts[i+1:]) if i+1 < len(parts) else None
                
                # Only use parsed values if not already provided
                if condition is None and parsed_condition is not None:
                    result["metadata"]["condition"] = parsed_condition
                if domain is None and parsed_domain:
                    result["metadata"]["domain"] = parsed_domain
                break
    except (ValueError, IndexError):
        # Could not parse from folder name - that's okay
        # Will use provided parameters if any
        pass
    
    return result


def validate_solution_format(solution: Dict[str, str]) -> bool:
    """
    Validate that a solution dictionary has required fields.
    
    Required Fields:
    - title: str, non-empty
    - description: str, non-empty
    
    This function is used to:
    - Filter out incomplete solutions before analysis
    - Detect corruption in experiment data
    - Provide feedback on data quality issues
    
    Args:
        solution: Solution dictionary to validate
                 - Expected keys: "title", "description"
                 - Both values should be strings
        
    Returns:
        bool: True if solution is valid and complete, False otherwise
        
    Example:
        >>> solution = {"title": "Solar Power", "description": "Use solar panels"}
        >>> validate_solution_format(solution)
        True
        >>> incomplete = {"title": "Wind Power"}
        >>> validate_solution_format(incomplete)
        False
    """
    required_fields = ["title", "description"]
    return all(
        field in solution and isinstance(solution[field], str)
        for field in required_fields
    )
    
    # Extract solutions - check if already extracted in results.json or in tree
    if isinstance(results, dict) and "solutions" in results:
        # Solutions already extracted - use them directly
        solutions = []
        for sol_data in results.get("solutions", []):
            if isinstance(sol_data, dict):
                solutions.append({
                    "title": sol_data.get("name", sol_data.get("title", "")),
                    "description": sol_data.get("description", ""),
                    "achievers": sol_data.get("achievers", [])
                })
    else:
        # Extract solutions from tree structure
        solutions = extract_solutions_from_tree(results)
    
    # Load metadata from status if available
    metadata = {}
    if status_file.exists():
        with open(status_file, 'r') as f:
            status = json.load(f)
            metadata = {
                "status": status.get("state", "unknown"),
                "nodes_generated": status.get("nodes_generated", 0),
                "total_solutions": status.get("total_solutions", len(solutions)),
                "timestamp": status.get("timestamp", None),
            }
    
    metadata["solution_count"] = len(solutions)
    
    return {
        "solutions": solutions,
        "metadata": metadata
    }


def process_experiment_folder(
    folder_path: str,
    condition: Optional[int] = None,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process complete experiment folder.
    
    Args:
        folder_path: Path to experiment folder
        condition: Optional condition number (0-3)
        domain: Optional domain name
        
    Returns:
        Dict with solutions, metadata, condition, domain
    """
    
    result = load_experiment_results(folder_path)
    
    # Add condition and domain if provided
    if condition is not None:
        result["metadata"]["condition"] = condition
    if domain is not None:
        result["metadata"]["domain"] = domain
    
    # Parse from folder name if not provided
    # Format: {timestamp}_{condition}_{domain_parts}
    # Example: 20260414_010541_2_kyoto_tourism
    folder = Path(folder_path)
    folder_name = folder.name
    
    try:
        parts = folder_name.split('_')
        
        # Look for a single digit (0-3) which should be the condition
        # Typically format: timestamp_timestamp_condition_domain...
        for i, part in enumerate(parts):
            if part.isdigit() and 0 <= int(part) <= 3 and i > 1:
                parsed_condition = int(part)
                parsed_domain = '_'.join(parts[i+1:]) if i+1 < len(parts) else None
                
                if condition is None and parsed_condition is not None:
                    result["metadata"]["condition"] = parsed_condition
                if domain is None and parsed_domain:
                    result["metadata"]["domain"] = parsed_domain
                break
    except (ValueError, IndexError):
        pass  # Could not parse from folder name
    
    return result


def validate_solution_format(solution: Dict[str, str]) -> bool:
    """
    Validate that a solution dict has required fields.
    
    Args:
        solution: Solution dict to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["title", "description"]
    return all(
        field in solution and isinstance(solution[field], str)
        for field in required_fields
    )
