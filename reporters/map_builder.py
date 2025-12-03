from graphviz import Digraph
import os
import re
import textwrap

def _sanitize_text(text, width=25):
    """
    Membersihkan dan membungkus teks. 
    PENTING: Mencegah crash jika input berupa Dictionary/List (Data API).
    """
    if text is None:
        return ""
    
    # --- FIX CRASH DI SINI ---
    # Jika input adalah Dictionary (misal data API Log), kita jangan wrap isinya.
    # Kita ganti dengan label generik agar Mindmap tetap bersih.
    if isinstance(text, dict):
        return "[Data API/Context]"
    
    if isinstance(text, list):
        return "[List Data]"
    # -------------------------

    # Pastikan jadi string
    text_str = str(text)
    
    # Bungkus teks agar tidak melebar ke samping
    return '\n'.join(textwrap.wrap(text_str, width=width))

class MapBuilder:
    def __init__(self, scenario_name: str, output_dir: str):
        self.scenario_name = scenario_name
        self.output_dir = output_dir
        self.nodes = {}
        self.edges = []
        # "Default" adalah cluster bawaan jika tidak ada tag # FITUR
        self.features = {"Default": []} 
        self.current_feature = "Default"
        
        # Node Start wajib ada
        self.nodes["Start"] = {"label": "Start", "fillcolor": "#4CAF50", "fontcolor": "white", "shape": "Mdiamond"}
        self.features["Default"].append("Start")

    def set_feature(self, feature_name: str):
        """Sets the current feature for clustering."""
        # Bersihkan nama fitur agar aman
        clean_name = _sanitize_text(feature_name, width=40)
        
        if clean_name not in self.features:
            self.features[clean_name] = []
        self.current_feature = clean_name

    def add_transition(self, from_activity: str, action_name: str, to_activity: str, status: str):
        """
        Menambahkan garis transisi dari Activity A ke Activity B.
        """
        # 1. Tentukan ID Node (Ambil nama belakang Activity saja biar pendek)
        # Misal: com.maxxi.MainActivity -> MainActivity
        from_node = "Start"
        if from_activity and from_activity != "Start":
            from_node = _sanitize_text(from_activity.split('.')[-1])
            
        to_node = _sanitize_text(to_activity.split('.')[-1])
        
        # 2. Sanitize Action Name (Ini yang bikin crash tadi)
        wrapped_action = _sanitize_text(action_name)

        # 3. Tentukan Warna (Merah jika Failed)
        color = '#E8F5E9' # Hijau Muda (Default node)
        if status == 'Failed':
            color = '#FFCDD2' # Merah Muda

        # 4. Daftarkan Node jika belum ada
        if from_node not in self.nodes:
            self.nodes[from_node] = {"label": from_node, "fillcolor": "lightgrey"}
            # Masukkan ke fitur yang sedang aktif
            self.features[self.current_feature].append(from_node)

        if to_node not in self.nodes:
            self.nodes[to_node] = {"label": to_node, "fillcolor": color}
            self.features[self.current_feature].append(to_node)
        else:
            # Update warna jika node sudah ada (misal dari abu jadi merah)
            self.nodes[to_node]['fillcolor'] = color

        # 5. Simpan Garis (Edge)
        self.edges.append({"from": from_node, "to": to_node, "label": wrapped_action})

    def render_map(self, filename=None):
        dot = Digraph(comment=f'{self.scenario_name} Flow')
        
        # Setting Visual: Top-to-Bottom, Garis Siku (ortho)
        dot.attr(rankdir='TB', splines='ortho', compound='true')
        dot.attr('node', shape='box', style='rounded,filled', fontname='Helvetica')

        # Create Clusters (Kotak-kotak Fitur)
        for feature, nodes in self.features.items():
            if not nodes:
                continue
            
            # Buat ID Cluster yang aman (hapus spasi/newline)
            cluster_id = "cluster_" + re.sub(r'\W+', '', feature)
            
            with dot.subgraph(name=cluster_id) as c:
                # Label Cluster
                c.attr(label=feature, style='filled', color='#E3F2FD', fontsize='12')
                c.node_attr.update(style='filled', color='white')
                
                # Masukkan node-node milik fitur ini ke dalam kotak
                for node_name in nodes:
                    if node_name in self.nodes:
                        attrs = self.nodes[node_name]
                        c.node(node_name, label=attrs.get("label", node_name), 
                               fillcolor=attrs.get("fillcolor", "white"),
                               fontcolor=attrs.get("fontcolor", "black"),
                               shape=attrs.get("shape", "box"))

        # Gambar Garis-garisnya
        for edge in self.edges:
            dot.edge(edge["from"], edge["to"], label=edge["label"], fontsize='10')

        try:
            safe_scenario_name = re.sub(r'[^\w-]', '', self.scenario_name).strip()
            if not filename:
                filename = f"Heimdall_Flow_{safe_scenario_name}.gv"
                
            render_path = os.path.join(self.output_dir, filename)
            # Render ke PNG
            output_file = dot.render(render_path, format='png', view=False, cleanup=True)
            return output_file
            
        except Exception as e:
            print(f"!!! Error rendering graph: {e}")
            print("Please ensure Graphviz is installed and in your system's PATH.")
            return None