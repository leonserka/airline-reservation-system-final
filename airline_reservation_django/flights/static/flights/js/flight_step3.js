document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById('selected_seats_json');
    const form = input ? input.closest('form') : null;
    const confirmBtn = document.getElementById('confirm-seats-btn');
    const counterEl = document.getElementById('seat-counter');
    const recommendedSeat = document.getElementById('recommended-seat');
    const numPassengers = parseInt(document.getElementById('num-passengers').value || '1', 10);

    if (!input || !form) return;

    let selectedSeats = new Set();
    try {
        const pre = JSON.parse(document.getElementById('pre-selected-seats').textContent || '[]');
        pre.forEach(s => selectedSeats.add(s));
    } catch (e) {}

    function update() {
        document.querySelectorAll('.seat').forEach(function (seat) {
            if (seat.classList.contains('occupied')) return;
            if (selectedSeats.has(seat.dataset.seat)) {
                seat.classList.add('selected');
            } else {
                seat.classList.remove('selected');
            }
        });

        const count = selectedSeats.size;
        if (counterEl) counterEl.textContent = count + ' / ' + numPassengers;
        input.value = JSON.stringify(Array.from(selectedSeats));

        if (confirmBtn) {
            confirmBtn.disabled = count !== numPassengers;
        }
        if (recommendedSeat) {
            recommendedSeat.textContent = Array.from(selectedSeats)[0] || '--';
        }
    }

    function toggleSeat(seat) {
        const id = seat.dataset.seat;
        if (selectedSeats.has(id)) {
            selectedSeats.delete(id);
        } else if (selectedSeats.size < numPassengers) {
            selectedSeats.add(id);
        }
        update();
    }

    document.querySelectorAll('.seat:not(.occupied)').forEach(function (seat) {
        seat.addEventListener('click', function () {
            toggleSeat(seat);
        });

        seat.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                toggleSeat(seat);
            }
        });
    });

    update();
});
