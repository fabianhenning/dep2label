# -*- coding: utf-8 -*-
# @Author: Jie
# @Date:   2017-06-14 17:34:32
# @Last Modified by:   Jie Yang,     Contact: jieynlp@gmail.com
# @Last Modified time: 2018-04-26 13:58:10

from functions import *
import cPickle as pickle


START = "</s>"
UNKNOWN = "</unk>"
PADDING = "</pad>"


class Data:
    def __init__(self):
        self.MAX_SENTENCE_LENGTH = 250
        self.MAX_WORD_LENGTH = -1
        self.number_normalized = True
        self.norm_word_emb = False
        self.norm_char_emb = False
        self.word_alphabet = Alphabet('word')
        self.char_alphabet = Alphabet('character')

        self.feature_name = []
        self.feature_alphabets = []
        self.feature_num = len(self.feature_alphabets)
        self.feat_config = None

        self.label_alphabet = {0: Alphabet('label',True)}
        self.tagScheme = "NoSeg" ## BMES/BIO
        self.seg = True

        ### I/O
        self.train_dir = None 
        self.dev_dir = None
        self.test_dir = None
        self.raw_dir = None

        self.decode_dir = None
        self.dset_dir = None ## data vocabulary related file
        self.model_dir = None ## model save  file
        self.load_model_dir = None ## model load file

        self.word_emb_dir = None 
        self.char_emb_dir = None
        self.feature_emb_dirs = []

        self.train_texts = []
        self.dev_texts = []
        self.test_texts = []
        self.raw_texts = []

        self.train_Ids = []
        self.dev_Ids = []
        self.test_Ids = []
        self.raw_Ids = []

        self.pretrain_word_embedding = None
        self.pretrain_char_embedding = None
        self.pretrain_feature_embeddings = []


        self.label_size = 0
        self.word_alphabet_size = 0
        self.char_alphabet_size = 0
        self.label_alphabet_sizes = {0:0}
        self.feature_alphabet_sizes = []
        self.feature_emb_dims = []
        self.norm_feature_embs = []
        self.word_emb_dim = 50
        self.char_emb_dim = 30

        ###Networks
        self.word_feature_extractor = "LSTM" ## "LSTM"/"CNN"/"GRU"/
        self.use_char = True
        self.char_feature_extractor = "CNN" ## "LSTM"/"CNN"/"GRU"/None
        self.use_crf = True
        self.nbest = None
        
        ## Training
        self.average_batch_loss = False
        self.optimizer = "SGD" ## "SGD"/"AdaGrad"/"AdaDelta"/"RMSProp"/"Adam"
        self.status = "train"

        ### Hyperparameters
        self.HP_cnn_layer = 4
        self.HP_iteration = 100
        self.HP_batch_size = 10
        self.HP_char_hidden_dim = 50
        self.HP_hidden_dim = 200
        self.HP_feature_default_size = 20
        self.HP_dropout = 0.5
        self.HP_lstm_layer = 1
        self.HP_bilstm = True
        
        self.HP_gpu = False
        self.HP_lr = 0.015
        self.HP_lr_decay = 0.05
        self.HP_clip = None
        self.HP_momentum = 0
        self.HP_l2 = 1e-8
        
        #MTL Setup
        self.HP_tasks = 1
        self.HP_main_tasks = self.HP_tasks
        self.HP_tasks_weights = [1]
        self.dependency_parsing = True
        self.constituency_parsing = True
        self.language="English"
        self.index_of_main_tasks = None
        
    def show_data_summary(self):
        print("++"*50)
        print("DATA SUMMARY START:")
        print(" I/O:")
        print("     Tag          scheme: %s"%(self.tagScheme))
        print("     MAX SENTENCE LENGTH: %s"%(self.MAX_SENTENCE_LENGTH))
        print("     MAX   WORD   LENGTH: %s"%(self.MAX_WORD_LENGTH))
        print("     Number   normalized: %s"%(self.number_normalized))
        print("     Word  alphabet size: %s"%(self.word_alphabet_size))
        print("     Char  alphabet size: %s"%(self.char_alphabet_size))
        for idtask in self.label_alphabet:
            print ("     Label alphabet size for task %s: %s"%(idtask,self.label_alphabet_sizes[idtask]))
        #print("     Label alphabet size: %s"%(self.label_alphabet_size))
        print("     Word embedding  dir: %s"%(self.word_emb_dir))
        print("     Char embedding  dir: %s"%(self.char_emb_dir))
        print("     Word embedding size: %s"%(self.word_emb_dim))
        print("     Char embedding size: %s"%(self.char_emb_dim))
        print("     Norm   word     emb: %s"%(self.norm_word_emb))
        print("     Norm   char     emb: %s"%(self.norm_char_emb))
        print("     Train  file directory: %s"%(self.train_dir))
        print("     Dev    file directory: %s"%(self.dev_dir))
        print("     Test   file directory: %s"%(self.test_dir))
        print("     Raw    file directory: %s"%(self.raw_dir))
        print("     Dset   file directory: %s"%(self.dset_dir))
        print("     Model  file directory: %s"%(self.model_dir))
        print("     Loadmodel   directory: %s"%(self.load_model_dir))
        print("     Decode file directory: %s"%(self.decode_dir))
        print("     Train instance number: %s"%(len(self.train_texts)))
        print("     Dev   instance number: %s"%(len(self.dev_texts)))
        print("     Test  instance number: %s"%(len(self.test_texts)))
        print("     Raw   instance number: %s"%(len(self.raw_texts)))
        print("     FEATURE num: %s"%(self.feature_num))
        for idx in range(self.feature_num):
            print("         Fe: %s  alphabet  size: %s"%(self.feature_alphabets[idx].name, self.feature_alphabet_sizes[idx]))
            print("         Fe: %s  embedding  dir: %s"%(self.feature_alphabets[idx].name, self.feature_emb_dirs[idx]))
            print("         Fe: %s  embedding size: %s"%(self.feature_alphabets[idx].name, self.feature_emb_dims[idx]))
            print("         Fe: %s  norm       emb: %s"%(self.feature_alphabets[idx].name, self.norm_feature_embs[idx]))
        print(" "+"++"*20)
        print(" Model Network:")
        print("     Model        use_crf: %s"%(self.use_crf))
        print("     Model word extractor: %s"%(self.word_feature_extractor))
        print("     Model       use_char: %s"%(self.use_char))
        if self.use_char:
            print("     Model char extractor: %s"%(self.char_feature_extractor))
            print("     Model char_hidden_dim: %s"%(self.HP_char_hidden_dim))
        print(" "+"++"*20)
        print(" Training:")
        print("     Optimizer: %s"%(self.optimizer))
        print("     Iteration: %s"%(self.HP_iteration))
        print("     BatchSize: %s"%(self.HP_batch_size))
        print("     Average  batch   loss: %s"%(self.average_batch_loss))

        print(" "+"++"*20)
        print(" Hyperparameters:")
        
        print("     Hyper              lr: %s"%(self.HP_lr))
        print("     Hyper        lr_decay: %s"%(self.HP_lr_decay))
        print("     Hyper         HP_clip: %s"%(self.HP_clip))
        print("     Hyper        momentum: %s"%(self.HP_momentum))
        print("     Hyper              l2: %s"%(self.HP_l2))
        print("     Hyper      hidden_dim: %s"%(self.HP_hidden_dim))
        print("     Hyper         dropout: %s"%(self.HP_dropout))
        print("     Hyper      lstm_layer: %s"%(self.HP_lstm_layer))
        print("     Hyper          bilstm: %s"%(self.HP_bilstm))
        print("     Hyper             GPU: %s"%(self.HP_gpu))
        print("     Hyper number of tasks: %s"%(self.HP_tasks))

        #TODO: print PG hyperparams
        print("DATA SUMMARY END.")
        print("++"*50)
        sys.stdout.flush()


    def initial_feature_alphabets(self):
        items = open(self.train_dir,'r').readline().strip('\n').split()
        total_column = len(items)
        if total_column > 2:
            for idx in range(1, total_column-1):
                feature_prefix = items[idx].split(']',1)[0]+"]"
                self.feature_alphabets.append(Alphabet(feature_prefix))
                self.feature_name.append(feature_prefix)
                print "Find feature: ", feature_prefix 
        self.feature_num = len(self.feature_alphabets)
        self.pretrain_feature_embeddings = [None]*self.feature_num
        self.feature_emb_dims = [self.HP_feature_default_size]*self.feature_num
        self.feature_emb_dirs = [None]*self.feature_num 
        self.norm_feature_embs = [False]*self.feature_num
        self.feature_alphabet_sizes = [0]*self.feature_num
        if self.feat_config:
            for idx in range(self.feature_num):
                print self.feat_config
                print "["+str(idx+1)+"]"
                if "["+str(idx+1)+"]" in self.feat_config:
                    self.feature_emb_dims[idx] = self.feat_config["["+str(idx+1)+"]"]['emb_size']
                    self.feature_emb_dirs[idx] = self.feat_config["["+str(idx+1)+"]"]['emb_dir']
                    self.norm_feature_embs[idx] = self.feat_config["["+str(idx+1)+"]"]['emb_norm']

    def build_alphabet(self, input_file):
        in_lines = open(input_file,'r').readlines()
        for line in in_lines:
            if len(line) > 2:
                pairs = line.strip().split()
                word = pairs[0].decode('utf-8')
                if self.number_normalized:
                    word = normalize_word(word)
                label = pairs[-1]
                
                if self.HP_tasks > 1:
                    label = parse_multitask_label(label)
                else:
                    label = [label]
                
                if len(label) != len(self.label_alphabet):
                    raise ValueError("The number of tasks and the number of labels in the output column do not match")
                
                for idtask, l in enumerate(label):
                    self.label_alphabet[idtask].add(l)

                self.word_alphabet.add(word)
                for idx in range(self.feature_num):
                    feat_idx = pairs[idx+1].split(']',1)[-1]
                    self.feature_alphabets[idx].add(feat_idx)
                    
                for char in word:
                    self.char_alphabet.add(char)
        self.word_alphabet_size = self.word_alphabet.size()
        self.char_alphabet_size = self.char_alphabet.size()
        
        for idtask in self.label_alphabet:
            self.label_alphabet_sizes[idtask] = self.label_alphabet[idtask].size()

        for idx in range(self.feature_num):
            self.feature_alphabet_sizes[idx] = self.feature_alphabets[idx].size()
            

        for idtask in self.label_alphabet:
            startS = False
            startB = False
        
            for label,_ in self.label_alphabet[idtask].iteritems():
                if "S-" in label.upper():
                    startS = True
                elif "B-" in label.upper():
                    startB = True
            if startB:
                if startS:
                    self.tagScheme = "BMES"
                else:
                    self.tagScheme = "BIO"

    def fix_alphabet(self):
        self.word_alphabet.close()
        self.char_alphabet.close()
        
        for idtask in self.label_alphabet:
            self.label_alphabet[idtask].close()
        
        #self.label_alphabet.close() 
        for idx in range(self.feature_num):
            self.feature_alphabets[idx].close()      


    def build_pretrain_emb(self):
        if self.word_emb_dir:
            print("Load pretrained word embedding, norm: %s, dir: %s"%(self.norm_word_emb, self.word_emb_dir))
            self.pretrain_word_embedding, self.word_emb_dim = build_pretrain_embedding(self.word_emb_dir, self.word_alphabet, self.word_emb_dim, self.norm_word_emb)
        if self.char_emb_dir:
            print("Load pretrained char embedding, norm: %s, dir: %s"%(self.norm_char_emb, self.char_emb_dir))
            self.pretrain_char_embedding, self.char_emb_dim = build_pretrain_embedding(self.char_emb_dir, self.char_alphabet, self.char_emb_dim, self.norm_char_emb)
        for idx in range(self.feature_num):
            if self.feature_emb_dirs[idx]:
                print("Load pretrained feature %s embedding:, norm: %s, dir: %s"%(self.feature_name[idx], self.norm_feature_embs[idx], self.feature_emb_dirs[idx]))
                self.pretrain_feature_embeddings[idx], self.feature_emb_dims[idx] = build_pretrain_embedding(self.feature_emb_dirs[idx], self.feature_alphabets[idx], self.feature_emb_dims[idx], self.norm_feature_embs[idx])


    def generate_instance(self, name):
        self.fix_alphabet()
        if name == "train":
            self.train_texts, self.train_Ids = read_instance(self.train_dir, self.word_alphabet, self.char_alphabet, self.feature_alphabets, self.label_alphabet, self.number_normalized, self.MAX_SENTENCE_LENGTH, self.HP_tasks)
        elif name == "dev":
            self.dev_texts, self.dev_Ids = read_instance(self.dev_dir, self.word_alphabet, self.char_alphabet, self.feature_alphabets, self.label_alphabet, self.number_normalized, self.MAX_SENTENCE_LENGTH, self.HP_tasks)
        elif name == "test":
            self.test_texts, self.test_Ids = read_instance(self.test_dir, self.word_alphabet, self.char_alphabet, self.feature_alphabets, self.label_alphabet, self.number_normalized, self.MAX_SENTENCE_LENGTH, self.HP_tasks)
        elif name == "raw":
            self.raw_texts, self.raw_Ids = read_instance(self.raw_dir, self.word_alphabet, self.char_alphabet, self.feature_alphabets, self.label_alphabet, self.number_normalized, self.MAX_SENTENCE_LENGTH, self.HP_main_tasks)
        else:
            print("Error: you can only generate train/dev/test instance! Illegal input:%s"%(name))


    def write_decoded_results(self, predict_results, name):
        fout = open(self.decode_dir,'w')
        content_list = []
        if name == 'raw':
           content_list = self.raw_texts
        elif name == 'test':
            content_list = self.test_texts
        elif name == 'dev':
            content_list = self.dev_texts
        elif name == 'train':
            content_list = self.train_texts
        else:
            print("Error: illegal name during writing predict result, name should be within train/dev/test/raw !")

        for task_predict_results in predict_results:
            sent_num = len(task_predict_results)
            assert(sent_num == len(content_list))
        #TODO: This won't work if the same input is not shared by all tasks
        for idx in range(sent_num):
            sent_length = len(predict_results[0][idx])
            for idy in range(sent_length):
                inputs = []
                for id_input in range(len(content_list[idx])-2):
                    if content_list[idx][id_input][0] != []:
                        if type(content_list[idx][id_input][idy]) == type([]):
                            for feature in content_list[idx][id_input][idy]:
                                inputs.append(feature.encode('utf-8'))
                        else:
                            inputs.append(content_list[idx][id_input][idy].encode('utf-8'))
            
                outputs = []
                for task in predict_results:
                    outputs.append(task[idx][idy])
                
                fout.write( "\t".join(inputs) + "\t" + "{}".join(outputs) + '\n')
            fout.write('\n')
        fout.close()
        print("Predict %s result has been written into file. %s"%(name, self.decode_dir))



    #for optimizing with pyevalb
    def write_decoded_results_ids_int(self, predict_results, train_id=None):

        output = ''
        content_list = self.train_texts[train_id]
        sent_length = len(predict_results[0][0])
        con_length = len(content_list[0])


        for idy in range(sent_length):
            inputs = []
            for id_input in range(len(content_list) - 2):
                if content_list[id_input][0] != []:
                    if type(content_list[id_input][idy]) == type([]):
                        for feature in content_list[id_input][idy]:
                            inputs.append(feature.encode('utf-8'))
                    else:
                        inputs.append(content_list[id_input][idy].encode('utf-8'))
            outputs = []
            for task in predict_results:
                outputs.append(task[0][idy])

            output += "\t".join(inputs) + "\t" + "{}".join(outputs) + '\n' + '^^'

        output += '\n'
        return output



    def load(self,data_file):
        f = open(data_file, 'rb')
        tmp_dict = pickle.load(f)
        f.close()
        self.__dict__.update(tmp_dict)

    def save(self,save_file):
        f = open(save_file, 'wb')
        pickle.dump(self.__dict__, f, 2)
        f.close()

    def write_nbest_decoded_results(self, predict_results, pred_scores, name):

        fout = open(self.decode_dir,'w')
        sent_num = len(predict_results)
        content_list = []
        if name == 'raw':
           content_list = self.raw_texts
        elif name == 'test':
            content_list = self.test_texts
        elif name == 'dev':
            content_list = self.dev_texts
        elif name == 'train':
            content_list = self.train_texts
        else:
            print("Error: illegal name during writing predict result, name should be within train/dev/test/raw !")

        for idtask_predict_results, task_predict_results in enumerate(predict_results):
            sent_num = len(task_predict_results)
            assert(sent_num == len(content_list))
            
        for idx in range(sent_num):
            score_string = "# "

            for idtask_predict_results, task_predict_results in enumerate(predict_results):
                sent_length = len(task_predict_results[idx][0])
                nbest = len(task_predict_results[0])

                #Printing the probabilities
                for idz in range(nbest):
                    score_string += format(pred_scores[idtask_predict_results][idx][idz], '.4f')+" "
            fout.write(score_string.strip() + "\t")    
            fout.write("\n")
    

            for idy in range(sent_length):
                print content_list[idx][0]
                print content_list[idx][1]
                label_string = content_list[idx][0][idy].encode('utf-8') + "\t"
                for ifeat in range(len(content_list[idx][1][idy])):
                    label_string += content_list[idx][1][idy][ifeat].encode('utf-8') + "\t"
                
                for idtask_predict_results, task_predict_results in enumerate(predict_results):            
                    for idz in range(nbest):
                        label_string += task_predict_results[idx][idz][idy]+","
                    label_string = label_string.strip().strip(",") + "{}"
                fout.write(label_string)
                fout.write('\n')
            fout.write('\n')
        fout.close()
        print("Predict %s %s-best result has been written into file. %s"%(name,nbest, self.decode_dir))

    def read_config(self,config_file):
        config = config_file_to_dict(config_file)
        the_item = 'train_dir'
        if the_item in config:
            self.train_dir = config[the_item]
        the_item = 'dev_dir'
        if the_item in config:
            self.dev_dir = config[the_item]
        the_item = 'test_dir'
        if the_item in config:
            self.test_dir = config[the_item]
        the_item = 'raw_dir'
        if the_item in config:
            self.raw_dir = config[the_item]
        the_item = 'decode_dir'
        if the_item in config:
            self.decode_dir = config[the_item]
        the_item = 'dset_dir'
        if the_item in config:
            self.dset_dir = config[the_item]
        the_item = 'model_dir'
        if the_item in config:
            self.model_dir = config[the_item]
        the_item = 'load_model_dir'
        if the_item in config:
            self.load_model_dir = config[the_item]
        the_item = 'word_emb_dir'
        if the_item in config:
            self.word_emb_dir = config[the_item]
        the_item = 'char_emb_dir'
        if the_item in config:
            self.char_emb_dir = config[the_item]


        the_item = 'MAX_SENTENCE_LENGTH'
        if the_item in config:
            self.MAX_SENTENCE_LENGTH = int(config[the_item])
        the_item = 'MAX_WORD_LENGTH'
        if the_item in config:
            self.MAX_WORD_LENGTH = int(config[the_item])

        the_item = 'norm_word_emb'
        if the_item in config:
            self.norm_word_emb = str2bool(config[the_item])
        the_item = 'norm_char_emb'
        if the_item in config:
            self.norm_char_emb = str2bool(config[the_item])
        the_item = 'number_normalized'
        if the_item in config:
            self.number_normalized = str2bool(config[the_item])


        the_item = 'seg'
        if the_item in config:
            self.seg = str2bool(config[the_item])
        the_item = 'word_emb_dim'
        if the_item in config:
            self.word_emb_dim = int(config[the_item])
        the_item = 'char_emb_dim'
        if the_item in config:
            self.char_emb_dim = int(config[the_item])

        ## read network:
        the_item = 'use_crf'
        if the_item in config:
            self.use_crf = str2bool(config[the_item])
        the_item = 'use_char'
        if the_item in config:
            self.use_char = str2bool(config[the_item])
        the_item = 'word_seq_feature'
        if the_item in config:
            self.word_feature_extractor = config[the_item]
        the_item = 'char_seq_feature'
        if the_item in config:
            self.char_feature_extractor = config[the_item]
        the_item = 'nbest'
        if the_item in config:
            self.nbest = int(config[the_item])

        the_item = 'feature'
        if the_item in config:
            self.feat_config = config[the_item] ## feat_config is a dict

        the_item = 'feature_default_size'
        if the_item in config:
            self.HP_feature_default_size = int(config[the_item])

        ## read training setting:
        the_item = 'optimizer'
        if the_item in config:
            self.optimizer = config[the_item]
        the_item = 'ave_batch_loss'
        if the_item in config:
            self.average_batch_loss = str2bool(config[the_item])
        the_item = 'status'
        if the_item in config:
            self.status = config[the_item]

        ## read Hyperparameters:
        the_item = 'cnn_layer'
        if the_item in config:
            self.HP_cnn_layer = int(config[the_item])
        the_item = 'iteration'
        if the_item in config:
            self.HP_iteration = int(config[the_item])
        the_item = 'batch_size'
        if the_item in config:
            self.HP_batch_size = int(config[the_item])

        the_item = 'char_hidden_dim'
        if the_item in config:
            self.HP_char_hidden_dim = int(config[the_item])
        the_item = 'hidden_dim'
        if the_item in config:
            self.HP_hidden_dim = int(config[the_item])
        the_item = 'dropout'
        if the_item in config:
            self.HP_dropout = float(config[the_item])
        the_item = 'lstm_layer'
        if the_item in config:
            self.HP_lstm_layer = int(config[the_item])
        the_item = 'bilstm'
        if the_item in config:
            self.HP_bilstm = str2bool(config[the_item])

        the_item = 'gpu'
        if the_item in config:
            self.HP_gpu = str2bool(config[the_item])
        the_item = 'learning_rate'
        if the_item in config:
            self.HP_lr = float(config[the_item])
        the_item = 'lr_decay'
        if the_item in config:
            self.HP_lr_decay = float(config[the_item])
        the_item = 'clip'
        if the_item in config:
            self.HP_clip = float(config[the_item])
        the_item = 'momentum'
        if the_item in config:
            self.HP_momentum = float(config[the_item])
        the_item = 'l2'
        if the_item in config:
            self.HP_l2 = float(config[the_item])

        the_item = 'tasks'
        if the_item in config:
            self.HP_tasks = int(config[the_item])
            if self.HP_tasks > 1:
                self.label_alphabet = {idtask: Alphabet('label',True) for idtask in range(self.HP_tasks)}
                self.label_alphabet_sizes = {idtask: self.label_alphabet[idtask].size() for idtask in range(self.HP_tasks)}
        
        the_item = "main_tasks"
        if the_item in config:
            self.HP_main_tasks = int(config[the_item])     
            if self.HP_main_tasks > self.HP_tasks:
                raise ValueError("HP_main_tasks cannot be greater than HP_tasks")   
        
        the_item = 'tasks_weights'
        if the_item in config:
            self.HP_tasks_weights = map(float,config[the_item].split("|"))
            
        the_item = 'evaluate'
        if the_item in config:
            self.evaluate = config[the_item]
            
        the_item = "evalb"
        if the_item in config:
            self.evalb = config[the_item]
            
        the_item = "gold_dev_cons"
        if the_item in config:
            self.gold_dev_cons = config[the_item]

        the_item = "gold_dev_dep"
        if the_item in config:
            self.gold_dev_dep= config[the_item]

        the_item = "language"
        if the_item in config:
            self.language= (config[the_item])
            
        the_item = "cons2labels"
        if the_item in config:
            self.cons2labels = config[the_item]
            
        the_item = "dependency_parsing"
        if the_item in config:
            self.dependency_parsing = str2bool(config[the_item])

        the_item = "constituency_parsing"
        if the_item in config:
            self.constituency_parsing = str2bool(config[the_item])

        the_item = "gold_train_trees"
        if the_item in config:
            self.gold_train_trees = config[the_item]

        the_item = "index_of_main_tasks"
        if the_item in config:
            self.index_of_main_tasks = map(int,config[the_item].split(","))

        the_item = "language"
        if the_item in config:
            self.language = config[the_item]


