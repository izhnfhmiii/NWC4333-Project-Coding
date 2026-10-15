
import socketserver
import json
import threading

HOST = "127.0.0.1"
PORT = 5000

# Product inventory
inventory = {
    "laptop": 10,
    "phone": 20,
    "headphone": 30
}

# Prevent simultaneous orders from corrupting stock
inventory_lock = threading.Lock()


class OrderHandler(socketserver.StreamRequestHandler):

    def handle(self):
        try:
            # Receive one JSON request, ending with a newline
            line = self.rfile.readline(4097)

            if not line or len(line) > 4096 or not line.endswith(b"\n"):
                self.send_response({
                    "status": "error",
                    "message": "Invalid or oversized request"
                })
                return

            request = json.loads(line.decode("utf-8"))

            product = request.get("product")
            quantity = request.get("quantity")

            # Validate the order
            if (
                not isinstance(product, str)
                or product not in inventory
                or type(quantity) is not int
                or quantity <= 0
            ):
                self.send_response({
                    "status": "error",
                    "message": "Invalid product or quantity"
                })
                return

            # Check and update stock atomically
            with inventory_lock:
                available = inventory[product]

                if available < quantity:
                    response = {
                        "status": "failed",
                        "message": "Insufficient stock",
                        "available": available
                    }
                else:
                    inventory[product] -= quantity
                    response = {
                        "status": "success",
                        "message": "Order placed successfully",
                        "product": product,
                        "quantity": quantity,
                        "remaining_stock": inventory[product]
                    }

            self.send_response(response)

            print(
                f"Customer request: {product}, "
                f"quantity: {quantity}, "
                f"result: {response['status']}"
            )

        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_response({
                "status": "error",
                "message": "Invalid JSON request"
            })
        except (ConnectionError, OSError):
            print("Client connection was interrupted")

    def send_response(self, response):
        message = json.dumps(response) + "\n"
        self.wfile.write(message.encode("utf-8"))


class EcommerceServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with EcommerceServer((HOST, PORT), OrderHandler) as server:
        print(f"E-commerce server running at {HOST}:{PORT}")
        print("Available products:", inventory)
        print("Press Ctrl+C to stop the server.")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
