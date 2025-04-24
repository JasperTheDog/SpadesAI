def get_valid_input(prompt, valid_inputs):
    while True:
        user_input = input(prompt)
        if user_input in valid_inputs:
            return user_input
        else:
            print("Not a valid input. Please try again.")
    
def get_valid_int_input(prompt, min_val, max_val):
    valid_inputs = {str(i) for i in range(min_val, max_val + 1)}
    return int(get_valid_input(prompt, valid_inputs))

def card_to_rank(card):
    rank_str = card[:-1]
    if rank_str == 'J':
        return 11
    elif rank_str == 'Q':
        return 12
    elif rank_str == 'K':
        return 13
    elif rank_str == 'A':
        return 14
    else:
        return int(rank_str)

def card_to_suit(card):
    return card[-1]