from IPython.display import display, HTML

class StyledHexCardGenerator:
    """
    A class to generate and display a styled HTML card.
    """
    def __init__(self, card_name: str, card_value: str, has_card_percent: bool = False, 
                 card_percent_value: str = "", card_background_color: str = "#f0f0f0"):
        """
        Initializes the StyledHexCardGenerator with the card details.

        Args:
            card_name (str): The name or title of the card.
            card_value (str): The main value to display on the card.
            has_card_percent (bool): If True, a percentage value will be displayed. Defaults to False.
            card_percent_value (str): The percentage value to display. Only used if has_card_percent is True.
                                      Defaults to an empty string.
            card_background_color (str): The background color for the card container. Defaults to a light grey.
        """
        self.card_name = card_name
        self.card_value = card_value
        self.has_card_percent = has_card_percent
        self.card_percent_value = card_percent_value
        self.card_background_color = card_background_color

    def display_card(self):
        """
        Generates the complete HTML for the styled card and displays it using IPython.display.
        """
        # Base HTML template for the card
        html_card_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Card</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Modern, clean font */
            margin: 20px;
            color: #333; /* Dark, readable text */
            transition: background-color 0.3s ease, color 0.3s ease;
            display: flex; /* Center the card on the page */
            justify-content: center;
            align-items: center;
        }}

        .header {{
            background-color: {card_bg_color}; /* Modern primary color */
            color: white;
            padding: 16px 20px;
            font-weight: 500; /* Slightly lighter font weight */
            font-size: 1.1em;
            text-align: center; /* Align header text to the left */
        }}

        .value {{
            padding: 24px 20px; /* Increased padding for better visual spacing */
            font-size: 2.2em; /* Larger, more prominent value */
            color: #777;; /* Modern success color for emphasis */
            text-align: center;
            font-weight: bold; /* Emphasize the main value */
        }}

        .percent-placeholder {{
            font-size: 0.9em; /* Slightly smaller, muted percentage */
            color: #6c757d; /* Muted gray color */
            padding: 10px 20px 20px;
            text-align: center;
            border-top: 1px solid #eee; /* Subtle separator */
        }}


        .container {{
            border-radius: 12px; /* More pronounced rounded corners */
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); /* Softer, modern shadow */
            overflow: hidden;
            width: 500px; /* Example fixed width for the card */
            border: 1px solid #777;
            transition: transform 0.3s ease-in-out; /* Smooth hover effect */
        }}

        .container:hover {{
            transform: translateY(-5px); /* Lift effect on hover */
        }}
        
        @media (max-width: 600px) {{
            .container {{
                width: 95%; /* Adjust width for smaller screens */
            }}
            .value {{
                font-size: 1.8em; /* Smaller font for values on small screens */
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">{card_name_placeholder}</div>
        <div class="value">{card_value_placeholder}</div>
        {percent_section}
    </div>
</body>
</html>
        """

        percent_section = ""
        if self.has_card_percent:
            percent_section = f"<div class='percent-placeholder'>{self.card_percent_value}</div>"

        # Format the final HTML with dynamic content
        final_html = html_card_template.format(
            card_name_placeholder=self.card_name,
            card_value_placeholder=self.card_value,
            percent_section=percent_section,
            card_bg_color=self.card_background_color
        )
        
        display(HTML(final_html))
