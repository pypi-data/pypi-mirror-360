def find_available_nodes(graph, v_type, v_available, num_nodes_req):
    """
    Finds a specified number of available nodes in the graph.

    This implementation assumes the request is for whole, available nodes.
    It doesn't handle requests for a specific number of cores distributed
    across nodes (which would be more complex).

    Args:
        graph: The graph-tool Graph object.
        v_type: Vertex property map for resource type.
        v_available: Vertex property map for availability.
        num_nodes_req: The number of nodes requested.

    Returns:
        list: A list of available Vertex objects (nodes) satisfying the request,
              or None if the request cannot be satisfied.
    """
    available_nodes = []
    # Iterate through all vertices in the graph
    for v in graph.vertices():
        if v_type[v] == "node" and v_available[v]:
            available_nodes.append(v)

            # If we found enough nodes, return them
            if len(available_nodes) == num_nodes_req:
                return available_nodes  # Found enough

    # If we finished iterating and didn't find enough
    if len(available_nodes) < num_nodes_req:
        print(f"Could not find {num_nodes_req} available nodes. Found only {len(available_nodes)}.")
        return None
    else:
        # This part should technically not be reached due to the check inside loop,
        # but ensures we return the list if the loop finishes exactly on target.
        return available_nodes[:num_nodes_req]


def allocate_nodes(graph, v_available, nodes_to_allocate):
    """
    Marks specified nodes (and their descendants) as unavailable in the graph.

    Args:
        graph: The graph-tool Graph object.
        v_available: Vertex property map for availability (will be modified).
        nodes_to_allocate: A list of Vertex objects (nodes) to mark as unavailable.
    """
    if not nodes_to_allocate:
        print("No nodes provided for allocation.")
        return

    for node_v in nodes_to_allocate:
        # Use BFS/DFS to find all descendants of the node
        # gt.bfs_iterator yields edges, gt.dfs_iterator yields vertices
        for descendant_v in gt.dfs_iterator(graph, node_v):
            # Mark the node itself and all its descendants (sockets, cores) unavailable
            if v_available[descendant_v]:  # Avoid unnecessary writes if already False
                v_available[descendant_v] = False
        print(f"Allocated Node {graph.vp.id[node_v]} and its descendants.")

            # Each valueset is a set of requirements for a node - we assume number is small
            # All requirements (multiple subsystems, for example) must be met for a single cluster.
            for valueset in values:
                # Within a valueset (a dict of properties that must apply to one node)
                # we need to have overlapping vertices. This is stupid and inefficient, but it
                # will get the job done.
                vertices_satisfied = []
                for vertex in self.g.get_vertices():
                    # Assemble the single query for one or more nodes
                    for key, value in valueset.items():   
                        # Node properties are directly on the node, not under metadata or attributes
                        if key in node_properties:
                            v_prop = self.g.vertex_properties.get(key)
                        else:
                            v_prop = self.g.vertex_properties.get(f"attribute.{key}")
                        if not v_prop:
                            print(f"{LogColors.RED}=> No Matches due to unknown property {key}{LogColors.ENDC}")                        
                            return False               
                        # If we get here, we found a property with the key, now we check the value
                        found_value = v_prop[vertex]
                        if not found_value or found_value != value:
                            continue
                            
                    # If we get here, we found a vertex that meets all value criteria
                    vertices_satisfied.append(vertex)


