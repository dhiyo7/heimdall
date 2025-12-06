import os
import base64
import requests
import re

class MapBuilder:
    """
    Heimdall Visual Engine (Theme: Wide & Dynamic).
    Fitur:
    1. Validasi ID Cluster (Anti-Crash).
    2. Syntax Fix (::: untuk styling).
    3. Tema Warna Modern (Biru/Kuning/Hijau).
    """
    
    def __init__(self, scenario_name, output_dir):
        self.scenario_name = scenario_name
        self.output_dir = output_dir
        self.current_feature = "Initialization"
        
        self.nodes = []
        self.edges = []
        self.clusters = {}
        
        self.last_node_id = "Start"
        self.node_counter = 0
        
        # Init Start Node
        self._add_node("Start", "Mulai", "circle", "startNode")
        self._add_to_cluster("Initialization", "Start")

    def set_feature(self, feature_name):
        clean_name = feature_name.replace('"', '').strip()
        self.current_feature = clean_name
        if clean_name not in self.clusters:
            self.clusters[clean_name] = []

    def add_step(self, narrative, step_type="action", condition_label=None):
        self.node_counter += 1
        node_id = f"N{self.node_counter}"
        
        # Mapping Tipe ke Style Class
        shape = "box"
        style = "success" # Default Action (Biru)
        
        if step_type == "logic":
            shape = "diamond"
            style = "logic"   # Logic (Kuning)
        elif step_type == "error":
            style = "danger"  # Error (Merah)
        elif step_type == "end":
            shape = "circle"
            style = "endNode" # End (Merah Bulat)

        self._add_node(node_id, narrative, shape, style)
        self._add_to_cluster(self.current_feature, node_id)
        
        edge_label = condition_label if condition_label else ""
        self.edges.append({
            "from": self.last_node_id, 
            "to": node_id, 
            "label": edge_label
        })
        
        self.last_node_id = node_id
        return node_id

    def render_map(self):
        print("  🎨 Rendering Mermaid Flowchart...")
        mermaid_code = self._generate_mermaid_code()
        
        # Backup code
        mmd_path = os.path.join(self.output_dir, "flowchart.mmd")
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(mermaid_code)
            
        self._download_image(mermaid_code)

    def _add_node(self, nid, label, shape, style):
        safe_label = label.replace('"', "'")
        self.nodes.append({
            "id": nid, 
            "label": safe_label, 
            "shape": shape, 
            "style": style
        })

    def _add_to_cluster(self, feature, nid):
        if feature not in self.clusters:
            self.clusters[feature] = []
        self.clusters[feature].append(nid)

    def _clean_id(self, text):
        """Membersihkan nama cluster agar valid di Mermaid."""
        clean = re.sub(r'[^a-zA-Z0-9]', '', text)
        return f"Cluster_{clean}"

    def _generate_mermaid_code(self):
        code = ["flowchart TD"]
        
        # --- 1. DEFINISI GAYA (MODERN THEME) ---
        # Node Biasa (Biru)
        code.append("    classDef success fill:#e1f5fe,stroke:#0277bd,stroke-width:2px,rx:5,ry:5,color:#01579b;")
        # Node Logika (Kuning)
        code.append("    classDef logic fill:#fff9c4,stroke:#fbc02d,stroke-width:3px,stroke-dasharray: 5 5,rx:5,ry:5,color:#ef6c00;")
        # Node Error (Merah Pucat)
        code.append("    classDef danger fill:#ffebee,stroke:#c62828,stroke-width:2px,rx:5,ry:5;")
        # Start Node (Hijau)
        code.append("    classDef startNode fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,rx:20,ry:20,color:#1b5e20;")
        # End Node (Merah)
        code.append("    classDef endNode fill:#ffcdd2,stroke:#c62828,stroke-width:2px,rx:20,ry:20,color:#b71c1c;")
        # Garis Panah (Abu Tua)
        code.append("    linkStyle default stroke:#546e7a,stroke-width:2px,fill:none;")
        code.append("")
        
        # --- 2. GENERATE CLUSTERS ---
        cluster_colors = [
            "fill:#f1f8e9,stroke:#558b2f,color:#33691e", # Hijau Muda
            "fill:#f3e5f5,stroke:#8e24aa,color:#4a148c", # Ungu Muda
            "fill:#fffde7,stroke:#fbc02d,color:#f57f17", # Kuning Muda
            "fill:#eceff1,stroke:#546e7a,color:#263238"  # Abu Muda
        ]
        
        cluster_idx = 0
        for feature, node_ids in self.clusters.items():
            safe_id = self._clean_id(feature)
            # Sanitasi Label Subgraph
            safe_label = feature.encode('ascii', 'ignore').decode('ascii').strip()
            if not safe_label: safe_label = "Feature"
            
            code.append(f'    subgraph {safe_id} ["📂 {safe_label}"]')
            code.append("    direction TB")
            
            for nid in node_ids:
                node = next((n for n in self.nodes if n["id"] == nid), None)
                if node:
                    open_br, close_br = "[", "]"
                    if node['shape'] == 'diamond': open_br, close_br = "{", "}"
                    elif node['shape'] == 'circle': open_br, close_br = "((", "))"
                    
                    # [FIX KRUSIAL] Pakai Tiga Titik Dua (:::)
                    line = f'    {node["id"]}{open_br}"{node["label"]}"{close_br}:::{node["style"]}'
                    code.append(line)
            
            code.append("    end")
            
            # Warnai Cluster (Looping warna)
            style_str = cluster_colors[cluster_idx % len(cluster_colors)]
            code.append(f"    style {safe_id} {style_str},stroke-width:2px,rx:10,ry:10")
            cluster_idx += 1
            code.append("")

        # --- 3. GENERATE EDGES ---
        for edge in self.edges:
            arrow = "-->"
            if edge["label"]:
                # Label panah logic (Ya/Tidak)
                arrow = f'-- "{edge["label"]}" -->'
            code.append(f'    {edge["from"]} {arrow} {edge["to"]}')
            
        return "\n".join(code)

    def _download_image(self, mermaid_code):
        try:
            graphbytes = mermaid_code.encode("utf8")
            base64_bytes = base64.b64encode(graphbytes)
            base64_string = base64_bytes.decode("ascii")
            
            url = "https://mermaid.ink/img/" + base64_string
            print("  📡 Requesting image from mermaid.ink...")
            response = requests.get(url)
            
            if response.status_code == 200:
                img_path = os.path.join(self.output_dir, "flowchart.png")
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print(f"  🖼️ Flowchart saved: {img_path}")
            else:
                print(f"  ⚠️ Gagal render. Status: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️ Error downloading flowchart: {e}")