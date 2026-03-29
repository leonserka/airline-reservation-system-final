window.isLogged = true;

function handleFlightSelection(e) {
    e.preventDefault();
    const dep = document.querySelector('input[name="departure_flight"]:checked');
    const ret = document.querySelector('input[name="return_flight"]:checked');
    const pax = document.getElementById("num_passengers").value || 1;
    const tripType = sessionStorage.getItem("trip_type") || "oneway";

    if (!dep) { alert("Please select a departure flight."); return false; }
    if (tripType === "round" && !ret) { alert("Please select a return flight."); return false; }

    let url = `/book/${dep.value}/step1/?pax=${pax}`;
    if (tripType === "round" && ret) url += `&return_id=${ret.value}`;
    window.location.href = url;
    return false;
}
