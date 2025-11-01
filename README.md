
# Simulador Visual de Árvore B e Árvore B+

Este projeto é um simulador gráfico e interativo desenvolvido em Python para fins acadêmicos, focado em demonstrar o funcionamento das estruturas de dados **Árvore B** e **Árvore B+**.

O programa permite que o usuário insira e remova chaves (letras do alfabeto) e visualize em tempo real como a árvore se auto-balanceia através de operações de split, merge (fusão) e borrow (empréstimo/distribuição).

## Funcionalidades

* **Visualização Gráfica:** Renderização da árvore em um canvas, mostrando a hierarquia de nós e chaves.
* **Operações Completas:** Implementação de **Inserção** e **Remoção** com toda a lógica de rebalanceamento (divisão, fusão e distribuição).
* **Interface Interativa:** Painel de controle para adicionar, remover ou limpar a árvore.
* **Controle de Visualização:**
    * **Zoom In / Zoom Out** para inspecionar árvores grandes.
    * **Canvas Rolável** (barras de rolagem) para navegar por árvores que excedem o tamanho da tela.
* **Histórico de Operações:** Um log que registra todas as ações realizadas (inserções, exclusões, erros).
* **Chaves Alfabéticas:** O simulador aceita letras (A-Z) como chaves, tratando-as de forma *case-insensitive* (sempre convertidas para maiúsculas).

---

## Estruturas Implementadas

O projeto contém duas implementações separadas:

### 1. Árvore B (`arvore_b_gui.py`)

* Implementação clássica da **Árvore B**.
* As chaves são armazenadas tanto nos nós internos quanto nos nós folha.
* Os nós são visualizados na cor azul.

### 2. Árvore B+ (`arvore_b_plus_gui.py`)

* Implementação da **Árvore B+**, comumente usada em bancos de dados e sistemas de arquivos.
* **Diferenciação Visual:**
    * **Nós Internos (Azuis):** Contêm apenas chaves "guia" para a navegação.
    * **Nós Folha (Verdes):** Contêm todas as chaves de dados.
* **Lista Encadeada:** Os nós folha são interligados por uma lista encadeada (visualizada por **setas vermelhas**), permitindo a travessia sequencial rápida dos dados.

---

## Tecnologias Utilizadas

* **Python 3.x**
* **Tkinter** (módulos `tk` e `ttk`) para a construção da interface gráfica.

---

## Como Executar

Não são necessárias bibliotecas externas além das que vêm nativamente com o Python.

1.  Certifique-se de ter o [Python 3](https://www.python.org/downloads/) instalado.
2.  Salve os códigos-fonte em seus respectivos arquivos:
    * `arvore_b_gui.py` (para a Árvore B)
    * `arvore_b_plus_gui.py` (para a Árvore B+)
3.  Abra seu terminal ou prompt de comando.

**Para executar o simulador da Árvore B:**

```bash
python arvore_b_gui.py
