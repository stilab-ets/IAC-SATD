from RQ1_Taxonomy_Construction.SATD_collector.CommentsMining.SatdKeyWordLists import keywordList1


def find_keyword_in_multiline_comment(comment):
    lines = comment.split('\n')  # Split the multiline comment into lines
    for i, line in enumerate(lines, start=1):  # Iterate through lines with line numbers
        for keyword in keywordList1:  # Iterate through keywords
            if keyword in line.lower():  # Check if the keyword is in the line
                return line, i  # Return the line and its line number
    return None  # Return None if no keyword found


