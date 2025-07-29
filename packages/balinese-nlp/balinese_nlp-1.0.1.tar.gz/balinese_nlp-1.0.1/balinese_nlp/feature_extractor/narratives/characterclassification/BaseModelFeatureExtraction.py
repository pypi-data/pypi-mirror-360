from numpy import array


class BaseModelFeatureExtraction:
    def __init__(self, *args, **kwargs):
        # DEFINE CONSTANT
        self.NUMBER_OF_ALL_FEATURES = kwargs['number_of_all_features']
        self.CODE_FEATURE = kwargs['code_feature']
        self._IS_TRANSFORM_METHOD = False
        self._IS_FIT_METHOD = False

        # get list of initial variables from init method in child class (kwargs)
        self.list_of_feature = self._validate_list_of_input_feature(
            kwargs['list_of_feature'])

        # results variables from processing
        self.extracted_features = None
        self.extracted_features_array = None
        self.docstring_feature_definition = None

    def _initialize_extracted_features(self):
        self.extracted_features = dict()
        for feature in self.list_of_feature:
            self.extracted_features[feature] = list()
        return self.extracted_features

    def _validate_list_of_input_feature(self, list_of_feature):
        if list_of_feature == "__all__":
            return [self.CODE_FEATURE+str(i+1) for i in range(self.NUMBER_OF_ALL_FEATURES)]
        elif list_of_feature is None or list_of_feature is list:
            raise TypeError(
                "List of features must be list of string feature code and can not be None!")
        else:
            return list_of_feature

    def get_features_names_out(self):
        return self.list_of_feature

    def get_features_definition(self):
        if self.docstring_feature_definition is None:
            # Access the docstring for the return value
            docstring = self.__doc__
            # Split the docstring into lines
            docstring_lines = docstring.split('\n')
            # Extract the return value section (it starts with "<Features Definition>")
            return_value_section = []
            found_return_section = False

            for line in docstring_lines:
                if found_return_section:
                    # Add lines from the return value section
                    return_value_section.append(line)
                elif line.strip().startswith("<Features Definition>"):
                    found_return_section = True

            # Join the lines of the return value section and print it
            return_value_docstring = '\n'.join(return_value_section)
            self.docstring_feature_definition = return_value_docstring
        return self.docstring_feature_definition

    def tonumpy(self):
        if not self._IS_TRANSFORM_METHOD:
            raise Exception('Please transform your fitted data first!')

        # convert dictionary results from transform method into numpy array
        if type(self.extracted_features) is dict:
            self.extracted_features_array = array(
                list(self.extracted_features.values())).transpose()
        return self.extracted_features_array
