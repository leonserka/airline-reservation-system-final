document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("bookingChart");
    if (!canvas) return;

    const { labels, bookings, revenue } = window.chartData;

    new Chart(canvas, {
        data: {
            labels,
            datasets: [
                {
                    type: "bar",
                    label: "Bookings",
                    data: bookings,
                    backgroundColor: "rgba(0,51,102,0.18)",
                    borderColor: "#003366",
                    borderWidth: 1.5,
                    borderRadius: 4,
                    yAxisID: "y",
                },
                {
                    type: "line",
                    label: "Revenue (€)",
                    data: revenue,
                    borderColor: "#1a8754",
                    backgroundColor: "rgba(26,135,84,0.08)",
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.35,
                    fill: true,
                    yAxisID: "y2",
                }
            ]
        },
        options: {
            responsive: true,
            interaction: { mode: "index", intersect: false },
            plugins: { legend: { position: "top" } },
            scales: {
                y:  {
                    position: "left",
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                    title: { display: true, text: "Bookings" }
                },
                y2: {
                    position: "right",
                    beginAtZero: true,
                    grid: { drawOnChartArea: false },
                    title: { display: true, text: "Revenue (€)" }
                },
            }
        }
    });
});
