import pandas as pd
from IPython.display import display, HTML

class StyledSubheaderGenerator:
    """
    A class to generate and display a styled HTML subheader with horizontal lines.
    """
    def __init__(self, subheader_text: str):
        """
        Initializes the StyledSubheaderGenerator with the subheader text.

        Args:
            subheader_text (str): The text to display in the subheader.
        """
        self.subheader_text = subheader_text

    def display_subheader(self):
        """
        Generates the complete HTML for the styled subheader and displays it using IPython.display.
        """
        # Base HTML template for the subheader
        subheader_html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Centered Header with Horizontal Lines</title>
  <style>
    body {{
      background-color: rgba(0,0,0,0); /* Transparent background by default */
      margin: 0; /* Remove default body margin */
      display: flex;
      justify-content: center; /* Center horizontally */
      align-items: center; /* Center vertically (if body has height) */
      height: 100%; /* Ensure body takes full height for centering if used alone */
    }}
    .centered-header {{
      display: flex;
      align-items: center;   /* Vertically center line/text */
      justify-content: center; /* Horizontally center text within its container */
      margin: 20px 0;       /* Space above/below the header */
      border: 2px solid #FC8D62;
      padding: 10px 20px; /* Added horizontal padding */
      border-radius: 8px; /* Rounded corners for the border */
      max-width: 90%; /* Ensure responsiveness */
      box-sizing: border-box; /* Include padding and border in the element's total width and height */
    }}
    .centered-header::before,
    .centered-header::after {{
      content: "";
      flex: 1;                     /* Ensures lines stretch horizontally */
      border-bottom: 1px solid #777;  /* Grey horizontal line */
      margin: 0 15px;                  /* Spacing between line & text */
    }}
    .centered-header span {{
      color: #777;         /* Text color */
      font-family: Arial, sans-serif;
      font-size: 16px;      /* Adjust as needed */
      white-space: nowrap;  /* Prevent text from wrapping between the lines */
      text-align: center; /* Ensure text is centered if it wraps within nowrap container */
    }}
    @media (max-width: 600px) {{
        .centered-header {{
            margin: 10px 0;
            padding: 8px 15px;
        }}
        .centered-header span {{
            font-size: 14px;
        }}
        .centered-header::before,
        .centered-header::after {{
            margin: 0 10px;
        }}
    }}
  </style>
</head>
<body>

  <div class="centered-header">
    <span>{subheader_placeholder}</span>
  </div>

</body>
</html>
        """

        # Format the final HTML with the dynamic content
        final_html = subheader_html_template.format(
            subheader_placeholder=self.subheader_text
        )
        
        display(HTML(final_html))

