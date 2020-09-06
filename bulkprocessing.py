def process_message_history(file='data.txt'):
    with open(file, 'r') as myfile:
        data=myfile.read()

    messages = []

    was_newline = True
    is_in_message = False
    is_in_time = False
    tmp_time = ''
    tmp_msg = ''
    for c in data:
        if was_newline and c == '[':
            is_in_time = True
            is_in_message = False
            was_newline = False
            messages.append((tmp_time,tmp_msg.split(':')[0].strip().replace('\n',''),':'.join(tmp_msg.split(':')[1:]).strip()))
            tmp_time = ''
            tmp_msg = ''
        elif is_in_time and c == ']':
            is_in_time = False
            is_in_message = True
        elif is_in_time:
            tmp_time += c
        elif is_in_message:
            tmp_msg += c
            if c == '\n':
                was_newline = True
        if was_newline and c != '\n':
            was_newline = False
            is_in_message = True

    return messages[1:]
