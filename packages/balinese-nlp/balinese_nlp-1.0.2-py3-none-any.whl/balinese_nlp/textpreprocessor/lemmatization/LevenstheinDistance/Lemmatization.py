from .LemmatizationRules import LemmatizationRules
import re


class Lemmatization:

    def __init__(self, vocabs):
        self.LemmatizationRules = LemmatizationRules(vocabs)
        self.rules = self.LemmatizationRules.regex_rules()

    def stemming(self, input_word):
        # cek dulu di db
        listStem = []
        listStem.append(input_word)
        if (self.LemmatizationRules.checkVocab(input_word)):
            returnWord = input_word
            matchRule = False
            message = False
            listStem = False
        else:
            for z in self.rules:
                for i in z:
                    returnWord = False
                    matchRule = False
                    message = False
                    wrap = False
                    if (self.LemmatizationRules.checkRegex(i['rule'], input_word)):
                        matchRule = i['rule']
                        tempWord = input_word
                        # print(matchRule)
                        if (i['type'] == 'wrap'):
                            wrap = True

                        for j in i['action']:
                            if (isinstance(j['to'], list)):
                                for x in j['to']:
                                    tempWord2 = (
                                        re.sub(j['from'], x, tempWord))
                                    listStem.append(tempWord2)
                                    # print(tempWord2)
                                    # Jika wrap lakukan ini
                                    if (wrap):
                                        tempWord = tempWord2

                                    if (self.LemmatizationRules.checkVocab(tempWord2)):
                                        returnWord = tempWord2
                                        message = False
                                        break
                                    else:
                                        message = 'not found on vocab'
                            else:
                                tempWord2 = re.sub(
                                    j['from'], j['to'], tempWord)
                                listStem.append(tempWord2)
                                # print(tempWord2)
                                tempWord = tempWord2
                                if (self.LemmatizationRules.checkVocab(tempWord2)):
                                    returnWord = tempWord2
                    if returnWord is not False:
                        break
                if returnWord is not False:
                    break
        r = {'word': input_word, 'matchRule': matchRule, 'stemWord': returnWord,
             'message': message, 'listStem': listStem}
        return r

    def lavenshteinDistance(self, recommendationWord, word):
        s1 = recommendationWord
        s2 = word

        if len(s1) > len(s2):
            s1, s2 = s2, s1
        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2+1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(
                        1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    def lemmatization(self, input_word):
        hasil = self.stemming(input_word.lower())
        output = hasil['stemWord']

        if (output == False):
            longest = len(input_word)
            recommend = input_word

            for recWord in hasil['listStem']:
                for word in self.LemmatizationRules.vocabs:
                    distance = self.lavenshteinDistance(recWord, word)
                    if (distance < longest):
                        longest = distance
                        recommend = word
            output = recommend
        return output

    def lemmatizationNoLavenshteinDistance(self, input_word):
        hasil = self.stemming(input_word.lower())
        output = hasil['stemWord']
        if (output == False):
            longest = len(input_word)
            output = input_word
        return output

    def lemmatizationDetail(self, input_word):
        hasil = self.stemming(input_word.lower())
        output = hasil['stemWord']

        if (output == False):
            longest = len(input_word)
            recommend = input_word

            for recWord in hasil['listStem']:
                for word in self.LemmatizationRules.vocabs:
                    distance = self.lavenshteinDistance(recWord, word)
                    if (distance < longest):
                        longest = distance
                        recommend = word
            output = recommend
