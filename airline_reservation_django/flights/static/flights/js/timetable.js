document.getElementById('cityFilter').addEventListener('change', function () {
    var val = this.value;
    document.querySelectorAll('.tt-section').forEach(function (sec) {
        sec.style.display = (!val || sec.dataset.city === val) ? '' : 'none';
    });
});
