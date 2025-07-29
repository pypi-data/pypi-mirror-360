from balinese_nlp.textpreprocessor import TextPreprocessor
from balinese_nlp.postag.utils import load_pretrained_hmm_model

class HiddenMarkovModelPOSTag:
   def __init__(self):
      self.preprocessor = TextPreprocessor()
      self.pretrainedHMM = load_pretrained_hmm_model()
      self.TP = 1
      self.transitionProbDict = {}
      self.emissionProbDict = {}
      self.obsSeqList = []
      self.tagStateList = []
      self.tagStateDict = {}
      self.outgoingTagCountDict = {}
      self.noOfTag = 0
      self.AllWordsList = {}

   def predict(self,sentence):
      # retrieve transition and emission probability matrix
      self.__retrieve_transition_emmission()

      # run viterbi algoritm
      st = self.__viterbi(sentence)
      return st

   def __retrieve_transition_emmission(self):
      modelFile = self.pretrainedHMM
      iCount = 0
      for line in modelFile:
         if iCount == 0:
            iCount = iCount + 1
            self.noOfTag = int(line.split(':')[1])
            continue
         if iCount == 1:
            # tags
            iCount = iCount + 1
            tagSet = line.split(':')[1]
            tagSet = tagSet.strip('\n')
            self.tagStateList = tagSet.split(',')
            continue
         if line == 'Outgoing Count:\n':
            TP = 2
            continue
         if line == 'Transition Probability:\n':
            TP = 1
            continue
         if TP == 2:
            d = line.split(':')
            # print(d[0])
            self.outgoingTagCountDict[d[0]] = int(d[1].strip('\n'))
         if line == 'Emission Probability:\n':
            TP = 0
            continue
         if TP == 1:
            data = line.split(':')
            if len(data[0]) < 4:
                  continue
            tp = data[0]  
            tp = tp.replace('Begin', 'Q0')
            self.transitionProbDict[tp] = float(data[1].strip('\n'))
         if TP == 0:
            data = line.split(':->')
            tagE = data[0]
            tagE = tagE[2:len(tagE) - 1]
            corpusWord = tagE.split('|')[0]
            self.AllWordsList[corpusWord] = 1
            self.emissionProbDict[tagE] = float(data[1].strip('\n'))
      # read input file
      c = 0
      for tagNm in self.tagStateList:
         self.tagStateDict[c] = tagNm
         c += 1
   
   def __viterbi(self, sentence):
      # variables initizalition
      score = 0
      Seq = self.preprocessor.balinese_word_tokenize(sentence)
      T = len(Seq)
      h, w = self.noOfTag + 1, T
      viterbi = [[0 for x in range(w)] for y in range(h)]
      backtrack = [[0 for x in range(w)] for y in range(h)]

      # run viterbi algorithm
      for s in self.tagStateDict.keys():

        emiKey = Seq[0] + '|' + self.tagStateDict[s]
        if Seq[0] not in self.AllWordsList.keys():
            multPE = 1
        elif emiKey not in self.emissionProbDict.keys():
            multPE = 0
        else:
            multPE = self.emissionProbDict[emiKey]
        tranKey = 'Q0-'+self.tagStateDict[s]
        if tranKey not in self.transitionProbDict:
            multPT = 1 / (self.outgoingTagCountDict['Q0'] + self.noOfTag)
        else:
            multPT = self.transitionProbDict[tranKey]
        viterbi[s][0] = multPT * multPE
        backtrack[s][0] = 0

      for t in range(1, T):
        for s_to in self.tagStateDict.keys():
            for s_from in self.tagStateDict.keys():
                emiKey = Seq[t] + '|' + self.tagStateDict[s_to]
                if Seq[t] not in self.AllWordsList.keys():
                    multPE = 1
                elif emiKey not in self.emissionProbDict.keys():
                    multPE = 0
                else:
                    multPE = self.emissionProbDict[emiKey]
                tranKey = self.tagStateDict[s_from] + '-' + self.tagStateDict[s_to]
                if tranKey not in self.transitionProbDict:
                    multPT = 1 / \
                        (self.outgoingTagCountDict[self.tagStateDict[s_from]] + self.noOfTag)
                else:
                    multPT = self.transitionProbDict[tranKey]
                score = viterbi[s_from][t-1] * multPT * multPE
                if score > viterbi[s_to][t]:
                    viterbi[s_to][t] = score
                    backtrack[s_to][t] = s_from
                else:
                    continue
      best = 0
      for i in self.tagStateDict.keys():
         if viterbi[i][T-1] > viterbi[best][T-1]:
               best = i
      path = [Seq[T-1]+'/'+self.tagStateDict[best]]
      nice_path = [self.tagStateDict[best]]
      for t in range(T-1, 0, -1):
         best = backtrack[best][t]
         path[0:0] = [Seq[t-1]+'/'+self.tagStateDict[best]]
         nice_path[0:0] = [self.tagStateDict[best], '--%s-->' % (Seq[t - 1],)]
         nice_path_string = ' '.join(nice_path)             
      # clean resulted path
      st = '$'
      for i in path:
         st = st + i + ' '
      st = st.strip('$')
      st = st.strip(' ')
      st = st + '\n'
      return st