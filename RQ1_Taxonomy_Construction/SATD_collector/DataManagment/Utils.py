def get_first_line(text):
    # Split the text by newline characters
    lines = text.split('\n')
    # Return the first line
    if lines:
        return lines[0]
    else:
        return text  # Return None if text is empty
    

def count_lines(text):
    # Compter le nombre de sauts de ligne dans le texte
    return text.count('\n') + 1 
