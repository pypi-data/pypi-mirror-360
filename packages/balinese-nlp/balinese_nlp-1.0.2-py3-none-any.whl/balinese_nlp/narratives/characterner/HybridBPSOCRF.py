import numpy as np
import time
from .ConditionalRandomFields import ConditionalRandomFields
import random as rd
import datetime
import copy
import os
ROOT_PATH_FOLDER = os.path.dirname(os.getcwd())


class HybridBPSOCRF:

    def __init__(self,
                 bit_encoding={
                     'w[i]': True,
                     'w[i].lower()': True,
                     'surr:w[i]': True,
                     'surr:w[i].lower()': True,
                     'pref:w[i]': True,
                     'suff:w[i]': True,
                     'surrPreff:w[i]': True,
                     'surrSuff:w[i]': True,
                     'w[i].isLessThres': True,
                     'w[i].isdigit()': True,
                     'surr:w[i].isdigit()': True,
                     'w[i].isupper()': True,
                     'surr:w[i].isupper()': True,
                     'w[i].istitle()': True,
                     'surr:w[i].istitle()': True,
                     'w[i].isStartWord()': True,
                     'w[i].isEndWord()': True,
                     'pos:w[i]': True,
                     'surrPos:w[i]': True,
                 },
                 pso_hyperparameters={
                     'particle': 30,
                     'max_iteration': 100,
                     'phi1': 0.3,
                     'phi2': 0.65,
                     'inertia': 0.8,
                     'fitness_objective': 'f1_score',
                     'maximum_convergence_threshold': 8,
                 },
                 crf_hyperparameters={
                     'algorithm': 'lbfgs',
                     'c1': 0.3034,
                     'c2': 0.0614,
                     'max_iteration': 100,
                     'average_metric': 'weighted'
                 },
                 verbose=True,
                 path_logs_file=ROOT_PATH_FOLDER+"\\temp\\logs_bpso\\",
                 filename=None,
                 ):
        self.VERBOSE = verbose
        # initialize PSO Hyperparameter
        self.PARTICLE_SIZE = int(pso_hyperparameters['particle'])
        self.MAX_ITERATION = int(pso_hyperparameters['max_iteration'])
        self.PHI1 = float(pso_hyperparameters['phi1'])
        self.PHI2 = float(pso_hyperparameters['phi2'])
        self.INERTIA = float(pso_hyperparameters['inertia'])
        self.FITNESS_OBJECTIVE = pso_hyperparameters['fitness_objective']
        self.MAXIMUM_CONVERGENCE_THRESHOLD = int(
            pso_hyperparameters['maximum_convergence_threshold'])
        self.LOWER_BOUND = 0
        self.UPPER_BOUND = 1
        self.V_MIN = self.LOWER_BOUND
        self.V_MAX = self.UPPER_BOUND
        self.BIT_ENCODING = bit_encoding
        # number of optimized features
        self.NUM_PARTICLE_ELEMENT = len(bit_encoding)
        self.NUM_RANDOM_CHAOSTIC_BOUNDARIES = 5

        # initialize CRF Hyperparameter
        self.CRF_CONFIG = {
            'algorithm': crf_hyperparameters['algorithm'],
            'c1': float(crf_hyperparameters['c1']),
            'c2': float(crf_hyperparameters['c2']),
            'max_iteration': int(crf_hyperparameters['max_iteration']),
            'average_metric': crf_hyperparameters['average_metric']
        }

        # initialize Logging Processed Variables
        self.__initialize_logs_variables(
            ITERATIONS=True,
            BEST_ACCURACY_VALIDATION=True,
            BEST_RECALL_VALIDATION=True,
            BEST_PRECISION_VALIDATION=True,
            BEST_F1_SCORE_VALIDATION=True,
            BEST_FITNESS_VALIDATION=True,
            BEST_FEATURES_VALIDATION=True,
            WORST_ACCURACY_VALIDATION=True,
            WORST_RECALL_VALIDATION=True,
            WORST_PRECISION_VALIDATION=True,
            WORST_F1_SCORE_VALIDATION=True,
            WORST_FITNESS_VALIDATION=True,
            BEST_ACCURACY_TRAINING=True,
            BEST_RECALL_TRAINING=True,
            BEST_PRECISION_TRAINING=True,
            BEST_F1_SCORE_TRAINING=True,
            BEST_FITNESS_TRAINING=True,
            BEST_FEATURES_TRAINING=True,
            WORST_ACCURACY_TRAINING=True,
            WORST_RECALL_TRAINING=True,
            WORST_PRECISION_TRAINING=True,
            WORST_F1_SCORE_TRAINING=True,
            WORST_FITNESS_TRAINING=True,
            TIME_OPTIMIZATION_TRACKING=True,
            PARTICLES_TRACKING=True,
            CONVERGENCE_VALUES=True,
        )
        self.FILENAME = filename
        if filename is None:
            self.FILENAME = "logs_bpso_" + \
                str(datetime.datetime.now().date()) + '.txt'
        self.PATH_LOGS_FILE = path_logs_file + self.FILENAME
        try:
            os.makedirs(path_logs_file, exist_ok=True)
            print("Directory '%s' created successfully" % path_logs_file)
        except OSError as error:
            print("Directory '%s' can not be created")

    def fit(self, df_fold_train, df_fold_validation):
        self.DATA_TRAIN = df_fold_train
        self.DATA_VALIDATION = df_fold_validation
        return self

    def run(self):
        # 1. Initialize Particle
        particles, velocities, pBestTrain, gBestTrain, pBestValidation, gBestValidation = self.__initialize_particles()

        # 2. Optimization
        constant_results = 0
        for iteration in range(self.MAX_ITERATION):
            prevBestPosition = gBestValidation['gBestPosition'].copy()
            st_time = time.time()

            # 3. Update the velocities vector
            velocities = self.__update_velocities(
                particles, velocities, pBestValidation, gBestValidation)

            # 4. update swarm position
            particles = particles + velocities

            # 5. apply boundaries to swarm positions using sigmoid function
            particles, velocities = self.__apply_boundaries(
                particles, velocities)

            # 6. evaluate fitness function
            fitnessParticlesTrainSet = {
                'accuracy': list(),
                'recall': list(),
                'precision': list(),
                'f1_score': list()
            }
            fitnessParticlesValidationSet = {
                'accuracy': list(),
                'recall': list(),
                'precision': list(),
                'f1_score': list()
            }
            for particle in particles:
                fitnessResults = self.__fitness_function(particle)
                fitnessParticlesTrainSet['accuracy'].append(
                    fitnessResults['train']['accuracy']
                )
                fitnessParticlesTrainSet['recall'].append(
                    fitnessResults['train']['recall']
                )
                fitnessParticlesTrainSet['precision'].append(
                    fitnessResults['train']['precision']
                )
                fitnessParticlesTrainSet['f1_score'].append(
                    fitnessResults['train']['f1_score']
                )
                fitnessParticlesValidationSet['accuracy'].append(
                    fitnessResults['validation']['accuracy']
                )
                fitnessParticlesValidationSet['recall'].append(
                    fitnessResults['validation']['recall']
                )
                fitnessParticlesValidationSet['precision'].append(
                    fitnessResults['validation']['precision']
                )
                fitnessParticlesValidationSet['f1_score'].append(
                    fitnessResults['validation']['f1_score']
                )

            # 7. update pBest
            pBestTrain = self.__update_pBest(
                pBestTrain, particles, fitnessParticlesTrainSet)
            pBestValidation = self.__update_pBest(
                pBestValidation, particles, fitnessParticlesValidationSet)

            # 8. update gBest
            gBestTrain = self.__update_gBest(gBestTrain, pBestTrain)
            gBestValidation = self.__update_gBest(
                gBestValidation, pBestValidation)

            et = time.time() - st_time

            # append process to logging variables
            self.__append_logs_variables(
                ITERATIONS=iteration+1,
                BEST_ACCURACY_VALIDATION=gBestValidation['gBestAccuracy'],
                BEST_RECALL_VALIDATION=gBestValidation['gBestRecall'],
                BEST_PRECISION_VALIDATION=gBestValidation['gBestPrecision'],
                BEST_F1_SCORE_VALIDATION=gBestValidation['gBestF1Score'],
                BEST_FITNESS_VALIDATION=gBestValidation['gBestFitness'],
                BEST_FEATURES_VALIDATION=gBestValidation['gBestPosition'],
                WORST_ACCURACY_VALIDATION=min(
                    pBestValidation['pBestAccuracy']),
                WORST_RECALL_VALIDATION=min(pBestValidation['pBestRecall']),
                WORST_PRECISION_VALIDATION=min(
                    pBestValidation['pBestPrecision']),
                WORST_F1_SCORE_VALIDATION=min(pBestValidation['pBestF1Score']),
                WORST_FITNESS_VALIDATION=min(pBestValidation['pBestFitness']),
                BEST_ACCURACY_TRAINING=gBestTrain['gBestAccuracy'],
                BEST_RECALL_TRAINING=gBestTrain['gBestRecall'],
                BEST_PRECISION_TRAINING=gBestTrain['gBestPrecision'],
                BEST_F1_SCORE_TRAINING=gBestTrain['gBestF1Score'],
                BEST_FITNESS_TRAINING=gBestTrain['gBestFitness'],
                BEST_FEATURES_TRAINING=gBestTrain['gBestPosition'],
                WORST_ACCURACY_TRAINING=min(
                    pBestTrain['pBestAccuracy']),
                WORST_RECALL_TRAINING=min(pBestTrain['pBestRecall']),
                WORST_PRECISION_TRAINING=min(
                    pBestTrain['pBestPrecision']),
                WORST_F1_SCORE_TRAINING=min(pBestTrain['pBestF1Score']),
                WORST_FITNESS_TRAINING=min(pBestTrain['pBestFitness']),
                TIME_OPTIMIZATION_TRACKING=et,
                PARTICLES_TRACKING=particles,
                CONVERGENCE_VALUES=constant_results,
            )

            # check convergence solutions
            nextBestPosition = gBestValidation['gBestPosition'].copy()
            if np.array_equal(prevBestPosition, nextBestPosition):
                constant_results += 1
            else:
                constant_results = 0
            if constant_results == self.MAXIMUM_CONVERGENCE_THRESHOLD:
                self.__print_to_prompt(messages=[
                    f'Optimization process did not achieve any improvement again after {self.MAXIMUM_CONVERGENCE_THRESHOLD} different iteration!',
                    'Optimization is stopped...'
                ])
                # save to logs
                self.__save_logs_file(additional_messages=[
                    '='*50+"\n",
                    f'Optimization process did not achieve any improvement again after {self.MAXIMUM_CONVERGENCE_THRESHOLD} different iteration!\n',
                    'Optimization is stopped...\n'
                ])
                break
            if self.VERBOSE:
                self.__print_to_prompt(messages=[
                    f"ITERATION : {iteration+1}",
                    f"CONVERGENCE : {constant_results}",
                    f"TIME : {et} seconds",
                    f"F1-score validation =  {gBestValidation['gBestFitness']}",
                    f"BEST FEATURES SET = {gBestValidation['gBestPosition']}",
                    f"PARTICLES = {particles}\n",
                ])

        # 3. Find the optimal results
        self.OPTIMIZATION_RESULTS = {
            'train': {
                'bestIndexParticle': np.argmax(pBestTrain['pBestFitness']),
                'bestFitness': gBestTrain['gBestFitness'],
                'bestAccuracy': gBestTrain['gBestAccuracy'],
                'bestRecall': gBestTrain['gBestRecall'],
                'bestPrecision': gBestTrain['gBestPrecision'],
                'bestF1Score': gBestTrain['gBestF1Score'],
                'bestFeatures': self.__get_optimal_features(
                    bit_encoding=self.BIT_ENCODING,
                    active_bit_encoding=gBestTrain['gBestPosition']
                ),
            },
            'validation': {
                'bestIndexParticle': np.argmax(pBestValidation['pBestFitness']),
                'bestFitness': gBestValidation['gBestFitness'],
                'bestAccuracy': gBestValidation['gBestAccuracy'],
                'bestRecall': gBestValidation['gBestRecall'],
                'bestPrecision': gBestValidation['gBestPrecision'],
                'bestF1Score': gBestValidation['gBestF1Score'],
                'bestFeatures': self.__get_optimal_features(
                    bit_encoding=self.BIT_ENCODING,
                    active_bit_encoding=gBestValidation['gBestPosition']
                ),
            },
            'logs': {
                **self.LOGS_VARIABLES
            }
        }
        # 4. Save the logs processes
        self.__save_logs_file()

        return self.OPTIMIZATION_RESULTS

    def __initialize_particles(self):
        # random between 0 or 1 using numpy
        particles = np.random.randint(
            self.LOWER_BOUND, self.UPPER_BOUND+1, size=(self.PARTICLE_SIZE, self.NUM_PARTICLE_ELEMENT))
        velocities = np.zeros((self.PARTICLE_SIZE, self.NUM_PARTICLE_ELEMENT))

        pBestPosition = particles
        # karena tujuannya memaksimasi, maka set infinite negatif
        pBestFitness = [float('-inf') for i in range(self.PARTICLE_SIZE)]
        pBestAccuracy = [float('-inf') for i in range(self.PARTICLE_SIZE)]
        pBestRecall = [float('-inf') for i in range(self.PARTICLE_SIZE)]
        pBestPrecision = [float('-inf') for i in range(self.PARTICLE_SIZE)]
        pBestF1Score = [float('-inf') for i in range(self.PARTICLE_SIZE)]
        gBestPosition = np.zeros(self.NUM_PARTICLE_ELEMENT)
        gBestFitness = float('-inf')
        gBestAccuracy = float('-inf')
        gBestRecall = float('-inf')
        gBestPrecision = float('-inf')
        gBestF1Score = float("-inf")

        # pBest dan gBest untuk data training
        pBestTrain = {
            'pBestPosition': pBestPosition.copy(),
            'pBestFitness': pBestFitness.copy(),
            'pBestAccuracy': pBestAccuracy.copy(),
            'pBestRecall': pBestRecall.copy(),
            'pBestPrecision': pBestPrecision.copy(),
            'pBestF1Score': pBestF1Score.copy(),
        }
        gBestTrain = {
            'gBestPosition': gBestPosition,
            'gBestFitness': gBestFitness,
            'gBestAccuracy': gBestAccuracy,
            'gBestRecall': gBestRecall,
            'gBestPrecision': gBestPrecision,
            'gBestF1Score': gBestF1Score,
        }

        # pBest dan gBest untuk data validasi
        pBestValidation = {
            'pBestPosition': pBestPosition.copy(),
            'pBestFitness': pBestFitness.copy(),
            'pBestAccuracy': pBestAccuracy.copy(),
            'pBestRecall': pBestRecall.copy(),
            'pBestPrecision': pBestPrecision.copy(),
            'pBestF1Score': pBestF1Score.copy(),
        }
        gBestValidation = {
            'gBestPosition': gBestPosition,
            'gBestFitness': gBestFitness,
            'gBestAccuracy': gBestAccuracy,
            'gBestRecall': gBestRecall,
            'gBestPrecision': gBestPrecision,
            'gBestF1Score': gBestF1Score,
        }

        return particles, velocities, pBestTrain, gBestTrain, pBestValidation, gBestValidation

    def __update_velocities(self, particles, velocities, pBest, gBest):
        pBestPosition = pBest['pBestPosition']
        gBestPosition = gBest['gBestPosition']
        # get the PSO params
        w = self.INERTIA
        c1 = self.PHI1
        c2 = self.PHI2
        r1 = np.random.rand(self.PARTICLE_SIZE, self.NUM_PARTICLE_ELEMENT)
        r2 = np.random.rand(self.PARTICLE_SIZE, self.NUM_PARTICLE_ELEMENT)
        velocities = w*velocities + c1*r1 * \
            (pBestPosition - particles) + c2*r2*(gBestPosition - particles)
        return velocities

    def __apply_boundaries(self, particles, velocities):
        # apply boundaries to particles positions using sigmoid function
        for idx_particle, particle in enumerate(particles):
            particles[idx_particle] = np.where(
                1/(1 + np.exp(-particle)) < np.random.uniform(0, 1), self.LOWER_BOUND, self.UPPER_BOUND)
            # check if particle only contain 0? if any, convert to 1 randomly
            if np.count_nonzero(particle == 0) == self.NUM_PARTICLE_ELEMENT:
                list_of_random_index = list()
                for i in range(self.NUM_RANDOM_CHAOSTIC_BOUNDARIES):
                    random_index = rd.randint(0, self.NUM_PARTICLE_ELEMENT-1)
                    while (random_index in list_of_random_index):
                        random_index = rd.randint(
                            0, self.NUM_PARTICLE_ELEMENT-1)
                    particle[random_index] = 1
                    list_of_random_index.append(random_index)
            # check if particle only contain 1? if any, convert to 0 randomly
            if np.count_nonzero(particle == 1) == self.NUM_PARTICLE_ELEMENT:
                list_of_random_index = list()
                for i in range(self.NUM_RANDOM_CHAOSTIC_BOUNDARIES):
                    random_index = rd.randint(0, self.NUM_PARTICLE_ELEMENT-1)
                    while (random_index in list_of_random_index):
                        random_index = rd.randint(
                            0, self.NUM_PARTICLE_ELEMENT-1)
                    particle[random_index] = 0
                    list_of_random_index.append(random_index)
        # velocities = np.clip(velocities, -self.LOWER_BOUND, self.UPPER_BOUND)
        return particles, velocities

    def __fitness_function(self, particle):
        bit_encoding = self.__get_optimal_features(
            bit_encoding=self.BIT_ENCODING,
            active_bit_encoding=particle
        )

        # train CRF using fold-train
        crf = ConditionalRandomFields(
            feature_encoding=bit_encoding,
            crf_hyperparameters=self.CRF_CONFIG
        ).fit(self.DATA_TRAIN)

        # evaluate crf model using fold-validation
        y_pred_val = crf.predict(self.DATA_VALIDATION)
        train_evaluation, validation_evaluation = crf.evaluate(
            crf.Y_TRAIN,
            crf.y_pred_train,
            crf.Y_TEST,
            crf.y_pred_test
        )

        # hitung metrics data train dan data validation
        fitnessResults = {
            'train': {
                'accuracy': train_evaluation['accuracy'],
                'recall': train_evaluation['recall'],
                'precision': train_evaluation['precision'],
                'f1_score': train_evaluation['f1_score'],
            },
            'validation': {
                'accuracy': validation_evaluation['accuracy'],
                'recall': validation_evaluation['recall'],
                'precision': validation_evaluation['precision'],
                'f1_score': validation_evaluation['f1_score'],
            }
        }

        return fitnessResults

    def __update_pBest(self, pBest, particles, fitnessParticles):
        for idx_particle in range(self.PARTICLE_SIZE):
            if fitnessParticles[self.FITNESS_OBJECTIVE][idx_particle] > pBest['pBestFitness'][idx_particle]:
                pBest['pBestPosition'][idx_particle] = particles[idx_particle]
                pBest['pBestFitness'][idx_particle] = fitnessParticles[self.FITNESS_OBJECTIVE][idx_particle]
                pBest['pBestAccuracy'][idx_particle] = fitnessParticles['accuracy'][idx_particle]
                pBest['pBestRecall'][idx_particle] = fitnessParticles['recall'][idx_particle]
                pBest['pBestPrecision'][idx_particle] = fitnessParticles['precision'][idx_particle]
                pBest['pBestF1Score'][idx_particle] = fitnessParticles['f1_score'][idx_particle]
        return pBest

    def __update_gBest(self, gBest, pBest):
        if np.max(pBest['pBestFitness']) > gBest['gBestFitness']:
            max_fitness_index = np.argmax(pBest['pBestFitness'])
            gBest['gBestPosition'] = pBest['pBestPosition'][max_fitness_index]
            gBest['gBestFitness'] = pBest['pBestFitness'][max_fitness_index]
            gBest['gBestAccuracy'] = pBest['pBestAccuracy'][max_fitness_index]
            gBest['gBestRecall'] = pBest['pBestRecall'][max_fitness_index]
            gBest['gBestPrecision'] = pBest['pBestPrecision'][max_fitness_index]
            gBest['gBestF1Score'] = pBest['pBestF1Score'][max_fitness_index]
        return gBest

    def __get_optimal_features(self, bit_encoding, active_bit_encoding):
        """
        <Descriptions>
        Only activated bit_encoding with '1' active_bit_encoding

        <Input>
        - bit_encoding: Dictionary contain all feature set
        bit_encoding = {
            'feature-1': True,
            'feature-2': True,
            'feature-3': True,
            dst
        }
        - active_bit_encoding: array of 1 or 0 bits corresponds to each key in bit_encoding. 1 means the feature will be activated
        active_bit_encoding = [
        0,
        1,
        0,
        1,
        dst
        ]
        Only second and fourth features will be actived
        """
        new_bit_encoding = copy.deepcopy(bit_encoding)
        for index, key in enumerate(bit_encoding):
            new_bit_encoding[key] = False if active_bit_encoding[index] == 0 else True
        return new_bit_encoding

    # logging processes
    def __initialize_logs_variables(self, **kwargs):
        self.LOGS_VARIABLES = dict([
            (key, list()) for key in kwargs
        ])
        return self

    def __append_logs_variables(self, **kwargs):
        for key in kwargs:
            self.LOGS_VARIABLES[key].append(kwargs[key])

    def __print_to_prompt(self, **kwargs):
        if kwargs['messages']:
            for message in kwargs['messages']:
                print(message)

    def __save_logs_file(self, **kwargs):
        if 'additional_messages' in kwargs:
            with open(self.PATH_LOGS_FILE, 'a') as file1:
                for message in kwargs['additional_messages']:
                    file1.write(message)
        else:
            for idx_, data in enumerate(self.LOGS_VARIABLES['ITERATIONS']):
                iteration = self.LOGS_VARIABLES['ITERATIONS'][idx_]
                convergence_value = self.LOGS_VARIABLES['CONVERGENCE_VALUES'][idx_]
                et = self.LOGS_VARIABLES['TIME_OPTIMIZATION_TRACKING'][idx_]
                particles = self.LOGS_VARIABLES['PARTICLES_TRACKING'][idx_]

                # get train logs information
                BEST_ACCURACY_TRAINING = self.LOGS_VARIABLES['BEST_ACCURACY_TRAINING'][idx_]
                BEST_RECALL_TRAINING = self.LOGS_VARIABLES['BEST_RECALL_TRAINING'][idx_]
                BEST_PRECISION_TRAINING = self.LOGS_VARIABLES['BEST_PRECISION_TRAINING'][idx_]
                BEST_F1_SCORE_TRAINING = self.LOGS_VARIABLES['BEST_F1_SCORE_TRAINING'][idx_]
                BEST_FITNESS_TRAINING = self.LOGS_VARIABLES['BEST_FITNESS_TRAINING'][idx_]
                BEST_FEATURES_TRAINING = self.LOGS_VARIABLES['BEST_FEATURES_TRAINING'][idx_]
                WORST_ACCURACY_TRAINING = self.LOGS_VARIABLES['WORST_ACCURACY_TRAINING'][idx_]
                WORST_RECALL_TRAINING = self.LOGS_VARIABLES['WORST_RECALL_TRAINING'][idx_]
                WORST_PRECISION_TRAINING = self.LOGS_VARIABLES['WORST_PRECISION_TRAINING'][idx_]
                WORST_F1_SCORE_TRAINING = self.LOGS_VARIABLES['WORST_F1_SCORE_TRAINING'][idx_]
                WORST_FITNESS_TRAINING = self.LOGS_VARIABLES['WORST_FITNESS_TRAINING'][idx_]

                # get validation logs information
                BEST_ACCURACY_VALIDATION = self.LOGS_VARIABLES['BEST_ACCURACY_VALIDATION'][idx_]
                BEST_RECALL_VALIDATION = self.LOGS_VARIABLES['BEST_RECALL_VALIDATION'][idx_]
                BEST_PRECISION_VALIDATION = self.LOGS_VARIABLES['BEST_PRECISION_VALIDATION'][idx_]
                BEST_F1_SCORE_VALIDATION = self.LOGS_VARIABLES['BEST_F1_SCORE_VALIDATION'][idx_]
                BEST_FITNESS_VALIDATION = self.LOGS_VARIABLES['BEST_FITNESS_VALIDATION'][idx_]
                BEST_FEATURES_VALIDATION = self.LOGS_VARIABLES['BEST_FEATURES_VALIDATION'][idx_]
                WORST_ACCURACY_VALIDATION = self.LOGS_VARIABLES['WORST_ACCURACY_VALIDATION'][idx_]
                WORST_RECALL_VALIDATION = self.LOGS_VARIABLES['WORST_RECALL_VALIDATION'][idx_]
                WORST_PRECISION_VALIDATION = self.LOGS_VARIABLES['WORST_PRECISION_VALIDATION'][idx_]
                WORST_F1_SCORE_VALIDATION = self.LOGS_VARIABLES['WORST_F1_SCORE_VALIDATION'][idx_]
                WORST_FITNESS_VALIDATION = self.LOGS_VARIABLES['WORST_FITNESS_VALIDATION'][idx_]

                with open(self.PATH_LOGS_FILE, 'a') as file1:
                    file1.write('='*50+"\n")
                    file1.write(f"\t\tITERATION - {iteration}\n")
                    file1.write(f"CONVERGENCE = {convergence_value}\n")
                    file1.write(f"TIME = {et} seconds\n")
                    file1.write(f"PARTICLES = {particles}\n")
                    file1.write(f"\t\VALIDATION LOGS\n")
                    file1.write(
                        f"BEST {self.FITNESS_OBJECTIVE.upper()} =  {BEST_FITNESS_VALIDATION}\n")
                    file1.write(
                        f"BEST ACCURACY = {BEST_ACCURACY_VALIDATION}\n")
                    file1.write(f"BEST RECALL = {BEST_RECALL_VALIDATION}\n")
                    file1.write(
                        f"BEST PRECISION = {BEST_PRECISION_VALIDATION}\n")
                    file1.write(
                        f"BEST F1_SCORE = {BEST_F1_SCORE_VALIDATION}\n")
                    file1.write(
                        f"BEST FEATURES SET = {BEST_FEATURES_VALIDATION}\n")
                    file1.write(
                        f"WORST {self.FITNESS_OBJECTIVE.upper()} =  {WORST_FITNESS_VALIDATION}\n")
                    file1.write(
                        f"WORST ACCURACY = {WORST_ACCURACY_VALIDATION}\n")
                    file1.write(f"WORST RECALL = {WORST_RECALL_VALIDATION}\n")
                    file1.write(
                        f"WORST PRECISION = {WORST_PRECISION_VALIDATION}\n")
                    file1.write(
                        f"WORST F1_SCORE = {WORST_F1_SCORE_VALIDATION}\n")
                    file1.write('='*50+"\n")
                    file1.write(f"\t\TRAIN LOGS\n")
                    file1.write(
                        f"BEST {self.FITNESS_OBJECTIVE.upper()} =  {BEST_FITNESS_TRAINING}\n")
                    file1.write(
                        f"BEST ACCURACY = {BEST_ACCURACY_TRAINING}\n")
                    file1.write(f"BEST RECALL = {BEST_RECALL_TRAINING}\n")
                    file1.write(
                        f"BEST PRECISION = {BEST_PRECISION_TRAINING}\n")
                    file1.write(
                        f"BEST F1_SCORE = {BEST_F1_SCORE_TRAINING}\n")
                    file1.write(
                        f"BEST FEATURES SET = {BEST_FEATURES_TRAINING}\n")
                    file1.write(
                        f"WORST {self.FITNESS_OBJECTIVE.upper()} =  {WORST_FITNESS_TRAINING}\n")
                    file1.write(
                        f"WORST ACCURACY = {WORST_ACCURACY_TRAINING}\n")
                    file1.write(f"WORST RECALL = {WORST_RECALL_TRAINING}\n")
                    file1.write(
                        f"WORST PRECISION = {WORST_PRECISION_TRAINING}\n")
                    file1.write(
                        f"WORST F1_SCORE = {WORST_F1_SCORE_TRAINING}\n")
                    file1.write('='*50+"\n")
