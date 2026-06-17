import pandas as pd
import unicodedata
from typing import List

def get_display_width(text: str) -> int:
    """Calculates the display width of a string, accounting for multi-byte characters."""
    width = 0
    for char in str(text):
        if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
            width += 2
        else:
            width += 1
    return width

def wrap_text(text: str, width: int) -> List[str]:
    """A simple text wrapper that respects display width and existing newlines."""
    lines = []
    for line in text.split('\n'):
        current_line = ""
        current_width = 0
        for char in line:
            char_width = get_display_width(char)
            if current_width + char_width > width:
                lines.append(current_line)
                current_line = char
                current_width = char_width
            else:
                current_line += char
                current_width += char_width
        if current_line:
            lines.append(current_line)
    return lines if lines else ['']

def format_df_as_grid(df: pd.DataFrame) -> str:
    """Formats a pandas DataFrame into a grid with text wrapping to fixed widths."""
    
    fixed_widths = {
        '受注No': 10,
        '出荷予定日': 10,
        '得意先コード': 5,
        '納入先コード': 5,
        '納入先': 8,
        '得意先名称1': 16,
        '納入先名称1': 16,
        '納入先名称2': 6,
        '品名': 18,
        '受注数量': 4,
        '受注単位': 4,
        '変換数量': 4,
        '変換単位': 4,
        '備考1': 8,
        '納期': 10,
        '運賃n缶分': 4,
        'Check': 16,
    }

    final_widths = {}
    for col in df.columns:
        if col in fixed_widths:
            final_widths[col] = fixed_widths[col]
        else:
            max_w = get_display_width(col)
            if not df[col].empty:
                max_w = max(max_w, df[col].fillna('').astype(str).apply(get_display_width).max())
            final_widths[col] = int(max_w)

    wrapped_header = {col: wrap_text(col, final_widths[col]) for col in df.columns}
    wrapped_data = df.fillna('').astype(str).apply(
        lambda col: col.apply(lambda cell: wrap_text(cell, final_widths[col.name]))
    )

    def create_separator(widths_dict):
        return '+' + '+'.join(['-' * (widths_dict.get(c, 0) + 2) for c in df.columns]) + '+'

    separator = create_separator(final_widths)
    lines = [separator]

    header_height = max((len(v) for v in wrapped_header.values()), default=1)
    for i in range(header_height):
        header_line_parts = []
        for col in df.columns:
            if i < len(wrapped_header[col]):
                header_line_parts.append(wrapped_header[col][i])
            else:
                header_line_parts.append('')
        
        cells = []
        for s, col_name in zip(header_line_parts, df.columns):
            w = final_widths[col_name]
            padding = w - get_display_width(s)
            cells.append(' ' + s + ' ' * padding + ' ')
        lines.append('|' + '|'.join(cells) + '|')
        
    lines.append(separator)

    for idx in df.index:
        row_data = wrapped_data.loc[idx]
        row_height = max((len(cell) for cell in row_data), default=1)
        
        for i in range(row_height):
            line_to_print = []
            for col in df.columns:
                cell_lines = row_data[col]
                if i < len(cell_lines):
                    line_to_print.append(cell_lines[i])
                else:
                    line_to_print.append('')
            
            cells = []
            for s, col_name in zip(line_to_print, df.columns):
                w = final_widths[col_name]
                padding = w - get_display_width(s)
                cells.append(' ' + s + ' ' * padding + ' ')
            lines.append('|' + '|'.join(cells) + '|')
            
        lines.append(separator)
        
    return '\n'.join(lines)
