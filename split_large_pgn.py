def split_pgn_file(input_file_path, output_directory, max_file_size_mb):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    max_file_size = max_file_size_mb * 1024 * 1024
    file_counter = 1
    buffer = b""
    encoding = detect_encoding(input_file_path)

    with open(input_file_path, 'rb') as file:
        while True:
            chunk = file.read(1024 * 1024)
            buffer += chunk

            while len(buffer) >= max_file_size:
                split_index = find_last_complete_game(buffer)

                if split_index != -1:
                    with open(os.path.join(output_directory, f'games{file_counter}.pgn'), 'wb') as current_file:
                        current_file.write(buffer[:split_index + 1])
                    buffer = buffer[split_index + 1:].lstrip(b' \t\r\n')
                    file_counter += 1
                else:
                    break  # No valid split point found, wait for more data

            if not chunk:  # End of file
                if buffer:  # Write remaining buffer to a new file
                    with open(os.path.join(output_directory, f'games{file_counter}.pgn'), 'wb') as current_file:
                        current_file.write(buffer)
                break

if __name__ == "__main__":
    input_file_path = ''
    output_directory = ''
    max_file_size_mb = 100
    split_pgn_file(input_file_path, output_directory, max_file_size_mb)
