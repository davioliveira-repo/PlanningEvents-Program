import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "Planning Events - Gestão de Eventos"

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_FILE = SCRIPT_DIR / "events.json"

eventos = {}
ID_CONTADOR = 1
DEFAULT_THEME = "vista"

def load_events():
    global eventos, ID_CONTADOR
    if not DATA_FILE.exists():
        eventos = {}
        ID_CONTADOR = 1
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
        eventos = {int(k): v for k, v in payload.get("eventos", {}).items()}
        next_id = payload.get("next_id")
        if next_id is None:
            ID_CONTADOR = (max(eventos.keys()) + 1) if eventos else 1
        else:
            ID_CONTADOR = int(next_id)
    except Exception as e:
        messagebox.showwarning(APP_NAME, f"Falha ao carregar dados: {e}")
        eventos = {}
        ID_CONTADOR = 1

def save_events():
    try:
        payload = {"eventos": {str(k): v for k, v in eventos.items()}, "next_id": ID_CONTADOR}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        root = tk._get_default_root()
        if root:
            messagebox.showerror(APP_NAME, f"Falha ao salvar dados: {e}", parent=root)
        else:
            messagebox.showerror(APP_NAME, f"Falha ao salvar dados: {e}")

def apply_style(root, style):
    try:
        style.theme_use(DEFAULT_THEME)
        root.configure(bg=None)
        style.configure("TLabel", background=None, foreground=None)
        style.configure("TFrame", background=None)
        style.configure("TButton", background=None, foreground=None)
        style.configure("TEntry", fieldbackground=None, foreground=None)
        style.configure("Treeview", background=None, fieldbackground=None, foreground=None)
        style.configure("Treeview.Heading", background=None, foreground=None)
        style.map("Treeview", background=[("selected", None)])
    except Exception:
        pass

def atualizar_treeview(tree):
    tree.delete(*tree.get_children())
    for id_evento, dados in sorted(eventos.items()):
        tree.insert("", "end", iid=str(id_evento), text=str(id_evento), values=(
            dados.get("nome", ""),
            dados.get("data", ""),
            dados.get("local", ""),
            dados.get("telefone", ""),
            len(dados.get("inscricoes", []))
        ))

def abrir_adicionar_evento(parent, tree, style):
    win = tk.Toplevel(parent)
    win.title("Adicionar Evento")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    win.lift()

    frm = ttk.Frame(win, padding=12)
    frm.grid()

    nome_var = tk.StringVar()
    data_var = tk.StringVar()
    local_var = tk.StringVar()
    tel_var = tk.StringVar()

    ttk.Label(frm, text="Nome do Evento:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=nome_var, width=40).grid(row=0, column=1, pady=2)
    ttk.Label(frm, text="Data (DD/MM/AAAA):").grid(row=1, column=0, sticky="w")
    ttk.Entry(frm, textvariable=data_var, width=40).grid(row=1, column=1, pady=2)
    ttk.Label(frm, text="Local do Evento:").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=local_var, width=40).grid(row=2, column=1, pady=2)
    ttk.Label(frm, text="Telefone para Contato:").grid(row=3, column=0, sticky="w")
    ttk.Entry(frm, textvariable=tel_var, width=40).grid(row=3, column=1, pady=2)

    def salvar():
        global ID_CONTADOR

        nonlocal nome_var, data_var, local_var, tel_var
        nome = nome_var.get().strip()
        data = data_var.get().strip()
        local = local_var.get().strip()
        tel = tel_var.get().strip()
        if not nome or not data or not local:
            messagebox.showerror("Erro", "Nome, Data e Local são obrigatórios.", parent=win)
            return
        novo = {"nome": nome, "data": data, "local": local, "telefone": tel, "inscricoes": []}
        eventos[ID_CONTADOR] = novo
        ID_CONTADOR += 1
        save_events()
        atualizar_treeview(tree)
        messagebox.showinfo("Sucesso", f"Evento '{nome}' criado.", parent=win)
        win.destroy()

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=(8,0))
    ttk.Button(btn_frame, text="Salvar", command=salvar).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=win.destroy).grid(row=0, column=1, padx=6)

def abrir_inscrever_participante(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(APP_NAME, "Selecione um evento.", parent=parent)
        return
    id_evento = int(selected[0])
    dados = eventos.get(id_evento)
    if dados is None:
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=parent)
        return

    win = tk.Toplevel(parent)
    win.title(f"Inscrever em: {dados.get('nome')}")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    win.lift()

    frm = ttk.Frame(win, padding=12)
    frm.grid()
    nome_var = tk.StringVar()
    email_var = tk.StringVar()
    ttk.Label(frm, text="Nome Completo:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=nome_var, width=40).grid(row=0, column=1, pady=2)
    ttk.Label(frm, text="Email:").grid(row=1, column=0, sticky="w")
    ttk.Entry(frm, textvariable=email_var, width=40).grid(row=1, column=1, pady=2)

    def salvar():
        nome = nome_var.get().strip()
        email = email_var.get().strip()
        if not nome or not email:
            messagebox.showerror("Erro", "Nome e Email são obrigatórios.", parent=win)
            return
        participante = {"nome": nome, "email": email}
        dados.setdefault("inscricoes", []).append(participante)
        save_events()
        atualizar_treeview(tree)
        messagebox.showinfo("Sucesso", f"{nome} inscrito(a).", parent=win)
        win.destroy()

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=(8,0))
    ttk.Button(btn_frame, text="Inscrever", command=salvar).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=win.destroy).grid(row=0, column=1, padx=6)

