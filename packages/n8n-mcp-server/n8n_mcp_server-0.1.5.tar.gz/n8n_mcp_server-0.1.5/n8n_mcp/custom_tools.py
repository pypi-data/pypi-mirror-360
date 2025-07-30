"""Custom tools for n8n MCP server."""
import sys
from typing import Dict, Any, Optional
import httpx


def register_custom_tools(mcp, client: httpx.AsyncClient):
    """Register custom tools on the MCP instance"""
    
    @mcp.tool()
    async def list_workflows_minimal(
        limit: int = 50,
        active: bool = None,
        tags: str = None,
        name: str = None,
        cursor: str = None
    ) -> Dict[str, Any]:
        """
        List workflows with minimal data (no nodes/connections/staticData).
        
        This is a lightweight version of Retrieve_all_workflows that returns only essential metadata
        to avoid token limits. Use this when you need to list workflows without their full content.
        
        Args:
            limit: Maximum number of workflows to return (default: 50, max: 100)
            active: Filter by active status (true/false)
            tags: Comma-separated list of tags to filter by
            name: Filter by workflow name (partial match)
            cursor: Pagination cursor from previous response
            
        Returns:
            Dictionary with 'data' array of minimal workflow info and optional 'nextCursor'
        """
        # Build query parameters
        params = {
            "limit": min(limit, 100),  # Cap at 100
            "excludePinnedData": "true"  # This helps reduce size somewhat
        }
        
        if active is not None:
            params["active"] = str(active).lower()
        if tags:
            params["tags"] = tags
        if name:
            params["name"] = name
        if cursor:
            params["cursor"] = cursor
        
        # Make the API call
        response = await client.get("/workflows", params=params)
        response.raise_for_status()
        
        result = response.json()
        
        # Strip large fields from each workflow
        if "data" in result and isinstance(result["data"], list):
            minimal_workflows = []
            for workflow in result["data"]:
                minimal_workflow = {
                    "id": workflow.get("id"),
                    "name": workflow.get("name"),
                    "active": workflow.get("active"),
                    "createdAt": workflow.get("createdAt"),
                    "updatedAt": workflow.get("updatedAt"),
                    "tags": workflow.get("tags", [])
                }
                # Add optional fields if they exist
                if "meta" in workflow:
                    minimal_workflow["meta"] = workflow["meta"]
                if "versionId" in workflow:
                    minimal_workflow["versionId"] = workflow["versionId"]
                
                minimal_workflows.append(minimal_workflow)
            
            result["data"] = minimal_workflows
            
            # Size reduction successful
        
        return result
    
    @mcp.tool()
    async def get_workflow_summary(workflow_id: str) -> Dict[str, Any]:
        """
        Get a workflow summary without full node details.
        
        This returns workflow metadata and basic structure info without the full node configurations,
        which can be very large. Use this when you need workflow info but not the complete node data.
        
        Args:
            workflow_id: The ID of the workflow to retrieve
            
        Returns:
            Workflow summary with basic info and node/connection counts
        """
        # Get the full workflow
        response = await client.get(f"/workflows/{workflow_id}")
        response.raise_for_status()
        
        workflow = response.json()
        
        # Create summary with counts instead of full data
        summary = {
            "id": workflow.get("id"),
            "name": workflow.get("name"),
            "active": workflow.get("active"),
            "createdAt": workflow.get("createdAt"),
            "updatedAt": workflow.get("updatedAt"),
            "tags": workflow.get("tags", []),
            "settings": workflow.get("settings", {}),
            "nodeCount": len(workflow.get("nodes", [])),
            "connectionCount": len(workflow.get("connections", {})),
            "hasStaticData": bool(workflow.get("staticData"))
        }
        
        # Add node types summary
        if "nodes" in workflow and workflow["nodes"]:
            node_types = {}
            for node in workflow["nodes"]:
                node_type = node.get("type", "unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1
            summary["nodeTypes"] = node_types
        
        # Add basic workflow info if available
        if "meta" in workflow:
            summary["meta"] = workflow["meta"]
        if "versionId" in workflow:
            summary["versionId"] = workflow["versionId"]
            
        # Size reduction successful
        
        return summary
    
    @mcp.tool()
    async def partial_update_workflow(
        workflow_id: str,
        node_updates: list[Dict[str, Any]],
        update_connections: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Partially update specific nodes in a workflow without updating the entire workflow.
        
        This function fetches the current workflow, updates only the specified nodes by ID,
        and intelligently handles connection updates when node names change.
        
        Args:
            workflow_id: The ID of the workflow to update
            node_updates: List of node updates, each containing:
                - id: The node ID to update (required)
                - updates: Dict of fields to update (e.g., parameters, position, name, etc.)
            update_connections: Whether to auto-update connections when node names change (default: True)
            dry_run: If True, return what would be updated without actually updating (default: False)
            
        Returns:
            Dictionary containing:
                - updated_nodes: List of updated nodes with their new values
                - connection_updates: List of connection updates made (if any)
                - workflow_id: The workflow ID
                - dry_run: Whether this was a dry run
                
        Example:
            node_updates = [
                {
                    "id": "9681490a-68f1-4c6a-86ea-bf2331c3125d",
                    "updates": {
                        "parameters": {"new": "value"},
                        "position": [500, 1000]
                    }
                },
                {
                    "id": "f597a54e-27e9-46e8-b9d5-46dd54406803", 
                    "updates": {
                        "name": "OpenAI Chat Model Updated"
                    }
                }
            ]
        """
        try:
            # Fetch the current workflow
            response = await client.get(f"/workflows/{workflow_id}")
            response.raise_for_status()
            workflow = response.json()
            
            # Track changes
            updated_nodes = []
            connection_updates = []
            name_changes = {}  # old_name -> new_name mapping
            
            # Create a map of node IDs to nodes for quick lookup
            node_map = {node["id"]: node for node in workflow.get("nodes", [])}
            
            # Apply node updates
            for update in node_updates:
                node_id = update.get("id")
                updates = update.get("updates", {})
                
                if not node_id:
                    raise ValueError("Each node update must have an 'id' field")
                
                if node_id not in node_map:
                    raise ValueError(f"Node with ID '{node_id}' not found in workflow")
                
                node = node_map[node_id]
                old_node = dict(node)  # Keep a copy of the old node
                
                # Track name changes for connection updates
                if "name" in updates and updates["name"] != node.get("name"):
                    old_name = node.get("name")
                    new_name = updates["name"]
                    name_changes[old_name] = new_name
                
                # Deep merge the updates into the node
                for key, value in updates.items():
                    if key == "parameters" and isinstance(value, dict) and isinstance(node.get(key), dict):
                        # Merge parameters instead of replacing
                        node[key] = {**node.get(key, {}), **value}
                    else:
                        # Direct replacement for other fields
                        node[key] = value
                
                updated_nodes.append({
                    "id": node_id,
                    "old": old_node,
                    "new": node,
                    "changed_fields": list(updates.keys())
                })
            
            # Update connections if node names changed
            if update_connections and name_changes:
                connections = workflow.get("connections", {})
                
                # Update connection keys (source nodes)
                for old_name, new_name in name_changes.items():
                    if old_name in connections:
                        connections[new_name] = connections.pop(old_name)
                        connection_updates.append({
                            "type": "source_rename",
                            "old_name": old_name,
                            "new_name": new_name
                        })
                
                # Update connection values (target nodes)
                for source_node, node_connections in connections.items():
                    for connection_type, connection_list in node_connections.items():
                        if isinstance(connection_list, list):
                            for conn_group in connection_list:
                                if isinstance(conn_group, list):
                                    for conn in conn_group:
                                        if isinstance(conn, dict) and "node" in conn:
                                            old_target = conn["node"]
                                            if old_target in name_changes:
                                                conn["node"] = name_changes[old_target]
                                                connection_updates.append({
                                                    "type": "target_rename",
                                                    "source": source_node,
                                                    "old_target": old_target,
                                                    "new_target": name_changes[old_target]
                                                })
            
            # Prepare the result
            result = {
                "workflow_id": workflow_id,
                "updated_nodes": [
                    {
                        "id": un["id"],
                        "name": un["new"].get("name"),
                        "changed_fields": un["changed_fields"]
                    } for un in updated_nodes
                ],
                "connection_updates": connection_updates,
                "dry_run": dry_run
            }
            
            # If not a dry run, save the updated workflow
            if not dry_run:
                # The n8n API requires these fields in the update
                # Note: 'tags' field is read-only and must not be included in updates
                update_payload = {
                    "name": workflow.get("name"),
                    "nodes": workflow.get("nodes", []),
                    "connections": workflow.get("connections", {}),
                    "settings": workflow.get("settings", {}),
                    "staticData": workflow.get("staticData", {})
                }
                
                # Make the update request
                update_response = await client.put(f"/workflows/{workflow_id}", json=update_payload)
                update_response.raise_for_status()
                
                result["success"] = True
                result["message"] = f"Successfully updated {len(updated_nodes)} nodes"
            else:
                result["message"] = f"Dry run: Would update {len(updated_nodes)} nodes"
            
            # Update successful
            
            return result
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            # Update failed
            return {
                "error": error_msg,
                "workflow_id": workflow_id,
                "success": False
            }
        except Exception as e:
            error_msg = str(e)
            # Update error
            return {
                "error": error_msg,  
                "workflow_id": workflow_id,
                "success": False
            }
    
    @mcp.tool()
    async def add_nodes_to_workflow(
        workflow_id: str,
        node_additions: list[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Add new nodes to a workflow and optionally insert them between existing nodes.
        
        This function allows you to add new nodes to a workflow and automatically handle
        connection rewiring when inserting nodes between existing ones.
        
        Args:
            workflow_id: The ID of the workflow to update
            node_additions: List of nodes to add, each containing:
                - node: The complete node object with id, name, type, position, parameters, etc.
                - insert_between: (Optional) Dict specifying where to insert the node:
                    - from: Source node name to disconnect from
                    - to: Target node name to disconnect from source
                    - connection_type: Type of connection (default: "main")
                    - output_index: Output index for multiple outputs (default: 0)
            dry_run: If True, return what would be added without actually updating (default: False)
            
        Returns:
            Dictionary containing:
                - added_nodes: List of nodes that were added
                - connection_changes: List of connection changes made
                - workflow_id: The workflow ID
                - dry_run: Whether this was a dry run
                - success: Whether the operation succeeded
                
        Example:
            node_additions = [
                {
                    "node": {
                        "id": "abc-123-def",
                        "name": "Transform Data",
                        "type": "n8n-nodes-base.code",
                        "position": [800, 500],
                        "typeVersion": 1,
                        "parameters": {
                            "code": "return items.map(item => ({ ...item.json, processed: true }));"
                        }
                    },
                    "insert_between": {
                        "from": "Extract from File",
                        "to": "Some Options for the Campaign",
                        "connection_type": "main"
                    }
                }
            ]
        """
        try:
            # Fetch the current workflow
            response = await client.get(f"/workflows/{workflow_id}")
            response.raise_for_status()
            workflow = response.json()
            
            # Get existing nodes and connections
            nodes = workflow.get("nodes", [])
            connections = workflow.get("connections", {})
            
            # Check for ID conflicts
            existing_ids = {node["id"] for node in nodes}
            
            # Track changes
            added_nodes = []
            connection_changes = []
            
            for addition in node_additions:
                new_node = addition.get("node")
                insert_between = addition.get("insert_between")
                
                if not new_node:
                    raise ValueError("Each addition must have a 'node' field")
                
                node_id = new_node.get("id")
                node_name = new_node.get("name")
                
                if not node_id or not node_name:
                    raise ValueError("Each node must have an 'id' and 'name'")
                
                if node_id in existing_ids:
                    raise ValueError(f"Node ID '{node_id}' already exists in the workflow")
                
                # Check if node name already exists
                existing_names = {node["name"] for node in nodes}
                if node_name in existing_names:
                    raise ValueError(f"Node name '{node_name}' already exists in the workflow")
                
                # Add the new node
                nodes.append(new_node)
                added_nodes.append({
                    "id": node_id,
                    "name": node_name,
                    "type": new_node.get("type")
                })
                existing_ids.add(node_id)
                
                # Handle connection insertion if specified
                if insert_between:
                    from_node = insert_between.get("from")
                    to_node = insert_between.get("to")
                    connection_type = insert_between.get("connection_type", "main")
                    output_index = insert_between.get("output_index", 0)
                    
                    if from_node and to_node:
                        # Find and remove the existing connection
                        if from_node in connections:
                            node_connections = connections[from_node]
                            if connection_type in node_connections:
                                connection_list = node_connections[connection_type]
                                
                                # Handle the nested array structure
                                if len(connection_list) > output_index:
                                    output_connections = connection_list[output_index]
                                    
                                    # Find and remove the connection to the target node
                                    new_output_connections = []
                                    removed = False
                                    for conn in output_connections:
                                        if conn.get("node") == to_node:
                                            removed = True
                                            connection_changes.append({
                                                "action": "removed",
                                                "from": from_node,
                                                "to": to_node,
                                                "type": connection_type
                                            })
                                        else:
                                            new_output_connections.append(conn)
                                    
                                    # Update the connections array
                                    connection_list[output_index] = new_output_connections
                                    
                                    # Add connection from source to new node
                                    connection_list[output_index].append({
                                        "node": node_name,
                                        "type": connection_type,
                                        "index": 0
                                    })
                                    connection_changes.append({
                                        "action": "added",
                                        "from": from_node,
                                        "to": node_name,
                                        "type": connection_type
                                    })
                        
                        # Add connection from new node to target
                        if node_name not in connections:
                            connections[node_name] = {}
                        if connection_type not in connections[node_name]:
                            connections[node_name][connection_type] = [[]]
                        
                        connections[node_name][connection_type][0].append({
                            "node": to_node,
                            "type": connection_type,
                            "index": 0
                        })
                        connection_changes.append({
                            "action": "added",
                            "from": node_name,
                            "to": to_node,
                            "type": connection_type
                        })
            
            # Prepare the result
            result = {
                "workflow_id": workflow_id,
                "added_nodes": added_nodes,
                "connection_changes": connection_changes,
                "dry_run": dry_run
            }
            
            # If not a dry run, save the updated workflow
            if not dry_run:
                # The n8n API requires these fields in the update
                # Note: 'tags' field is read-only and must not be included in updates
                update_payload = {
                    "name": workflow.get("name"),
                    "nodes": nodes,
                    "connections": connections,
                    "settings": workflow.get("settings", {}),
                    "staticData": workflow.get("staticData", {})
                }
                
                # Make the update request
                update_response = await client.put(f"/workflows/{workflow_id}", json=update_payload)
                update_response.raise_for_status()
                
                result["success"] = True
                result["message"] = f"Successfully added {len(added_nodes)} nodes"
            else:
                result["message"] = f"Dry run: Would add {len(added_nodes)} nodes"
            
            # Addition successful
            
            return result
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            # Addition failed
            return {
                "error": error_msg,
                "workflow_id": workflow_id,
                "success": False
            }
        except Exception as e:
            error_msg = str(e)
            # Addition error
            return {
                "error": error_msg,
                "workflow_id": workflow_id,
                "success": False
            }