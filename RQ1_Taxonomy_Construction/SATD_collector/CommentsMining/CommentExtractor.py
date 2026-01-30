import re


def extract_comments(text):
    comments = []

    # Regular expression pattern to match single-line comments
    single_line_pattern = r'(?<!:)(//|#)(.*?)(?=\n|$)'
    # Regular expression pattern to match multi-line comments
    multi_line_pattern = r'/\*([\s\S]*?)\*/'

    # Extract single-line comments
    single_line_comments = re.finditer(single_line_pattern, text)
    for match in single_line_comments:
        comment_symbol = match.group(1)
        comment_text = match.group(2)
        comment = comment_symbol + comment_text
        line_number = text.count('\n', 0, match.start()) + 1
        comments.append((comment, line_number))

    # Extract multi-line comments
    multi_line_comments = re.finditer(multi_line_pattern, text)
    for match in multi_line_comments:
        comment = "/*" + match.group(1).strip() + "*/"
        line_number = text.count('\n', 0, match.start()) + 1
        comments.append((remove_n(comment), line_number))

    return comments


def trier_par_numero_ligne(comment_list):
    return sorted(comment_list, key=lambda x: x[1])


def fusionner_commentaires_en_bloc(comment_list):
    blocs = []
    bloc = [comment_list[0]]
    for i in range(1, len(comment_list)):
        if comment_list[i][1] == comment_list[i-1][1] + 1:
            bloc.append(comment_list[i])
        else:
            blocs.append(bloc)
            bloc = [comment_list[i]]
    blocs.append(bloc)

    resultat = []
    for bloc in blocs:
        concatenated_comment = '\n'.join(comment[0] for comment in bloc)
        resultat.append((concatenated_comment, bloc[0][1]))

    return resultat


def remove_newlines(text):
    return text.replace("\n", "")



def remove_n(text):
    text = text.replace("\n", " ")
    return text



def extract_comment_block(terraform_content, line_id):
    comment_blocks = []
    current_block = []
    start_line = None

    lines = terraform_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check if the line is a single-line comment
        if ((current_block and (line.strip().startswith('#') or line.strip().startswith('//'))) or (not(current_block) and ('//' in line or '#' in line))):
        #if '#' in line or '//' in line:
            if start_line is None:
                start_line = i + 1
            if current_block:
                current_block.append('\n')
            current_block.append(line.strip())
            i += 1
        # Check if the line starts a multi-line comment
        elif (current_block and line.strip().startswith('/*')) or (not(current_block) and ('/*' in line)):
            if start_line is None:
                start_line = i + 1
            while i < len(lines) and '*/' not in line:
                if current_block:
                    current_block.append('\n')
                current_block.append(line.strip())
                i += 1
                if(i<len(lines)):
                    line = lines[i]
            if current_block:
                current_block.append('\n')
            current_block.append(line.strip())
            i += 1
        # Check if the line is empty
        elif not line.strip():
            if current_block:
                current_block.append('')
            i += 1
        # Check if the line ends the current block
        else:
            if current_block:
                comment_blocks.append((' '.join(current_block), start_line, i))
                current_block = []
                start_line = None
            i += 1

    # Add the last block if there's any
    if current_block:
        comment_blocks.append((' '.join(current_block), start_line, i))

    for comment, start_line, end_line in comment_blocks:
        if(start_line<=line_id and line_id<=end_line):
            return comment
        
    #     
    if 0 < line_id <= len(lines):
        return lines[line_id - 1]