def abrir_consultar_inscritos(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(APP_NAME, "Selecione um evento.", parent=parent)
        return
    id_evento = int(selected[0])
    dados = eventos.get(id_evento)
    if dados is None:
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=parent)
        return
    inscritos = dados.get("inscricoes", [])
    texto = f"Evento: {dados.get('nome')} (ID {id_evento})\nTotal de inscritos: {len(inscritos)}\n\n"
    for p in inscritos:
        texto += f"- {p.get('nome')} ({p.get('email')})\n"
    win = tk.Toplevel(parent)
    win.title("Inscritos")
    win.transient(parent)
    win.grab_set()
    win.lift()
    txt = tk.Text(win, width=70, height=20)
    txt.insert("1.0", texto)
    txt.config(state="disabled")
    txt.pack(padx=8, pady=8)

def abrir_remover_participante(parent, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning(APP_NAME, "Selecione um evento.", parent=parent)
        return
    id_evento = int(selected[0])
    dados = eventos.get(id_evento)
    if dados is None:
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=parent)
        return

    inscritos = dados.get("inscricoes", [])
    if not inscritos:
        messagebox.showinfo("Sem inscritos", "Este evento não possui inscritos.", parent=parent)
        return

    win = tk.Toplevel(parent)
    win.title(f"Remover Inscrito - {dados.get('nome')}")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)
    win.lift()

    frm = ttk.Frame(win, padding=12)
    frm.grid(row=0, column=0)

    ttk.Label(frm, text=f"Inscritos ({len(inscritos)}):").grid(row=0, column=0, sticky="w")

    listbox = tk.Listbox(frm, width=60, height=12, exportselection=False)
    for p in inscritos:
        listbox.insert("end", f"{p.get('nome')} ({p.get('email')})")
    listbox.grid(row=1, column=0, pady=(6,0))

    btn_frame = ttk.Frame(frm)
    btn_frame.grid(row=2, column=0, pady=(8,0))

    def remover_selecionado():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Seleção", "Selecione um inscrito para remover.", parent=win)
            return
        idx = sel[0]
        participante = inscritos[idx]
        nome = participante.get("nome", "—")
        if messagebox.askyesno("Confirmar", f"Remover {nome} do evento?", parent=win):
            try:
                dados["inscricoes"].pop(idx)
                save_events()
                atualizar_treeview(tree)
                messagebox.showinfo("Removido", f"{nome} foi removido.", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao remover participante: {e}", parent=win)

    def cancelar():
        win.destroy()

    ttk.Button(btn_frame, text="Remover Selecionado", command=remover_selecionado).grid(row=0, column=0, padx=6)
    ttk.Button(btn_frame, text="Cancelar", command=cancelar).grid(row=0, column=1, padx=6)

def remover_evento(tree):
    selected = tree.selection()
    if not selected:
        root = tree.winfo_toplevel()
        messagebox.showwarning(APP_NAME, "Selecione um evento para remover.", parent=root)
        return
    id_evento = int(selected[0])
    ev = eventos.get(id_evento)
    if not ev:
        root = tree.winfo_toplevel()
        messagebox.showerror(APP_NAME, "Evento não encontrado.", parent=root)
        return
    root = tree.winfo_toplevel()
    if messagebox.askyesno(APP_NAME, f"Remover '{ev.get('nome')}' (ID {id_evento})?", parent=root):
        del eventos[id_evento]
        save_events()
        atualizar_treeview(tree)

def criar_interface():
    load_events()

    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("940x540")

    style = ttk.Style(root)
    try:
        style.theme_use(DEFAULT_THEME)
    except Exception:
        try:
            style.theme_use("default")
        except Exception:
            pass

    header = ttk.Frame(root, padding=(12,8))
    header.pack(fill="x")
    ttk.Label(header, text="Planning Events", font=(None, 16, "bold")).pack(anchor="w")
    ttk.Label(header, text="Gerencie eventos: adicionar, inscrever participantes e exportar.").pack(anchor="w")

    bar = ttk.Frame(root, padding=(8,6))
    bar.pack(fill="x")

    tree_frame = ttk.Frame(root, padding=8)
    tree_frame.pack(fill="both", expand=True)

    cols = ("Nome", "Data", "Local", "Contato", "Inscritos")
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

    tree.heading("#0", text="ID")
    tree.column("#0", width=60, minwidth=40, anchor="center", stretch=tk.NO)

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="w")

    tree.column("Nome", width=360)
    tree.column("Data", width=120, anchor="center")
    tree.column("Local", width=220)
    tree.column("Contato", width=160)
    tree.column("Inscritos", width=100, anchor="center")

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    ttk.Button(bar, text="Adicionar Evento", command=lambda: abrir_adicionar_evento(root, tree, style)).pack(side="left", padx=6)
    ttk.Button(bar, text="Inscrever Participante", command=lambda: abrir_inscrever_participante(root, tree)).pack(side="left", padx=6)
    ttk.Button(bar, text="Consultar Inscritos", command=lambda: abrir_consultar_inscritos(root, tree)).pack(side="left", padx=6)
    ttk.Button(bar, text="Remover Participante", command=lambda: abrir_remover_participante(root, tree)).pack(side="left", padx=6)
    ttk.Button(bar, text="Remover Evento", command=lambda: remover_evento(tree)).pack(side="left", padx=6)

    ttk.Button(bar, text="Sair", command=root.quit).pack(side="right", padx=6)

    atualizar_treeview(tree)

    def on_close():
        save_events()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    apply_style(root, style)
    root.mainloop()

if __name__ == "__main__":
    criar_interface()
