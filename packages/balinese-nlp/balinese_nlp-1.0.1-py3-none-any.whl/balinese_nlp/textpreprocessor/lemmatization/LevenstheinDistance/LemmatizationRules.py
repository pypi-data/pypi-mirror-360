import re


class LemmatizationRules:
    def __init__(self, vocabs):
        self.vocabs = vocabs

    # def loadBalineseVocabs(self):
    #     balinese_vocab_path = os.path.join(os.path.dirname(__file__), "..",
    #                                        "TextFiles\\Vocabulary\\BaliVocab.txt")
    #     vocabs = []
    #     with open(balinese_vocab_path) as f:
    #         vocabs = f.read().splitlines()
    #     return vocabs

    def checkVocab(self, word_input):
        if (word_input in self.vocabs):
            return True
        else:
            return False

    def checkRegex(self, regex_rules, word_input):
        result = re.match(regex_rules, word_input)
        if result:
            return True
        else:
            return False

    def regex_rules(self):
        # Define lemmatization rules
        rules = []
        # Append kombinasi affix
        rules.append([
            {'rule': '^n[a-z]*in$',
             'type': 'wrap',
             'action': [
                 {'from': '^n', 'to': ['t']},
                 {'from': 'in$', 'to': ''},
             ]
             },
            # sendiri
            {'rule': '^ny[a-z]*in$',
             'type': 'wrap',
             'action': [
                 {'from': '^ny', 'to': ['c', 'j', 's']},
                 {'from': 'in$', 'to': ''},
             ]
             },
            # sendiri end
            {'rule': '^man[a-z]*in$',
             'type': 'wrap',
             'action': [
                 {'from': '^man', 'to': ['t', 'd']},
                 {'from': 'in$', 'to': ''},
             ]
             },
            {'rule': '^ma[a-z]*an$',
             'type': 'wrap',
             'action': [
                 {'from': '^ma', 'to': ''},
                 {'from': 'an$', 'to': ''},
             ]
             },
            {'rule': '^mang[a-z]*ang$',
             'type': 'wrap',
             'action': [
                 {'from': '^mang', 'to': ''},
                 {'from': 'ang$', 'to': ''},
             ]
             },

            #     Tamvbah sendiri
            {'rule': '^ng[a-z]*in$',
             'type': 'wrap',
             'action': [

                 {'from': '^ng', 'to': ['', 'k', 'g']},
                 {'from': 'in$', 'to': ''}
             ],
             },
        ])
        # Append Somulfiks
        rules.append([
            {'rule': '^mam[a-z]*',
             'type': 'non-wrap',
             'action': [
                 {'from': '^mam', 'to': ['b', 'p']}
             ],
             },
            {'rule': '^pang[a-z]*',
             'type': 'non-wrap',
             'action': [
                 {'from': '^pang', 'to': ['k', 'g']}
             ],
             },
        ])
        # Append Konfiks
        rules.append([
            # Tambah sendiri
            {'rule': '^ka[a-z]*ang$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ka', 'to': ''},
                 {'from': 'ang$', 'to': ''}
             ],
             },
            {'rule': '^ny[a-z]*[aiueo]yang$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ny', 'to': ['c', 'j', 's']},
                 {'from': 'yang$', 'to': ''}
             ],
             },

            {'rule': '^ka[a-z]*e$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ka', 'to': ''},
                 {'from': 'e$', 'to': ''}
             ],
             },

            {'rule': '^ng[aiueo]*[a-z]*in$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ng', 'to': ['', 'k', 'g']},
                 {'from': 'in$', 'to': ''}
             ],
             },


            {'rule': '^peng[aiueo][a-z]*ne$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^peng', 'to': ''},
                 {'from': 'ne$', 'to': ''}
             ],
             },
            # end tambah sendiri
            {'rule': '^pa[a-z]*an$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^pa', 'to': ''},
                 {'from': 'an$', 'to': ''}
             ],
             },
            {'rule': '^ny[aiueo][a-z]*[^aiueo]in$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ny', 'to': ['c', 'j', 's']},
                 {'from': 'in$', 'to': ''}
             ],
             },


            {'rule': '^ka[a-z]*an$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ka', 'to': ''},
                 {'from': 'an$', 'to': ''}
             ],
             },
            {'rule': '^ma[a-z]*an$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ma', 'to': ''},
                 {'from': 'an$', 'to': ''}
             ],
             },
            {'rule': '^bra[a-z]*an$',
             'type': 'non-wrap',
             'action': [

                 {'from': '^bra', 'to': 'a'},
                 {'from': 'an$', 'to': ''}
             ],
             },
        ])
        # Append Prefiks
        rules.append([
            # Prefix
            {'rule': '^ng[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ng', 'to': ['k', 'g']}
             ],
             },

            {'rule': '^ng[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ng', 'to': ''}
             ],
             },

            {'rule': '^ng[w]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ng', 'to': ''}
             ],
             },

            {'rule': '^n[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^n', 'to': ['t', 'd']}
             ],
             },

            {'rule': '^ny[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ny', 'to': ['c', 'j', 's']}
             ],
             },


            {'rule': '^m[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^m', 'to': ['b', 'p']}
             ],
             },

            {'rule': '^nga[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^nga', 'to': ''}
             ],
             },
            # ma
            {'rule': '^ma[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ma', 'to': ''}
             ],
             },
            {'rule': '^ma[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ma', 'to': ''}
             ],
             },
            {'rule': '^me[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^me', 'to': ''}
             ],
             },
            {'rule': '^me[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^me', 'to': ''}
             ],
             },
            {'rule': '^ma[wy]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^ma', 'to': ''}
             ],
             },
            # {'rule': '^m[aiueo]',
            #  'type':'non-wrap',
            #  'action': [
            #
            #      {'from': '^m', 'to': ''}
            #  ],
            #  },
            # pa
            {'rule': '^p[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^p', 'to': ''}
             ],
             },
            # ka
            {'rule': '^k[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^k', 'to': ''}
             ],
             },
            #
            {'rule': '^sa[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^sa', 'to': ''}
             ],
             },
            {'rule': '^sa[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^sa', 'to': ''}
             ],
             },
            # a
            {'rule': '^a[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^a', 'to': ''}
             ],
             },
            {'rule': '^a[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^a', 'to': ''}
             ],
             },
            # pra
            {'rule': '^pra[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^pra', 'to': ''}
             ],
             },
            # pari
            {'rule': '^pari[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^pari', 'to': ''}
             ],
             },
            {'rule': '^pari[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^pari', 'to': ''}
             ],
             },
            # pati
            {'rule': '^pati[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^pati', 'to': ''}
             ],
             },
            # maka
            {'rule': '^maka[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^maka', 'to': ''}
             ],
             },
            {'rule': '^maka[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^maka', 'to': ''}
             ],
             },
            {'rule': '^saka[aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^saka', 'to': ''}
             ],
             },
            {'rule': '^saka[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^saka', 'to': ''}
             ],
             },
            {'rule': '^kuma[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^kuma', 'to': ''}
             ],
             },
            # tambah sendiri
            {'rule': '^n[^aiueo]',
             'type': 'non-wrap',
             'action': [

                 {'from': '^n', 'to': ''}
             ],
             },
            # end tambah sendiri
        ])
        # Append Sufix
        rules.append([
            # Suffix
            {'rule': '[a-z]*a$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'a$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]na$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'na$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[^aiueo]ang$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'ang$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo][ny]ang$',
             'type': 'non-wrap',
             'action': [

                 {'from': '[ny]ang$', 'to': ''}
             ],
             },

            {'rule': '[a-z]*[^aiueo]an$',
             'type': 'non-wrap',
             'action': [
                 {'from': 'an$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]nan$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'nan$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[^aiueo]in$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'in$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]nin$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'nin$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[^aiueo]e$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'e$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]ne$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'ne$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[^aiueo]ne$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'ne$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]nne$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'nne$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]n$',
             'type': 'non-wrap',
             'action': [

                 {'from': 'n$', 'to': ''}
             ],
             },
            {'rule': '[a-z]*[aiueo]ning$',
             'type': 'non-wrap',
             'action': [
                 {'from': 'ning$', 'to': ''}
             ],
             },
        ])
        # Append Infiks
        rules.append([

            #
            {'rule': '[^aiueo]*in[aiueo][a-z]*an$',
             'type': 'wrap',
             'action': [

                 {'from': 'in', 'to': ''},
                 {'from': 'an', 'to': ''}
             ],
             },
            # Inffix
            {'rule': '[^aiueo]*in[aiueo][a-z]*',
             'type': 'non-wrap',
             'action': [

                 {'from': 'in', 'to': ''}
             ],
             },
            {'rule': '^in[aiueo][a-z]*',
             'type': 'non-wrap',
             'action': [

                 {'from': '^in', 'to': ''}
             ],
             },
            {'rule': '[^aiueo]*um[aiueo][a-z]*',
             'type': 'non-wrap',
             'action': [

                 {'from': 'um', 'to': ''}
             ],
             },
            {'rule': '^um[aiueo][a-z]*',
             'type': 'non-wrap',
             'action': [

                 {'from': '^um', 'to': ''}
             ],
             },
            {'rule': '[^aiueo]*el[aiueo][a-z]*',
             'type': 'non-wrap',
             'action': [

                 {'from': 'el', 'to': ''}
             ],
             },
            {'rule': '[^aiueo]*er[aiueo][a-z]*',
             'type': 'non-wrap',
             'action': [

                 {'from': 'er', 'to': ''}
             ],
             },
        ])
        return rules
