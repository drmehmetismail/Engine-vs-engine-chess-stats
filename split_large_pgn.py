def split_pgn_file(input_file_path, output_directory, max_file_size_mb):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    max_file_size = max_file_size_mb * 1024 * 1024  # Convert MB to Bytes
    file_counter = 1
    buffer = b""
    encoding = detect_encoding(input_file_path)

    with open(input_file_path, 'rb') as file:  # Open in binary mode
        while True:
            chunk = file.read(1024 * 1024)  # Read 1MB chunk at a time
            if not chunk and not buffer:  # End of file
                break

            buffer += chunk

            if len(buffer) >= max_file_size:
                split_index = find_last_complete_game(buffer)

                if split_index != -1:
                    # Write the complete games to a new file
                    with open(os.path.join(output_directory, f'games{file_counter}.pgn'), 'wb') as current_file:
                        current_file.write(buffer[:split_index + 1])
                    buffer = buffer[split_index + 1:]
                    # Remove leading whitespaces (including newline) from the new buffer
                    buffer = buffer.lstrip(b' \t\r\n')
                else:
                    # In case no complete game is found, increase buffer size
                    continue

                file_counter += 1

    # Write remaining buffer to file, if any
    if buffer:
        with open(os.path.join(output_directory, f'games{file_counter}.pgn'), 'wb') as current_file:
            current_file.write(buffer)

if __name__ == "__main__":
    input_file_path = ''
    output_directory = ''
    max_file_size_mb = 100
    split_pgn_file(input_file_path, output_directory, max_file_size_mb)
