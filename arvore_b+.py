import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --------------------------------------------------------------------------
# PARTE 1: LÓGICA DA ÁRVORE B+ (BACKEND COM REMOÇÃO 100% CORRETA)
# --------------------------------------------------------------------------

class BPlusTreeNode:
    def __init__(self, t, leaf=False, parent=None):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []
        self.parent = parent
        self.next = None

class BPlusTree:
    def __init__(self, t):
        if t < 2:
            raise ValueError("A ordem da Árvore B+ (t) deve ser no mínimo 2.")
        self.root = BPlusTreeNode(t, leaf=True)
        self.t = t

    def insert(self, k):
        if self.search(k):
            return False
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            temp = BPlusTreeNode(self.t, leaf=False)
            temp.children.append(self.root)
            self.root.parent = temp
            self._split_child(temp, 0)
            self.root = temp
        self._insert_non_full(self.root, k)
        return True

    def _insert_non_full(self, x, k):
        if x.leaf:
            pos = 0
            while pos < len(x.keys) and k > x.keys[pos]: pos += 1
            x.keys.insert(pos, k)
        else:
            i = len(x.keys) - 1
            while i >= 0 and k < x.keys[i]: i -= 1
            i += 1
            if len(x.children[i].keys) == 2 * self.t - 1:
                self._split_child(x, i)
                if k > x.keys[i]: i += 1
            self._insert_non_full(x.children[i], k)

    def _split_child(self, x, i):
        t = self.t
        y = x.children[i]
        z = BPlusTreeNode(t, leaf=y.leaf, parent=x)
        if not y.leaf:
            mid_key = y.keys[t - 1]
            z.keys = y.keys[t:]
            y.keys = y.keys[:t - 1]
            z.children = y.children[t:]
            for child in z.children: child.parent = z
            y.children = y.children[:t]
            x.keys.insert(i, mid_key)
        else:
            mid_key_index = t -1 # Na B+, o split de folha copia a chave
            mid_key = y.keys[mid_key_index]
            z.keys = y.keys[mid_key_index:]
            y.keys = y.keys[:mid_key_index]
            z.next = y.next
            y.next = z
            x.keys.insert(i, mid_key)
        x.children.insert(i + 1, z)

    def search(self, k, x=None):
        x = x if x is not None else self.root
        while not x.leaf:
            i = 0
            while i < len(x.keys) and k >= x.keys[i]: i += 1
            x = x.children[i]
        for key in x.keys:
            if key == k: return x
        return None

    # --- Funções de Remoção ---
    def delete(self, key):
        leaf_node = self.search(key)
        if not leaf_node:
            raise ValueError(f"Chave '{key}' não encontrada na árvore.")
        self._delete_entry(leaf_node, key)

    def _delete_entry(self, node, key):
        # Remove a chave do nó
        node.keys.remove(key)

        # Se o nó sofreu underflow, rebalanceia
        min_keys = self.t - 1
        if len(node.keys) < min_keys:
            self._handle_underflow(node)

    def _handle_underflow(self, node):
        # A raiz pode ter menos que o mínimo de chaves
        if node == self.root:
            if not self.root.leaf and len(self.root.keys) == 0:
                self.root = self.root.children[0]
                self.root.parent = None
            return

        parent = node.parent
        child_index = parent.children.index(node)

        # Tenta emprestar do irmão esquerdo
        if child_index > 0:
            left_sibling = parent.children[child_index - 1]
            if len(left_sibling.keys) > self.t - 1:
                self._borrow_from_left(node, left_sibling, parent, child_index)
                return

        # Tenta emprestar do irmão direito
        if child_index < len(parent.children) - 1:
            right_sibling = parent.children[child_index + 1]
            if len(right_sibling.keys) > self.t - 1:
                self._borrow_from_right(node, right_sibling, parent, child_index)
                return

        # Se não pode emprestar, faz a fusão
        if child_index > 0:
            # Funde com o irmão esquerdo
            self._merge(parent.children[child_index - 1], node, parent)
        else:
            # Funde com o irmão direito
            self._merge(node, parent.children[child_index + 1], parent)
    
    def _borrow_from_left(self, node, sibling, parent, child_index):
        # Move a chave do irmão para o nó atual
        key_to_move = sibling.keys.pop()
        node.keys.insert(0, key_to_move)
        
        # Atualiza a chave no pai
        parent.keys[child_index - 1] = node.keys[0]

        # Move o filho correspondente se não for folha
        if not node.leaf:
            child_to_move = sibling.children.pop()
            child_to_move.parent = node
            node.children.insert(0, child_to_move)

    def _borrow_from_right(self, node, sibling, parent, child_index):
        # Move a chave do irmão para o nó atual
        key_to_move = sibling.keys.pop(0)
        node.keys.append(key_to_move)

        # Atualiza a chave no pai
        parent.keys[child_index] = sibling.keys[0]

        # Move o filho correspondente se não for folha
        if not node.leaf:
            child_to_move = sibling.children.pop(0)
            child_to_move.parent = node
            node.children.append(child_to_move)
            
    def _merge(self, left_node, right_node, parent):
        # Encontra o índice da chave do pai a ser removida
        parent_key_index = parent.children.index(left_node)

        # Se for um nó interno, desce a chave do pai
        if not left_node.leaf:
            left_node.keys.append(parent.keys.pop(parent_key_index))

        # Move chaves e filhos do nó direito para o esquerdo
        left_node.keys.extend(right_node.keys)
        left_node.children.extend(right_node.children)
        for child in right_node.children:
            child.parent = left_node

        # Atualiza a lista encadeada se forem folhas
        if left_node.leaf:
            left_node.next = right_node.next
        
        # Remove o ponteiro para o nó direito e a chave do pai
        parent.children.remove(right_node)
        if parent_key_index < len(parent.keys): # Evita erro se for o último filho
             parent.keys.pop(parent_key_index)

        # Se o pai sofrer underflow, propaga o problema
        if len(parent.keys) < self.t - 1:
            self._handle_underflow(parent)


