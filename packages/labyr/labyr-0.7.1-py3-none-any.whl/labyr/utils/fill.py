def fill_rect(matrix, coord1, coord2, char):
    rows, cols = len(matrix), len(matrix[0])

    def norm(idx, size):
        return idx if idx >= 0 else size + idx

    x1, y1 = norm(coord1[0], rows), norm(coord1[1], cols)
    x2, y2 = norm(coord2[0], rows), norm(coord2[1], cols)
    row_start, row_end = sorted([x1, x2])
    col_start, col_end = sorted([y1, y2])
    for i in range(row_start, row_end + 1):
        for j in range(col_start, col_end + 1):
            matrix[i][j] = char
