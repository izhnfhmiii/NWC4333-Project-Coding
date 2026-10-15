
import socket
import json

HOST = "127.0.0.1"
PORT = 5000


def place_order(product, quantity):
    request = {
        "product": product,
        "quantity": quantity
    }

    try:
        with socket.create_connection(
            (HOST, PORT), timeout=5
        ) as client:

            # Send the order using JSON
            message = json.dumps(request) + "\n"
            client.sendall(message.encode("utf-8"))

            # Receive the server response
            with client.makefile("r", encoding="utf-8") as reader:
                response = reader.readline()

                if not response:
                    print("Server closed the connection.")
                    return

                result = json.loads(response)
                print("Server response:")
                print(json.dumps(result, indent=4))

    except (OSError, json.JSONDecodeError) as error:
        print("Unable to process order:", error)


if __name__ == "__main__":
    print("ONLINE E-COMMERCE ORDER SYSTEM")
    print("Products: laptop, phone, headphone")

    product = input("Enter product name: ").strip().lower()

    try:
        quantity = int(input("Enter quantity: "))
        place_order(product, quantity)
    except ValueError:
        print("Quantity must be a whole number.")
