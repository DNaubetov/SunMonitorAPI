import socket


def get_local_ip():
    try:
        # Создаем временное соединение с внешним хостом, например, Google DNS (8.8.8.8)
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))
        local_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return local_ip
    except socket.error:
        return None


