from tasks import emit_words
import random
words = 'the rain in spain falls mainly on the plain'.split(' ')
emit_words(document=' '.join(random.choice(words) for i in range(50)))
