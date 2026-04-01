from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'


def main():
    md_path = OUT / 'academic_tables.md'
    tex_path = OUT / 'academic_tables.tex'

    content = md_path.read_text(encoding='utf-8') if md_path.exists() else ''

    tex = []
    tex.append('% Auto-generated lightweight LaTeX export')
    tex.append('% For publication-style tables, extend this formatter as needed.')
    tex.append('\\section*{Fama-French 1993-style (E/P Value Leg) Tables}')
    tex.append('\\begin{verbatim}')
    tex.append(content)
    tex.append('\\end{verbatim}')

    tex_path.write_text('\n'.join(tex), encoding='utf-8')
    print('Done:', tex_path)


if __name__ == '__main__':
    main()
