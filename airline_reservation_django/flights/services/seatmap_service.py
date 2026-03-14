SEAT_LETTERS = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}


def build_seat_positions(total_seats, taken_seats, selected_seats, seats_per_row=4):
    seat_positions = []
    num_rows = total_seats // seats_per_row

    for row_number in range(1, num_rows + 1):
        row = {
            "row_number": row_number,
            "left": [],
            "right": [],
        }
        for seat_index in range(1, seats_per_row + 1):
            seat_id = f"{row_number}{SEAT_LETTERS[seat_index]}"
            is_occupied = seat_id in taken_seats or seat_id in selected_seats
            seat = {"seat_id": seat_id, "occupied": is_occupied}
            if seat_index <= 2:
                row["left"].append(seat)
            else:
                row["right"].append(seat)
        seat_positions.append(row)

    return seat_positions