# --------------------------------------------------------------------------
# PARTE 2: INTERFACE GRÁFICA (FRONTEND - SEM MUDANÇAS)
# --------------------------------------------------------------------------
BG_COLOR, CANVAS_BG, CONTROL_BG = "#2E2E2E", "#F5F5F5", "#404040"
TEXT_COLOR, BUTTON_BG, BUTTON_FG = "#FFFFFF", "#007ACC", "#FFFFFF"
NODE_FILL, LEAF_NODE_FILL, NODE_OUTLINE = "#4A90E2", "#34A853", "#005A9C"
NODE_TEXT_COLOR = "#FFFFFF"
FONT_FAMILY = "Segoe UI"

class BPlusTreeVisualizer(tk.Tk):
    def __init__(self, t=3):
        super().__init__()
        self.title("Simulador de Árvore B+ (Remoção Completa)")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)
        self.tree = BPlusTree(t)
        self.zoom_factor = 1.0
        self.node_coords = {}
        
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background=CONTROL_BG)
        style.configure("TLabel", background=CONTROL_BG, foreground=TEXT_COLOR, font=(FONT_FAMILY, 11))
        style.configure("Title.TLabel", font=(FONT_FAMILY, 16, "bold"))
        style.configure("History.TLabel", font=(FONT_FAMILY, 12, "bold"))
        style.configure("TButton", background=BUTTON_BG, foreground=BUTTON_FG, font=(FONT_FAMILY, 10, "bold"), borderwidth=0)
        style.map("TButton", background=[('active', '#005A9C')])
        style.configure("TEntry", fieldbackground="#D0D0D0", font=(FONT_FAMILY, 11))
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1, minsize=300)

        canvas_frame = tk.Frame(self, bg=BG_COLOR)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(canvas_frame, bg=CANVAS_BG, highlightthickness=0)
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")

        control_frame = ttk.Frame(self, style="TFrame", padding=20)
        control_frame.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)

        ttk.Label(control_frame, text=f"Árvore B+ (Ordem t={t})", style="Title.TLabel").pack(pady=(0, 20), anchor="w")
        self.entry = ttk.Entry(control_frame, style="TEntry")
        self.entry.pack(pady=5, fill=tk.X, ipady=4)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=10, fill=tk.X)
        btn_insert = ttk.Button(btn_frame, text="Inserir", command=self.insert_value)
        btn_insert.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5, padx=(0,5))
        btn_delete = ttk.Button(btn_frame, text="Excluir", command=self.delete_value)
        btn_delete.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5, padx=(5,0))

        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(pady=5, fill=tk.X)
        btn_zoom_in = ttk.Button(zoom_frame, text="Zoom In (+)", command=lambda: self.zoom(1.1))
        btn_zoom_in.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5, padx=(0,5))
        btn_zoom_out = ttk.Button(zoom_frame, text="Zoom Out (-)", command=lambda: self.zoom(0.9))
        btn_zoom_out.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=5, padx=(5,0))

        btn_clear = ttk.Button(control_frame, text="Limpar Árvore", command=self.clear_tree)
        btn_clear.pack(pady=5, fill=tk.X, ipady=5)

        ttk.Label(control_frame, text="Histórico", style="History.TLabel").pack(pady=(20, 10), anchor="w")
        self.history_text = scrolledtext.ScrolledText(control_frame, height=10, state='disabled', bg="#2E2E2E", fg=TEXT_COLOR, font=("Consolas", 10), relief="flat")
        self.history_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.bind('<Return>', lambda event=None: self.insert_value())
        self.entry.focus()

    def insert_value(self):
        raw_value = self.entry.get()
        if not raw_value.isalpha() or len(raw_value) != 1:
            messagebox.showerror("Erro de Entrada", "Por favor, insira uma única letra do alfabeto (A-Z).")
        else:
            value = raw_value.upper()
            if self.tree.insert(value):
                self.add_history(f"Inserido: {value}")
                self.draw_tree()
            else:
                messagebox.showinfo("Aviso", f"A chave '{value}' já existe na árvore.")
        self.entry.delete(0, tk.END)

    def delete_value(self):
        raw_value = self.entry.get()
        if not raw_value.isalpha() or len(raw_value) != 1:
            messagebox.showerror("Erro de Entrada", "Por favor, insira uma única letra do alfabeto (A-Z).")
            return
        value = raw_value.upper()
        try:
            self.tree.delete(value)
            self.add_history(f"Excluído: {value}")
            self.draw_tree()
        except ValueError as e: 
            messagebox.showerror("Erro", f"{e}")
        finally:
            self.entry.delete(0, tk.END)

    def clear_tree(self):
        self.tree = BPlusTree(self.tree.t)
        self.zoom_factor = 1.0
        self.add_history("--- Árvore Limpa ---")
        self.draw_tree()
        
    def add_history(self, message):
        self.history_text.config(state='normal')
        self.history_text.insert(tk.END, message + "\n")
        self.history_text.config(state='disabled')
        self.history_text.see(tk.END)

    def zoom(self, factor):
        self.zoom_factor *= factor
        self.draw_tree()

    def draw_tree(self):
        self.canvas.delete("all")
        self.node_coords.clear()
        if self.tree.root and (self.tree.root.keys or not self.tree.root.leaf):
            dims = self._calculate_tree_dimensions(self.tree.root)
            total_width, total_height = dims['width'] + 100 * self.zoom_factor, dims['height'] + 100 * self.zoom_factor
            self.canvas.config(scrollregion=(0, 0, total_width, total_height))
            start_x, start_y = total_width / 2, 60 * self.zoom_factor
            self._draw_node(self.tree.root, start_x, start_y)
            self._draw_leaf_links()
    
    def _draw_leaf_links(self):
        first_leaf = self.tree.root
        if not first_leaf: return
        while not first_leaf.leaf: first_leaf = first_leaf.children[0]
        current = first_leaf
        while current and current.next:
            if current in self.node_coords and current.next in self.node_coords:
                x1, y1 = self.node_coords[current]
                x2, y2 = self.node_coords[current.next]
                self.canvas.create_line(x1 + 20, y1 + 10, x1 + 30, y1 + 40, x2 - 30, y2 + 40, x2 - 20, y2 + 10, 
                                        arrow=tk.LAST, fill="#D93025", width=1.5, smooth=True)
            current = current.next

    def _draw_node(self, node, x, y):
        self.node_coords[node] = (x, y)
        node_h, key_w, key_p = 35*self.zoom_factor, 35*self.zoom_factor, 5*self.zoom_factor
        level_h, font_s = 90*self.zoom_factor, int(11*self.zoom_factor)
        node_w = len(node.keys) * key_w + (len(node.keys) + 1) * key_p
        if node_w == 0: node_w = key_w
        x1, y1, x2, y2 = x - node_w/2, y - node_h/2, x + node_w/2, y + node_h/2
        fill_color = LEAF_NODE_FILL if node.leaf else NODE_FILL
        self._create_rounded_rectangle(x1, y1, x2, y2, radius=10*self.zoom_factor, fill=fill_color, outline=NODE_OUTLINE, width=2)
        key_x_start = x1 + key_p + key_w / 2
        for key in node.keys:
            self.canvas.create_text(key_x_start, y, text=str(key), font=(FONT_FAMILY, font_s, "bold"), fill=NODE_TEXT_COLOR)
            key_x_start += key_w + key_p
        if not node.leaf:
            child_y = y + level_h
            child_dims = [self._calculate_tree_dimensions(c)['width'] for c in node.children]
            child_total_w = sum(child_dims) + 30*self.zoom_factor*(len(node.children) - 1)
            current_x = x - child_total_w / 2
            for i, child in enumerate(node.children):
                child_w = child_dims[i]
                child_x = current_x + child_w / 2
                self.canvas.create_line(x, y + node_h/2, child_x, child_y - node_h/2, fill=CONTROL_BG, width=2)
                self._draw_node(child, child_x, child_y)
                current_x += child_w + 30 * self.zoom_factor

    def _calculate_tree_dimensions(self, node):
        if not node or (node.leaf and not node.keys): return {'width': 0, 'height': 0}
        node_width = len(node.keys) * (35*self.zoom_factor) + (len(node.keys) + 1) * (5*self.zoom_factor)
        level_h = 90 * self.zoom_factor
        if node.leaf: return {'width': node_width, 'height': level_h}
        children_width, max_child_height = 0, 0
        for child in node.children:
            dims = self._calculate_tree_dimensions(child)
            children_width += dims['width']
            if dims['height'] > max_child_height: max_child_height = dims['height']
        spacing = 30 * self.zoom_factor * (len(node.children) - 1)
        total_width, total_height = max(node_width, children_width + spacing), level_h + max_child_height
        return {'width': total_width, 'height': total_height}

    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, 
                  x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
                  x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, 
                  x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

if __name__ == '__main__':
    app = BPlusTreeVisualizer(t=2)
    app.after(100, app.draw_tree)
    app.mainloop()