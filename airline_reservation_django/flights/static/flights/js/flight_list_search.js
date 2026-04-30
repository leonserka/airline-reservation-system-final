(function() {
    var params = new URLSearchParams(window.location.search);
    var dep = params.get('departure_city');
    var arr = params.get('arrival_city');
    var date = params.get('departure_date');
    if (dep || arr || date) {
        document.addEventListener('DOMContentLoaded', function() {
            var fromInput = document.getElementById('fromInput');
            var toInput = document.getElementById('toInput');
            var departDate = document.getElementById('departDate');
            if (fromInput && dep) fromInput.value = dep;
            if (toInput && arr) toInput.value = arr;
            if (departDate && date) departDate.value = date;
        });
    }
})();

document.querySelectorAll('.fl-route-pill').forEach(function(btn) {
    btn.addEventListener('click', function() {
        var from = this.dataset.from;
        var to = this.dataset.to;
        var fromInput = document.getElementById('fromInput');
        var toInput = document.getElementById('toInput');
        if (fromInput) { fromInput.value = from; fromInput.dataset.city = from; }
        if (toInput) { toInput.value = to; toInput.dataset.city = to; }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
