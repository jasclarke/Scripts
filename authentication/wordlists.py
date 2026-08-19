
import sys

WORDLIST = 'authentication/wordlists/passwords_repeat.txt'
WORD = 'peter'
AFTER_EVERY = 3
REPEAT_WORD = 'carlos'
PLACED_WORD = 'wiener'
WORD_COUNT = 150

def create_wordlist(repeat_word, placed_word, word_count, wordlist, insert_every=0):
    words = list()
    words.append(placed_word + '\n')

    for index in range(1, word_count):
        if index % insert_every == 0:
            words.append(placed_word + '\n')
        else:
            words.append(repeat_word + '\n')
        
    try:
        with open(wordlist, 'w') as wl:
            words = wl.writelines(words)

        print(f'The new list was successfully saved to {wordlist} file.')
    except Exception as e:
            sys.exit(f'An error occurred: {e}')

def modify_wordlist(wordlist, word, insert_every=0):
    words = list()
    word += '\n'

    try:
        with open(wordlist, 'r') as wl:
            words = wl.readlines()

        count = 0
        required_words = len(words) + (len(words) // (insert_every - 1))
        print(required_words)

        for index in range(0, required_words, insert_every):
            words.insert(index, word)
            count += 1

        print(f'The word was inserted {count} times at every {insert_every} occurance.')
        print(f'There is now a total of {len(words)} words.')
    except FileNotFoundError:
        sys.exit('The file was not found')
    except Exception as e:
        sys.exit(f'An error occurred: {e}')

    try:
        with open(wordlist, 'w') as wl:
            words = wl.writelines(words)

        print(f'The new list was successfully saved to {wordlist} file.')
    except Exception as e:
            sys.exit(f'An error occurred: {e}')
            

if __name__ == '__main__':
    #create_wordlist(REPEAT_WORD, PLACED_WORD, WORD_COUNT, WORDLIST, AFTER_EVERY)
    modify_wordlist(WORDLIST, WORD, AFTER_EVERY)