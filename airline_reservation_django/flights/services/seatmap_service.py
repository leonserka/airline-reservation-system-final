SEAT_LETTERS = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}


def build_seat_positions(total_seats, taken_seats, selected_seats, seats_per_row=4):
    seat_positions = []
    for r in range(1, total_seats // seats_per_row + 1):
        row = {"row_number": r, "left": [], "right": []}
        for s in range(1, seats_per_row + 1):
            seat_id = f"{r}{SEAT_LETTERS[s]}"
            pos = {"seat_id": seat_id, "occupied": seat_id in taken_seats or seat_id in selected_seats}
            (row["left"] if s <= 2 else row["right"]).append(pos)
        seat_positions.append(row)
    return seat_positions
