const COUNTRY_TIMEZONES = {
    'Albania': 'Europe/Tirane',
    'Austria': 'Europe/Vienna',
    'Belgium': 'Europe/Brussels',
    'Bosnia & Herzegovina': 'Europe/Sarajevo',
    'Croatia': 'Europe/Zagreb',
    'Czech Republic': 'Europe/Prague',
    'Denmark': 'Europe/Copenhagen',
    'Finland': 'Europe/Helsinki',
    'France': 'Europe/Paris',
    'Germany': 'Europe/Berlin',
    'Greece': 'Europe/Athens',
    'Italy': 'Europe/Rome',
    'Lithuania': 'Europe/Vilnius',
    'Montenegro': 'Europe/Podgorica',
    'Netherlands': 'Europe/Amsterdam',
    'Norway': 'Europe/Oslo',
    'Poland': 'Europe/Warsaw',
    'Portugal': 'Europe/Lisbon',
    'Romania': 'Europe/Bucharest',
    'Serbia': 'Europe/Belgrade',
    'Spain': 'Europe/Madrid',
    'Sweden': 'Europe/Stockholm',
    'Switzerland': 'Europe/Zurich',
    'Turkey': 'Europe/Istanbul',
    'United Kingdom': 'Europe/London',
};

const COUNTRY_CITIES = {
    'Albania':              ['Tirana', 'Durrës', 'Vlorë', 'Shkodër', 'Elbasan'],
    'Austria':              ['Vienna', 'Graz', 'Linz', 'Salzburg', 'Innsbruck'],
    'Belgium':              ['Brussels', 'Antwerp', 'Ghent', 'Liège', 'Bruges'],
    'Bosnia & Herzegovina': ['Sarajevo', 'Banja Luka', 'Mostar', 'Tuzla', 'Zenica'],
    'Croatia':              ['Zagreb', 'Split', 'Dubrovnik', 'Rijeka', 'Zadar'],
    'Czech Republic':       ['Prague', 'Brno', 'Ostrava', 'Plzeň', 'Liberec'],
    'Denmark':              ['Copenhagen', 'Aarhus', 'Odense', 'Aalborg', 'Esbjerg'],
    'Finland':              ['Helsinki', 'Tampere', 'Turku', 'Oulu', 'Jyväskylä'],
    'France':               ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
    'Germany':              ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'],
    'Greece':               ['Athens', 'Thessaloniki', 'Heraklion', 'Patras', 'Rhodes'],
    'Italy':                ['Rome', 'Milan', 'Naples', 'Turin', 'Florence'],
    'Lithuania':            ['Vilnius', 'Kaunas', 'Klaipėda', 'Šiauliai', 'Panevėžys'],
    'Montenegro':           ['Podgorica', 'Nikšić', 'Bar', 'Herceg Novi', 'Kotor'],
    'Netherlands':          ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'],
    'Norway':               ['Oslo', 'Bergen', 'Trondheim', 'Stavanger', 'Tromsø'],
    'Poland':               ['Warsaw', 'Kraków', 'Łódź', 'Wrocław', 'Poznań'],
    'Portugal':             ['Lisbon', 'Porto', 'Faro', 'Braga', 'Setúbal'],
    'Romania':              ['Bucharest', 'Cluj-Napoca', 'Timișoara', 'Iași', 'Constanța'],
    'Serbia':               ['Belgrade', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica'],
    'Spain':                ['Madrid', 'Barcelona', 'Seville', 'Valencia', 'Bilbao'],
    'Sweden':               ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala', 'Västerås'],
    'Switzerland':          ['Zurich', 'Geneva', 'Basel', 'Bern', 'Lausanne'],
    'Turkey':               ['Istanbul', 'Ankara', 'Izmir', 'Antalya', 'Bursa'],
    'United Kingdom':       ['London', 'Manchester', 'Birmingham', 'Edinburgh', 'Glasgow'],
};

function replaceWithSelect(inputId) {
    const input = document.getElementById(inputId);
    const select = document.createElement('select');
    select.id    = input.id;
    select.name  = input.name;
    select.className = input.className;
    select.innerHTML = '<option value="">-- Select city --</option>';
    input.replaceWith(select);
    return select;
}

function populateCities(country, citySelect) {
    const cities = COUNTRY_CITIES[country] || [];
    citySelect.innerHTML = '<option value="">-- Select city --</option>';
    cities.forEach(city => {
        const opt = document.createElement('option');
        opt.value = city;
        opt.textContent = city;
        citySelect.appendChild(opt);
    });
}

const depCitySelect = replaceWithSelect('id_departure_city');
const arrCitySelect = replaceWithSelect('id_arrival_city');

document.getElementById('id_departure_country').addEventListener('change', function () {
    const tz = COUNTRY_TIMEZONES[this.value];
    if (tz) document.getElementById('id_departure_timezone').value = tz;
    populateCities(this.value, depCitySelect);
});

document.getElementById('id_arrival_country').addEventListener('change', function () {
    const tz = COUNTRY_TIMEZONES[this.value];
    if (tz) document.getElementById('id_arrival_timezone').value = tz;
    populateCities(this.value, arrCitySelect);
});

const flightNumInput = document.getElementById('id_flight_number');
if (!flightNumInput.value) {
    flightNumInput.value = 'AR' + Math.floor(100 + Math.random() * 900);
}
