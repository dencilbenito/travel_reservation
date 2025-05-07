import mysql.connector
from datetime import datetime

#Bus Information
buses = {
    1: {"route": "DEL to JAI", "fare": 600, "depart": "08:30", "arrive": "13:30"},
    2: {"route": "DEL to NAI", "fare": 700, "depart": "09:00", "arrive": "15:15"},
    3: {"route": "DEL to CHA", "fare": 500, "depart": "07:45", "arrive": "12:00"}
}

TOTAL_SEATS = 40

#Connect MYSql
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="travel_agency"
    )

#Check seat availability
def get_reserved_seats(cursor, bus_no, date):
    query = "SELECT seat_no FROM reservations WHERE bus_no=%s AND travel_date=%s"
    cursor.execute(query, (bus_no, date))
    return [row[0] for row in cursor.fetchall()]

#Make a reservation
def make_reservation():
    print("\nAvailable Buses:")
    for bno, info in buses.items():
        print(f"{bno}: {info['route']} – Fare: {info['fare']}")

    try:
        bus_no = int(input("Enter Bus Number (1/2/3): "))
        if bus_no not in buses:
            print("Invalid bus number.")
            return

        date_input = input("Enter date of journey (e.g. 2024-04-20): ").strip()
        travel_date = datetime.strptime(date_input, "%Y-%m-%d").date()

        conn = connect_db()
        cursor = conn.cursor()

        reserved = get_reserved_seats(cursor, bus_no, travel_date)
        available = [i for i in range(1, TOTAL_SEATS + 1) if i not in reserved]

        if not available:
            print("No seats available.")
            return

        n = int(input("How many passengers to book?: "))
        if n > len(available):
            print(f"Only {len(available)} seats are available.")
            return

        passengers = []
        for i in range(n):
            print(f"\nPassenger {i+1}")
            name = input("Name: ").strip()
            sex = input("Sex (M/F): ").strip().upper()
            if sex not in ("M", "F"):
                print("Invalid sex.")
                return
            age = int(input("Age: "))
            if not (0 < age <= 120):
                print("Invalid age.")
                return
            seat_no = available[i]
            passengers.append((bus_no, travel_date, seat_no, name, sex, age))

        for p in passengers:
            cursor.execute("""
                INSERT INTO reservations (bus_no, travel_date, seat_no, name, sex, age, depart_time, arrival_time, fare)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                p[0], p[1], p[2], p[3], p[4], p[5],
                buses[bus_no]["depart"],
                buses[bus_no]["arrive"],
                buses[bus_no]["fare"]
            ))

        conn.commit()
        print("\n--- Reservation Ticket ---")
        print(f"Bus No: {bus_no}\tDate: {travel_date}")
        print("SNo\tName\tSex\tAge\tDepart\tArrive\tFare")
        total = 0
        for p in passengers:
            print(f"{p[2]}\t{p[3]}\t{p[4]}\t{p[5]}\t{buses[bus_no]['depart']}\t{buses[bus_no]['arrive']}\t{buses[bus_no]['fare']}")
            total += buses[bus_no]['fare']
        print(f"Total Amount: {total:.2f}")

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

# === Display Reservation List ===
def show_reservation_list():
    try:
        bus_no = int(input("Enter Bus Number (1/2/3): "))
        if bus_no not in buses:
            print("Invalid bus number.")
            return

        date_input = input("Enter date (YYYY-MM-DD): ").strip()
        travel_date = datetime.strptime(date_input, "%Y-%m-%d").date()

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT seat_no, name, age, sex, fare FROM reservations
            WHERE bus_no=%s AND travel_date=%s ORDER BY seat_no
        """, (bus_no, travel_date))

        rows = cursor.fetchall()
        print(f"\n--- Reservation List for Bus {bus_no} on {travel_date} ---")
        print(f"Departure: {buses[bus_no]['depart']} Arrival: {buses[bus_no]['arrive']}")
        print("Seat\tName\tAge\tSex\tFare")
        total = 0
        for row in rows:
            print(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}")
            total += float(row[4])
        print(f"\nTotal Fare Collected: {total:.2f}")

    except Exception as e:
        print("Error:", e)
    finally:
        cursor.close()
        conn.close()

# === Main Menu ===
def main():
    while True:
        print("\n===== Travel Agency Reservation System =====")
        print("1. Make a Reservation")
        print("2. Show Reservation List")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            make_reservation()
        elif choice == '2':
            show_reservation_list()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
