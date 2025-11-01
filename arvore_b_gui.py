import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# --------------------------------------------------------------------------
# PARTE 1: LÓGICA DA ÁRVORE B (BACKEND)
# --------------------------------------------------------------------------

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t
        self.leaf = leaf
        self.keys = []
        self.children = []

class BTree:
    def __init__(self, t):
        if t < 2:
            raise ValueError("A ordem da Árvore B (t) deve ser no mínimo 2.")
        self.root = BTreeNode(t, leaf=True)
        self.t = t

    def _split_child(self, x, i):
        t = self.t
        y = x.children[i]
        z = BTreeNode(t, leaf=y.leaf)
        x.keys.insert(i, y.keys[t - 1])
        x.children.insert(i + 1, z)
        z.keys = y.keys[t:(2 * t - 1)]
        y.keys = y.keys[0:(t - 1)]
        if not y.leaf:
            z.children = y.children[t:(2 * t)]
            y.children = y.children[0:t]

    def insert(self, k):
        if self.search(k):
            return False
        root = self.root
        if len(root.keys) == (2 * self.t - 1):
            temp = BTreeNode(self.t, leaf=False)
            self.root = temp
            temp.children.insert(0, root)
            self._split_child(temp, 0)
            self._insert_non_full(temp, k)
        else:
            self._insert_non_full(root, k)
        return True

    def _insert_non_full(self, x, k):
        i = len(x.keys) - 1
        if x.leaf:
            pos = 0
            while pos < len(x.keys) and k > x.keys[pos]:
                pos += 1
            x.keys.insert(pos, k)
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.children[i].keys) == (2 * self.t - 1):
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.children[i], k)
    
    def search(self, k, x=None):
        x = x if x is not None else self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return x
        elif x.leaf:
            return None
        else:
            return self.search(k, x.children[i])

    def delete(self, k):
        if not self.search(k):
            raise ValueError(f"Chave '{k}' não encontrada na árvore.")
        self._delete(self.root, k)
        if len(self.root.keys) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, x, k):
        t = self.t
        i = 0
        while i < len(x.keys) and k > x.keys[i]: i += 1
        if i < len(x.keys) and k == x.keys[i] and x.leaf:
            x.keys.pop(i)
        elif i < len(x.keys) and k == x.keys[i] and not x.leaf:
            if len(x.children[i].keys) >= t:
                pred = self._get_predecessor(x, i)
                x.keys[i] = pred
                self._delete(x.children[i], pred)
            elif len(x.children[i + 1].keys) >= t:
                succ = self._get_successor(x, i)
                x.keys[i] = succ
                self._delete(x.children[i + 1], succ)
            else:
                self._merge(x, i)
                self._delete(x.children[i], k)
        elif not x.leaf:
            if len(x.children[i].keys) == t - 1:
                self._fill(x, i)
            if i > len(x.keys):
                self._delete(x.children[i - 1], k)
            else:
                self._delete(x.children[i], k)

    def _fill(self, x, i):
        t = self.t
        if i != 0 and len(x.children[i - 1].keys) >= t: self._borrow_from_prev(x, i)
        elif i != len(x.children) - 1 and len(x.children[i + 1].keys) >= t: self._borrow_from_next(x, i)
        else:
            if i != len(x.children) - 1: self._merge(x, i)
            else: self._merge(x, i - 1)

    def _borrow_from_prev(self, x, i):
        child, sibling = x.children[i], x.children[i - 1]
        child.keys.insert(0, x.keys[i - 1])
        x.keys[i - 1] = sibling.keys.pop()
        if not child.leaf: child.children.insert(0, sibling.children.pop())

    def _borrow_from_next(self, x, i):
        child, sibling = x.children[i], x.children[i + 1]
        child.keys.append(x.keys[i])
        x.keys[i] = sibling.keys.pop(0)
        if not child.leaf: child.children.append(sibling.children.pop(0))

    def _merge(self, x, i):
        child, sibling = x.children[i], x.children[i + 1]
        child.keys.append(x.keys.pop(i))
        child.keys.extend(sibling.keys)
        if not child.leaf: child.children.extend(sibling.children)
        x.children.pop(i + 1)

    def _get_predecessor(self, x, i):
        current = x.children[i]
        while not current.leaf: current = current.children[-1]
        return current.keys[-1]

    def _get_successor(self, x, i):
        current = x.children[i + 1]
        while not current.leaf: current = current.children[0]
        return current.keys[0]

