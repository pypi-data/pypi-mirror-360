import pandas as pd
from IPython.display import display, HTML

class StyledHexTableGenerator:
    """
    A class to generate and display a styled HTML table from a Pandas DataFrame.
    """
    def __init__(self, dataframe: pd.DataFrame, color_map: dict, footer: bool, aggregation: str, 
                 color_header: bool = False, color_cell: bool = False, opacity: float = None, height_in_px: str = None, round_values: int=0):
        """
        Initializes the StyledHTMLTableGenerator with the necessary data and configuration.

        Args:
            dataframe (pd.DataFrame): The input Pandas DataFrame.
            color_map (dict): A dictionary mapping column names to rgba color strings (e.g., 'rgba(255, 0, 0, 1)').
            footer (bool): If True, a footer row with aggregation will be included.
            aggregation (str): The type of aggregation for the footer ('sum' or 'avg').
            color_header (bool): If True, table headers will be colored according to color_map.
            color_cell (bool): If True, table cells will be colored according to color_map.
            opacity (float, optional): An optional opacity value (0.0 to 1.0) to apply to colors.
                                       If None, the opacity from color_map will be used.
        """
        self.dataframe = dataframe
        self.color_map = color_map
        self.footer = footer
        self.aggregation = aggregation
        self.color_header = color_header
        self.color_cell = color_cell
        self.opacity = opacity
        self.height_in_px = height_in_px
        self.round_values = round_values
        # Create column_to_css_map_suffix using a dictionary comprehension based on color_map keys
        self.column_to_css_map_suffix = {key: key.replace(' ', '-').lower() for key in color_map.keys()}

    def _generate_css_styles(self) -> str:
        """
        Generates dynamic CSS styles based on the color map, opacity, and coloring flags.

        Returns:
            str: The CSS string.
        """
        css_styles = ""
        
        # Add hover effect for table rows
        css_styles += """
    tbody tr:hover {
        background-color: #f0f0f0 !important; /* Light gray background on hover */
        cursor: pointer;
    }
        """

        for col_name, css_suffix in self.column_to_css_map_suffix.items():
            original_rgba = self.color_map.get(col_name)
            if not original_rgba:
                continue

            # Extract RGB components and original alpha
            parts = original_rgba.replace('rgba(', '').replace(')', '').split(',')
            r, g, b = [int(x.strip()) for x in parts[:3]]
            # Use provided opacity if available, otherwise use original alpha or default to 1 if no original alpha
            current_opacity = self.opacity if self.opacity is not None else (float(parts[3].strip()) if len(parts) > 3 else 1.0)
            
            rgba_with_applied_opacity = f"rgba({r}, {g}, {b}, {current_opacity})"

            # Determine text color based on luminance for contrast
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            text_color = "white" if luminance < 0.5 else "#01011b" # A very dark blue for light backgrounds

            if self.color_cell:
                css_styles += f"""
    .column-{css_suffix} {{
        background-color: {rgba_with_applied_opacity} !important;
        color: {text_color} !important;
    }}
                """
            
            if self.color_header:
                css_styles += f"""
    .header-{css_suffix} {{
        background-color: {rgba_with_applied_opacity} !important;
        color: {text_color} !important;
        font-size: 12px;
        font-style: normal;
        font-weight: 400;
    }}
                """
        return css_styles

    def _generate_table_content(self) -> str:
        """
        Generates the HTML table body, header, and optional footer.

        Returns:
            str: The HTML string for the table content (excluding <style> and <body> tags).
        """
        df = self.dataframe
        col_css_map_suffix_param = self.column_to_css_map_suffix
        footer_enabled = self.footer
        agg_type = self.aggregation

        html_content = '<table>\n<thead>\n<tr>\n'
        
        # Table Header
        for col in df.columns:
            css_suffix = col_css_map_suffix_param.get(col)
            # Apply header-specific class only if color_header is true and a suffix exists for the column
            header_class = f'header-{css_suffix}' if self.color_header and css_suffix else ''
            html_content += f'<th class="{header_class}">{col}</th>\n'
        html_content += '</tr>\n</thead>\n<tbody>\n'

        # Table Body
        for _, row in df.iterrows():
            html_content += '<tr>\n'
            for col in df.columns:
                css_suffix = col_css_map_suffix_param.get(col)
                # Apply column-specific class for cells only if color_cell is true
                cell_class = f'column-{css_suffix}' if self.color_cell and css_suffix else ''
                val = '' if pd.isna(row[col]) else row[col]
                html_content += f'<td class="{cell_class}">{val}</td>\n'
            html_content += '</tr>\n'
        html_content += '</tbody>\n'

        # Table Footer (Conditional)
        if footer_enabled:
            html_content += '<tfoot>\n<tr>\n<td class="">Total</td>\n' # First cell is "Total"
            
            for col in df.columns[1:]: # Iterate through columns starting from the second one
                footer_cell_class = '' # Footers generally have a consistent background, not column-specific colors
                
                try:
                    numeric_col = pd.to_numeric(df[col].astype(str).str.replace('%', ''), errors='coerce')
                    if agg_type == 'sum':
                        total = numeric_col.sum()
                    elif agg_type == 'avg':
                        total = numeric_col.mean()
                    else:
                        total = '' # Fallback for unknown aggregation

                    val = round(total, self.round_values)
                    print('val', val)
                except Exception:
                    val = '' # Handle non-numeric columns or errors

                html_content += f'<td class="{footer_cell_class}">{val}</td>\n'
            html_content += '</tr>\n</tfoot>\n'
        
        html_content += '</table>\n'
        return html_content

    def display_table(self):
        """
        Generates the complete HTML for the styled table and displays it using IPython.display.
        """
        css_styles = self._generate_css_styles()
        html_table_content = self._generate_table_content()
        height_in_px = self.height_in_px if self.height_in_px else "100%"
        final_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <style>
            body {{
            font-family: Arial, sans-serif;
            background: white;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            min-width: 900px;
        }}
        th td {{
            border: 1px solid #ecedf2;
            padding: 8px;
            text-align: left;
            white-space: nowrap;
            color: #afb4c2;
        }}
        tbody td {{
            border: 1px solid #ecedf2; /* Add a border around the table body */
            background-color: #ffffff; /* Light background for the body */
        }}
        tbody tr:nth-child(even) td {{
            background-color: transparent; /* Light gray for even rows */
            font-size: 12px;
            font-style: normal;
            font-weight: 400;
        }}
        tbody tr:nth-child(odd) td {{
            background-color: transparent; /* Light gray for even rows */
            font-size: 12px;
            font-style: normal;
            font-weight: 400;
        }}
        thead th {{
            position: sticky;
            top: 0;
            background: #f8f9fa;
            color: #848995;
            font-size: 12px;
            font-style: normal;
            font-weight: 400;
            border: 1px solid #ecedf2;
            z-index: 10;
        }}
        tfoot td {{
            background-color: #e2e8f0 !important;
            font-size: 12px;
            font-style: normal;
            font-weight: 400;
        }}
        .table-container {{
            border-radius: 8px;
            overflow-y: auto;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for the container */
            height: {height_in_px};
        }}
        {css_styles}
    </style>
</head>
<body>
    <div class="table-container">
        {html_table_content}
    </div>
</body>
</html>
        """
        display(HTML(final_html))