# --- Main Execution ---
if __name__ == "blerg":
    # 1. Create the cluster graph
    g, v_type, v_id, v_available = create_cluster_graph(
        NUM_RACKS, NODES_PER_RACK, SOCKETS_PER_NODE, CORES_PER_SOCKET
    )

    # Optional: Print details of some vertices
    print("\nSample Vertex Details:")
    for i in range(min(15, g.num_vertices())):  # Print first few vertices
        v = g.vertex(i)
        print(f"  Vertex {i}: ID='{v_id[v]}', Type='{v_type[v]}', Available={v_available[v]}")

    # Optional: Visualize the graph (requires cairocffi/pycairo)
    try:
        # Use radial tree layout, good for hierarchies
        # pos = gt.radial_tree_layout(g, g.vertex(0)) # g.vertex(0) is the cluster root
        # Use planar layout if radial fails or looks odd
        pos = gt.arf_layout(g, max_iter=100)

        # Color vertices by type
        color_map = {
            "cluster": "red",
            "rack": "blue",
            "node": "green",
            "socket": "orange",
            "core": "grey",
        }
        v_color = g.new_vertex_property("string")
        for v in g.vertices():
            v_color[v] = color_map.get(v_type[v], "black")  # Default to black if type unknown

        # Draw available nodes brighter, unavailable nodes darker/transparent
        v_fill_color_prop = g.new_vertex_property("vector<double>")
        for v in g.vertices():
            base_color_hex = gt.color_names[color_map.get(v_type[v], "black")]
            if v_available[v]:
                v_fill_color_prop[v] = list(base_color_hex)  # Use original color with full alpha
            else:
                # Make unavailable nodes semi-transparent or darker gray
                # v_fill_color_prop[v] = list(base_color_hex)[:3] + [0.3] # RGBA with low alpha
                v_fill_color_prop[v] = [0.5, 0.5, 0.5, 0.7]  # Dark Gray semi-transparent

        print("\nAttempting to draw graph to 'cluster_graph.png'...")
        gt.graph_draw(
            g,
            pos=pos,
            vertex_text=v_id,  # Label vertices with their ID
            vertex_font_size=8,
            # vertex_fill_color=v_color, # Simple color by type
            vertex_fill_color=v_fill_color_prop,  # Color + Availability
            vertex_size=10,
            edge_pen_width=1,
            output_size=(1200, 1000),
            output="cluster_graph.png",
        )
        print("Graph saved to cluster_graph.png (if drawing libraries are installed).")
    except ImportError:
        print("\nCould not draw graph: cairocffi/pycairo not found or other graphics issue.")
    except Exception as e:
        print(f"\nError during graph drawing: {e}")

    # 2. Define a resource request
    nodes_requested = 5
    print(f"\n--- Resource Request: {nodes_requested} nodes ---")

    # 3. Check if the request can be satisfied
    allocation = find_available_nodes(g, v_type, v_available, nodes_requested)

    # 4. Process the result
    if allocation:
        print(f"\nSuccess! Found {len(allocation)} available nodes:")
        allocated_node_ids = [v_id[node_v] for node_v in allocation]
        print(f"  Allocated Node IDs: {allocated_node_ids}")

        # 5. Simulate Allocation (Modify the graph state)
        print("\nSimulating allocation by marking resources as unavailable...")
        allocate_nodes(g, v_available, allocation)

        # 6. Try another request after allocation
        nodes_requested_2 = 5
        print(f"\n--- Second Resource Request: {nodes_requested_2} nodes ---")
        allocation2 = find_available_nodes(g, v_type, v_available, nodes_requested_2)
        if allocation2:
            print(f"\nSuccess! Found {len(allocation2)} available nodes for the second request:")
            allocated_node_ids_2 = [v_id[node_v] for node_v in allocation2]
            print(f"  Allocated Node IDs: {allocated_node_ids_2}")
        else:
            print(f"\nFailed to satisfy the second request for {nodes_requested_2} nodes.")

        # Optional: Redraw graph after allocation
        try:
            # Recalculate colors based on updated availability
            for v in g.vertices():
                base_color_hex = gt.color_names[color_map.get(v_type[v], "black")]
                if v_available[v]:
                    v_fill_color_prop[v] = list(base_color_hex)
                else:
                    v_fill_color_prop[v] = [0.5, 0.5, 0.5, 0.7]  # Dark Gray semi-transparent

            print(
                "\nAttempting to draw graph after allocation to 'cluster_graph_after_alloc.png'..."
            )
            gt.graph_draw(
                g,
                pos=pos,  # Reuse previous layout position
                vertex_text=v_id,
                vertex_font_size=8,
                vertex_fill_color=v_fill_color_prop,
                vertex_size=10,
                edge_pen_width=1,
                output_size=(1200, 1000),
                output="cluster_graph_after_alloc.png",
            )
            print("Graph saved to cluster_graph_after_alloc.png.")
        except Exception as e:
            print(f"\nError during second graph drawing: {e}")

    else:
        print(f"\nFailed to satisfy the initial request for {nodes_requested} nodes.")

    print("\nScript finished.")
