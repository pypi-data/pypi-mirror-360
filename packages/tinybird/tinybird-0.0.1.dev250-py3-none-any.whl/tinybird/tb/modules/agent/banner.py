import click


def display_banner():
    reset = "\033[0m"

    click.echo("\n")
    # The Tinybird Code ASCII art banner
    banner = [
        "  ████████╗██╗███╗   ██╗██╗   ██╗██████╗ ██╗██████╗ ██████╗     ██████╗ ██████╗ ██████╗ ███████╗",
        "  ╚══██╔══╝██║████╗  ██║╚██╗ ██╔╝██╔══██╗██║██╔══██╗██╔══██╗   ██╔════╝██╔═══██╗██╔══██╗██╔════╝",
        "     ██║   ██║██╔██╗ ██║ ╚████╔╝ ██████╔╝██║██████╔╝██║  ██║   ██║     ██║   ██║██║  ██║█████╗  ",
        "     ██║   ██║██║╚██╗██║  ╚██╔╝  ██╔══██╗██║██╔══██╗██║  ██║   ██║     ██║   ██║██║  ██║██╔══╝  ",
        "     ██║   ██║██║ ╚████║   ██║   ██████╔╝██║██║  ██║██████╔╝   ╚██████╗╚██████╔╝██████╔╝███████╗",
        "     ╚═╝   ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═════╝ ╚═╝╚═╝  ╚═╝╚═════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝",
    ]

    def interpolate_color(start_rgb, end_rgb, factor):
        """Interpolate between two RGB colors"""
        return [int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * factor) for i in range(3)]

    def rgb_to_ansi(r, g, b):
        """Convert RGB values to ANSI escape code"""
        return f"\033[38;2;{r};{g};{b}m"

    # Define start and end colors for smooth gradient
    start_color = [0, 128, 128]  # Deep teal
    end_color = [100, 200, 180]  # Light turquoise

    # Print each line with a very smooth horizontal gradient
    for line in banner:
        colored_line = ""
        # Count non-space characters for gradient calculation
        non_space_chars = sum(1 for char in line if char != " ")
        char_count = 0

        for char in line:
            if char == " ":
                colored_line += char
                continue

            # Calculate smooth gradient position (0.0 to 1.0)
            if non_space_chars > 1:
                gradient_position = char_count / (non_space_chars - 1)
            else:
                gradient_position = 0

            # Interpolate color
            current_rgb = interpolate_color(start_color, end_color, gradient_position)
            color_code = rgb_to_ansi(*current_rgb)

            colored_line += f"{color_code}{char}"
            char_count += 1

        click.echo(colored_line + reset)
