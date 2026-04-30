from ..models import Flight


class BookingSession:

    def __init__(self, request):
        self.session = request.session

    def get_return_flight(self):
        rid = self.get_return_flight_id()
        return Flight.objects.filter(id=rid).first() if rid else None

    def get_num_passengers(self):
        return self.session.get("num_passengers", 1)

    def set_num_passengers(self, value):
        self.session["num_passengers"] = value

    def get_passengers(self):
        return self.session.get("passengers", [])

    def set_passengers(self, value):
        self.session["passengers"] = value

    def get_outbound_flight_id(self):
        return self.session.get("outbound_flight_id")

    def set_outbound_flight_id(self, value):
        self.session["outbound_flight_id"] = value

    def get_return_flight_id(self):
        return self.session.get("return_id")

    def set_return_flight_id(self, value):
        self.session["return_id"] = value

    def get_total_price(self):
        return float(self.session.get("total_price", 0.0))

    def set_total_price(self, value):
        self.session["total_price"] = float(value)

    def init_price(self, price):
        if "total_price" not in self.session:
            self.set_total_price(price)
        return self.get_total_price()

    def get_seat_class(self):
        return self.session.get("seat_class")

    def set_seat_class(self, value):
        self.session["seat_class"] = value

    def get_selected_seats(self):
        return self.session.get("selected_seats", {})

    def set_selected_seats(self, value):
        self.session["selected_seats"] = value

    def get_luggage(self):
        return self.session.get("selected_luggage")

    def set_luggage(self, value):
        self.session["selected_luggage"] = value

    def get_equipment(self):
        return self.session.get("selected_equipment")

    def set_equipment(self, value):
        self.session["selected_equipment"] = value

    def clear(self):
        keys = [
            "outbound_flight_id", "passengers", "num_passengers",
            "selected_seats", "seat_class", "total_price",
            "return_id", "selected_luggage", "selected_equipment",
        ]
        for key in keys:
            self.session.pop(key, None)