# --------------------------------------------------------------------------
# PARTE 2: INTERFACE GRÁFICA (FRONTEND)
# --------------------------------------------------------------------------
BG_COLOR, CANVAS_BG, CONTROL_BG = "#2E2E2E", "#F5F5F5", "#404040"
TEXT_COLOR, BUTTON_BG, BUTTON_FG = "#FFFFFF", "#007ACC", "#FFFFFF"
NODE_FILL, NODE_OUTLINE, NODE_TEXT_COLOR = "#4A90E2", "#005A9C", "#FFFFFF"
FONT_FAMILY = "Segoe UI"

class BTreeVisualizer(tk.Tk):
    def __init__(self, t=3):
        super().__init__()
        self.title("Simulador de Árvore B (Letras do Alfabeto)")
        self.geometry("1200x800")
        self.configure(bg=BG_COLOR)
        self.tree = BTree(t)
        self.zoom_factor = 1.0
        
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

        ttk.Label(control_frame, text=f"Árvore B (Ordem t={t})", style="Title.TLabel").pack(pady=(0, 20), anchor="w")
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
            self.entry.delete(0, tk.END)
            return
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
            self.entry.delete(0, tk.END)
            return
        value = raw_value.upper()
        try:
            self.tree.delete(value)
            self.add_history(f"Excluído: {value}")
            self.draw_tree()
        except ValueError as e: 
            messagebox.showerror("Erro de Valor", f"{e}")
        finally:
            self.entry.delete(0, tk.END)

    def clear_tree(self):
        self.tree = BTree(self.tree.t)
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
        if self.tree.root and self.tree.root.keys:
            dims = self._calculate_tree_dimensions(self.tree.root)
            total_width, total_height = dims['width'] + 100 * self.zoom_factor, dims['height'] + 100 * self.zoom_factor
            self.canvas.config(scrollregion=(0, 0, total_width, total_height))
            start_x, start_y = total_width / 2, 60 * self.zoom_factor
            self._draw_node(self.tree.root, start_x, start_y, total_width / 2)

    def _calculate_tree_dimensions(self, node):
        if not node: return {'width': 0, 'height': 0}
        node_width = len(node.keys) * (35 * self.zoom_factor) + (len(node.keys) + 1) * (5 * self.zoom_factor)
        level_height = 90 * self.zoom_factor
        if node.leaf: return {'width': node_width, 'height': level_height}
        children_width, max_child_height = 0, 0
        for child in node.children:
            dims = self._calculate_tree_dimensions(child)
            children_width += dims['width']
            if dims['height'] > max_child_height: max_child_height = dims['height']
        spacing = 30 * self.zoom_factor * (len(node.children) - 1)
        total_width, total_height = max(node_width, children_width + spacing), level_height + max_child_height
        return {'width': total_width, 'height': total_height}

    def _draw_node(self, node, x, y, horizontal_spacing):
        node_h, key_w, key_p = 35 * self.zoom_factor, 35 * self.zoom_factor, 5 * self.zoom_factor
        level_h, font_s = 90 * self.zoom_factor, int(11 * self.zoom_factor)
        node_w = len(node.keys) * key_w + (len(node.keys) + 1) * key_p
        x1, y1, x2, y2 = x - node_w / 2, y - node_h / 2, x + node_w / 2, y + node_h / 2
        self._create_rounded_rectangle(x1, y1, x2, y2, radius=10 * self.zoom_factor, fill=NODE_FILL, outline=NODE_OUTLINE, width=2)
        key_x_start = x1 + key_p + key_w / 2
        for i, key in enumerate(node.keys):
            self.canvas.create_text(key_x_start + i * (key_w + key_p), y, text=str(key), font=(FONT_FAMILY, font_s, "bold"), fill=NODE_TEXT_COLOR)
        if not node.leaf:
            child_y = y + level_h
            child_dims = [self._calculate_tree_dimensions(c)['width'] for c in node.children]
            child_total_w = sum(child_dims) + 30 * self.zoom_factor * (len(node.children) - 1)
            current_x = x - child_total_w / 2
            for i, child in enumerate(node.children):
                child_w = child_dims[i]
                child_x = current_x + child_w / 2
                self.canvas.create_line(x, y + node_h/2, child_x, child_y - node_h/2, fill=CONTROL_BG, width=2)
                self._draw_node(child, child_x, child_y, horizontal_spacing / len(node.children))
                current_x += child_w + 30 * self.zoom_factor
    
    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
       
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, 
                  x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, 
                  x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, 
                  x1, y1+radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

if __name__ == '__main__':
    app = BTreeVisualizer(t=3)
   
    app.after(100, app.draw_tree)
    app.mainloop()