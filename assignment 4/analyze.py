import json

def analyze():
    with open('Task.ipynb', encoding='utf-8') as f:
        nb = json.load(f)
    
    with open('structure.txt', 'w', encoding='utf-8') as f:
        for i, cell in enumerate(nb.get('cells', [])):
            cell_type = cell.get('cell_type')
            source = "".join(cell.get('source', []))[:100].replace('\n', ' ')
            f.write(f"{i}: {cell_type} - {source}\n")

if __name__ == '__main__':
    analyze()