def config_file_to_dict(input_file):
    config = {}
    fins = open(input_file,'r').readlines()
    for line in fins:
        if len(line) > 0 and line[0] == "#":
            continue
        if "=" in line:
            pair = line.strip().split('#',1)[0].split('=',1)
            item = pair[0]
            if item=="feature":
                if item not in config:
                    feat_dict = {}
                    config[item]= feat_dict 
                feat_dict = config[item]
                new_pair = pair[-1].split()
                feat_name = new_pair[0]
                one_dict = {}
                one_dict["emb_dir"] = None
                one_dict["emb_size"] = 10
                one_dict["emb_norm"] = False
                if len(new_pair) > 1:
                    for idx in range(1,len(new_pair)):
                        conf_pair = new_pair[idx].split('=')
                        if conf_pair[0] == "emb_dir":
                            one_dict["emb_dir"]=conf_pair[-1]
                        elif conf_pair[0] == "emb_size":
                            one_dict["emb_size"]=int(conf_pair[-1])
                        elif conf_pair[0] == "emb_norm":
                            one_dict["emb_norm"]=str2bool(conf_pair[-1])
                feat_dict[feat_name] = one_dict
            else:
                if item in config:
                    print("Warning: duplicated config item found: %s, updated."%(pair[0]))
                config[item] = pair[-1]                
    return config


def str2bool(string):
    if string == "True" or string == "true" or string == "TRUE":
        return True 
    else:
        return False
