#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from sklearn.datasets import load_boston   
from sklearn import preprocessing  
import tensorflow as tf  
import numpy as np
import time
from sklearn import cross_validation
from sklearn import metrics
from os import listdir
import os
from numpy import genfromtxt
config = tf.ConfigProto(
        device_count = {'GPU': 1},
        allow_soft_placement=True
    )
config.gpu_options.allocator_type = 'BFC'
config.gpu_options.per_process_gpu_memory_fraction = 0.90
def one_hot(y_):
    y_ = y_.reshape(len(y_))
    n_values = np.max(y_) + 1
    return np.eye(int(n_values))[np.array(y_, dtype=np.int32)]

def categoriser(y,lenght):
	_y = [] 
	for i in y:

		if i <= 6:
			_y = np.append( _y,[0], axis=0)
		elif 7<= i <=9:
			_y = np.append( _y,[1], axis=0)
		elif 10<= i <=12:
			_y = np.append( _y,[2], axis=0)
		elif 13<= i <=14:
			_y = np.append( _y,[3], axis=0)
		elif 15<= i <=18: ##i5
			_y = np.append( _y,[4], axis=0)
		else:
			_y = np.append( _y,[5], axis=0)
	return _y	


#############load data###############
length = 5000
time 			
boston = np.nan_to_num(genfromtxt('./data/combine6.csv', delimiter=','))  #find_csv_filenames(path) #oad_boston()
print boston.shape
x = preprocessing.scale(boston[0:length,1:41])
y = one_hot(categoriser(boston[0:length,42], x.shape[0]))[0:length]

X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(
x, y, test_size=0.2, random_state = 1)




total_len = X_train.shape[0]

print('X:',x.shape)# (506, 13)  
print('Y:',y.shape)  
print 'X-train:',X_train.shape,"Y-train ",Y_train.shape
print Y_train

BATCH_START = 0     # 建立 batch data 时候的 index  
TIME_STEPS = 1000     # backpropagation through time 的 time_steps  
BATCH_SIZE = 1000
INPUT_SIZE = 40    # sin 数据输入 size
OUTPUT_SIZE = 1     # cos 数据输出 size  
CELL_SIZE = 10      # RNN 的 hidden unit size  
LR = 0.001          # learning rate  
LAMEDA= 0.004
N_CLASSES =6
ATTENTION_SIZE = 20
n_steps = 1
no_fea = 40
n_classes = N_CLASSES
batch_size=BATCH_SIZE
nodes1 = 40#2 #taks 1 input
nodes2 = 40#2 #taks 1 input
nodes3 = 40#3 #taks 1 input

nodesjoin = 40
n_group=4


X_train1 =np.pad(X_train[:,[0,	1,	4,	5,	10,	11,	14,	21,	23, 30 ]],  ((0,0),(0,0)), 'constant', constant_values=1).reshape([BATCH_SIZE*n_group,n_steps,nodes1/n_steps])
X_train2 =np.pad(X_train[:,[15,	18,	24,	25,	26,	27,31,	32,	33,	35]], ((0,0),(0,0)), 'constant', constant_values=1).reshape([BATCH_SIZE*n_group,n_steps,nodes2/n_steps])
X_train3 =np.pad(X_train[:,[6,	7,	8,	9,	12,	13,	17,	29, 32,	38]], ((0,0),(0,0)), 'constant', constant_values=1).reshape([BATCH_SIZE*n_group,n_steps,nodes3/n_steps])
X_train =X_train.reshape([BATCH_SIZE*n_group,n_steps,no_fea/n_steps])


X_test1 =np.pad(X_test[:,[0,	1,	4,	5,	10,	11,	14,	21,	23, 30]],  ((0,0),(0,0)), 'constant', constant_values=1).reshape([BATCH_SIZE,n_steps,nodes1/n_steps])
X_test2 =np.pad(X_test[:,[15,	18,	24,	25,	26,	27,	32,	33,	35, 35]], ((0,0),(0,0)), 'constant', constant_values=1).reshape([BATCH_SIZE,n_steps,nodes2/n_steps])
X_test3 =np.pad(X_test[:,[6,	7,	8,	9,	12,	13,	17,	29, 32, 38]], ((0,0),(0,0)), 'constant', constant_values=1).reshape([BATCH_SIZE,n_steps,nodes3/n_steps])
X_test =X_test.reshape([BATCH_SIZE,n_steps,no_fea/n_steps])

train_fea =[]
train_fea1=[]
train_fea2=[]
train_fea3=[]
train_fea4=[]
train_fea5=[]
train_fea6=[]

for i in range(n_group):
    f =X_train[(0+batch_size*i):(batch_size+batch_size*i)]
    train_fea.append(f)
    f1 =X_train1[(0+batch_size*i):(batch_size+batch_size*i)]
    train_fea1.append(f1)
    f2 =X_train2[(0+batch_size*i):(batch_size+batch_size*i)]
    train_fea2.append(f2)
    f3 =X_train3[(0+batch_size*i):(batch_size+batch_size*i)]
    train_fea3.append(f3)

print "feature"
print (train_fea[0].shape)


train_label=[]
for i in range(n_group):
    f =Y_train[(0+batch_size*i):(batch_size+batch_size*i), :]
    train_label.append(f)
print "label"
print (train_label[0].shape)

feature_testing = X_test[:batch_size]
feature_testing1 =X_test[:batch_size]
feature_testing2 =X_test[:batch_size]
feature_testing3 =X_test[:batch_size]



label_testing =Y_test[:batch_size]




n_inputs = no_fea/n_steps  # MNIST data input (img shape: 11*99)
# n_steps =  # time steps
n_hidden1_task1 = nodes1   # neurons in hidden layer
n_hidden2_task1 = nodes1

n_hidden1_task2 = nodes2
n_hidden2_task2 = nodes2

n_hidden1_task3 = nodes3
n_hidden2_task3 = nodes3


n_hidden1_join = nodesjoin
# n_steps =  # time steps

xjoin = tf.placeholder(tf.float32, [None, n_steps, n_inputs]) #xs 有三个维度  
ys = tf.placeholder(tf.float32, [None, N_CLASSES]) #ys 有三个维度  
#task 1
x1 = tf.placeholder(tf.float32, [None, n_steps, n_inputs])
x2 = tf.placeholder(tf.float32, [None, n_steps, n_inputs])
x3 = tf.placeholder(tf.float32, [None, n_steps, n_inputs])



weights = {
# (28, 128)
'in_join': tf.Variable(tf.random_normal([n_inputs,n_hidden1_join]), trainable=True),
'n_hidden1_join': tf.Variable(tf.random_normal([n_hidden1_join, n_hidden1_join]), trainable=True),
# (28, 128)
'in_task1': tf.Variable(tf.random_normal([n_inputs+n_hidden1_join,n_hidden1_task1]), trainable=True),
'n_hidden1_task1': tf.Variable(tf.random_normal([n_hidden1_task1+n_hidden1_task1, n_hidden1_task1]), trainable=True),
#(128,128)
'in_task2': tf.Variable(tf.random_normal([n_inputs+n_hidden1_join,n_hidden1_task2]), trainable=True),
'n_hidden1_task2': tf.Variable(tf.random_normal([n_hidden1_task2+n_hidden1_task2, n_hidden1_task2 ]), trainable=True),

'in_task3': tf.Variable(tf.random_normal([n_inputs+n_hidden1_join,n_hidden1_task3]), trainable=True),
'n_hidden1_task3': tf.Variable(tf.random_normal([n_hidden1_task3+n_hidden1_task3, n_hidden1_task3 ]), trainable=True),

'out_task1': tf.Variable(tf.random_normal([n_hidden1_task1, n_classes]), trainable=True),
'out_task2': tf.Variable(tf.random_normal([n_hidden1_task2, n_classes]), trainable=True),
'out_task3': tf.Variable(tf.random_normal([n_hidden1_task3, n_classes]), trainable=True),
'out_task_join': tf.Variable(tf.random_normal([n_hidden1_task1, n_classes]), trainable=True),

}

biases = {
# (128, )
'in_task1': tf.Variable(tf.constant(0.1, shape=[n_hidden1_task1])),
'task1': tf.Variable(tf.constant(0.1, shape=[n_hidden2_task1 ])),

'in_task2': tf.Variable(tf.constant(0.1, shape=[n_hidden1_task2])),
'task2': tf.Variable(tf.constant(0.1, shape=[n_hidden1_task2])),

'in_task3': tf.Variable(tf.constant(0.1, shape=[n_hidden1_task3])),
'task3': tf.Variable(tf.constant(0.1, shape=[n_hidden1_task3])),

'in_join': tf.Variable(tf.constant(0.1, shape=[n_hidden1_join])),
'join': tf.Variable(tf.constant(0.1, shape=[n_hidden1_join])),

# (10, )
'out_task1': tf.Variable(tf.constant(0.1, shape=[n_classes ]), trainable=True),
'out_task2': tf.Variable(tf.constant(0.1, shape=[n_classes ]), trainable=True),
'out_task3': tf.Variable(tf.constant(0.1, shape=[n_classes ]), trainable=True),
'out_task_join': tf.Variable(tf.constant(0.1, shape=[n_classes]), trainable=True)
}
keep_prob = tf.placeholder(tf.float32)

def attention(inputs, attention_size, time_major=False, return_alphas=False):

	if time_major:# (T,B,D) => (B,T,D)
		inputs = tf.transpose(inputs, [1, 0, 2])
	#print "input",tf.eval(inputs.shape[2])
	hidden_size = inputs.shape[2].value  # D value - hidden size of the RNN layer
	batch_szie = inputs.shape[0].value
	time_step= inputs.shape[1].value

    # Trainable parameters
	W_omega = tf.Variable(tf.random_normal([hidden_size, attention_size], stddev=0.1))
	b_omega = tf.Variable(tf.random_normal([attention_size], stddev=0.1))
	u_omega = tf.Variable(tf.random_normal([attention_size], stddev=0.1))

	print "attent Shape",inputs.shape,"w_omega",W_omega.shape
	v = tf.tanh(tf.tensordot(tf.reshape(inputs,[batch_szie,hidden_size] ), W_omega, axes = [[1], [0]]) + b_omega)

	print "input",b_omega.shape
	print "",v.shape
    # For each of the timestamps its vector of size A from `v` is reduced with `u` vector
	vu = tf.tensordot(v, u_omega, axes = [[1], [0]])   # (B,T) shape
	alphas = tf.nn.softmax(vu)              # (B,T) shape also
	print "=========shape:",inputs.shape,alphas.shape
	output = tf.reduce_sum(inputs* tf.expand_dims(alphas, -1), 1)
	output = tf.reshape(output,[batch_szie,time_step,hidden_size])
	#print "input",inputs.shape,output.shape,alphas.shape
	if not return_alphas:
		return output
	else:
		return output, alphas

def RNN(xjoin, x1, x2, x3, weights, biases, keep_prob ):#:x4, x5, x6, weights, biases):
    # hidden layer for input to cell
    ########################################

    # transpose the inputs shape from
    # X ==> (128 batch * 28 steps, 28 inputs)
    #X = tf.reshape(X, [-1, n_inputs])
	X_join = tf.reshape(xjoin, [-1, n_inputs])
	X1 = tf.reshape(x1, [-1, n_inputs])
	X2 = tf.reshape(x2, [-1, n_inputs])
	X3 = tf.reshape(x3, [-1, n_inputs])


    # into hidden
    # X_in = (128 batch * 28 steps, 128 hidden)
    #X_hidd1 = tf.sigmoid(tf.matmul(X, weights['in']) + biases['in'])
	#print "asdasdasd",X_join.shape,X1.shape,X2.shape,X3.shape,X4.shape,X5.shape,X6.shape
	X_hidd1_join = tf.sigmoid(tf.matmul(X_join, weights['in_join']) + biases['in_join'])
	X_hidd1_task1 = tf.sigmoid(tf.matmul(tf.concat([X1,X_hidd1_join],axis=1), weights['in_task1']) + biases['in_task1'])
	X_hidd1_task2 = tf.sigmoid(tf.matmul(tf.concat([X2,X_hidd1_join],axis=1), weights['in_task2']) + biases['in_task2'])
	X_hidd1_task3 = tf.sigmoid(tf.matmul(tf.concat([X3,X_hidd1_join],axis=1), weights['in_task1']) + biases['in_task1'])
	print X2.shape, X_hidd1_join.shape 

    # X_hidd1 = tf.matmul(X, weights['in']) + biases['in']
    #X_hidd2 = tf.matmul(X_hidd1, weights['hidd2']) + biases['hidd2']
	X_hidd2_join = tf.matmul(X_hidd1_join, weights['n_hidden1_join']) + biases['join']
	print "asdasdasd",X_hidd2_join.shape,X_hidd1_task1.shape
	X_hidd2_task1 = tf.matmul(tf.concat([X_hidd1_task1,X_hidd2_join],axis=1), weights['n_hidden1_task1']) + biases['task1']
	X_hidd2_task2 = tf.matmul(tf.concat([X_hidd1_task2,X_hidd2_join],axis=1), weights['n_hidden1_task2']) + biases['task2']
	X_hidd2_task3 = tf.matmul(tf.concat([X_hidd1_task3,X_hidd2_join],axis=1), weights['n_hidden1_task1']) + biases['task1']

	X_taskjoin = tf.reshape(X_hidd2_join, [-1, n_steps, n_hidden1_join])
	X_task1 = tf.reshape(X_hidd2_task1, [-1, n_steps, n_hidden1_task1])
	X_task2 = tf.reshape(X_hidd2_task2, [-1, n_steps, n_hidden1_task2])
	X_task3 = tf.reshape(X_hidd2_task3, [-1, n_steps, n_hidden1_task3])

    # shared cell
    ##########################################
	lstm_cell_share = tf.contrib.rnn.BasicLSTMCell(n_hidden1_join, forget_bias=1, state_is_tuple=True)
	init_statejoin = lstm_cell_share.zero_state(batch_size, dtype=tf.float32)
	with tf.variable_scope('lstmshare'):
		outputsjoin, final_state1 = tf.nn.dynamic_rnn(lstm_cell_share, X_taskjoin, initial_state=init_statejoin, time_major=False)
	outputsjoin = tf.unstack(tf.transpose(outputsjoin, [1, 0, 2]))
	outputsjoin=outputsjoin[-1]

	X_hidd2_task1=tf.stack((X_hidd2_task1,outputsjoin))
	X_hidd2_task2=tf.stack((X_hidd2_task2,outputsjoin))
	X_hidd2_task3=tf.stack((X_hidd2_task3,outputsjoin))

	##########################################

	# basic LSTM Cell.
	# lstm_cell_join = tf.contrib.rnn.BasicLSTMCell(n_hidden1_join, forget_bias=1, state_is_tuple=True)
	lstm_cell_11 = tf.contrib.rnn.BasicLSTMCell(n_hidden1_task1, forget_bias=1, state_is_tuple=True)
	lstm_cell_12 = tf.contrib.rnn.BasicLSTMCell(n_hidden1_task1, forget_bias=1, state_is_tuple=True)

	lstm_cell_21 = tf.contrib.rnn.BasicLSTMCell(n_hidden1_task2, forget_bias=1, state_is_tuple=True)	
	lstm_cell_22 = tf.contrib.rnn.BasicLSTMCell(n_hidden1_task2, forget_bias=1, state_is_tuple=True)

	lstm_cell_31 = tf.contrib.rnn.BasicLSTMCell(n_hidden1_task3, forget_bias=1, state_is_tuple=True)	
	lstm_cell_32 = tf.contrib.rnn.BasicLSTMCell(n_hidden1_task3, forget_bias=1, state_is_tuple=True)


	lstm_cell1 = tf.contrib.rnn.MultiRNNCell([lstm_cell_11, lstm_cell_12], state_is_tuple=True)
	lstm_cell2 = tf.contrib.rnn.MultiRNNCell([lstm_cell_21, lstm_cell_22], state_is_tuple=True)
	lstm_cell3 = tf.contrib.rnn.MultiRNNCell([lstm_cell_31, lstm_cell_32], state_is_tuple=True)

	init_state1 = lstm_cell1.zero_state(batch_size, dtype=tf.float32)
	init_state2 = lstm_cell2.zero_state(batch_size, dtype=tf.float32)
	init_state3 = lstm_cell3.zero_state(batch_size, dtype=tf.float32)
	with tf.variable_scope('lstm1'):
		outputs1, final_state1 = tf.nn.dynamic_rnn(lstm_cell1, X_task1, initial_state=init_state1, time_major=False)
		outputs1 = tf.nn.dropout(outputs1, keep_prob)
	with tf.variable_scope('lstm2'):
		outputs2, final_state2 = tf.nn.dynamic_rnn(lstm_cell2, X_task2, initial_state=init_state2, time_major=False)
		outputs2 = tf.nn.dropout(outputs2, keep_prob)
	with tf.variable_scope('lstm3'):
		outputs3, final_state2 = tf.nn.dynamic_rnn(lstm_cell3, X_task3, initial_state=init_state3, time_major=False)
		outputs3 = tf.nn.dropout(outputs3, keep_prob)

	merge = tf.concat([outputs1, outputs2,outputs3], axis=1)  #,  outputs4,outputs5, outputs6], axis=0)


	outputs = tf.nn.dropout(merge, keep_prob)
	outputs = tf.unstack(tf.transpose(merge, [1, 0, 2]))#attention_output, [1, 0, 2])) #outputs, [1, 0, 2]))    # states is the last outputs
	results = tf.matmul(outputs[-1], weights['out_task_join']) + biases['out_task_join']

	return results# , attention_output

pred = RNN(xjoin, x1, x2, x3, weights, biases, keep_prob)#, attention = RNN(xjoin, x1, x2, x3, weights, biases)#x4, x5, x6, weights, biases)

lr=LR
lamena = LAMEDA
l2 = lamena * sum(tf.nn.l2_loss(tf_var) for tf_var in tf.trainable_variables())  # L2 loss prevents this overkill neural network to overfit the data
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=ys))+l2  # Softmax loss

# tf.scalar_summary('loss', cost)
train_op = tf.train.AdamOptimizer(lr).minimize(cost)
pred_result =tf.argmax(pred, 1)
label_true =tf.argmax(ys, 1)
correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(ys, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
softmaxed_logits = tf.nn.softmax(pred)
auc_update_op = tf.contrib.metrics.streaming_auc(softmaxed_logits,
							  labels=ys,
                              weights=1,
                              curve='ROC')


init = tf.global_variables_initializer(), tf.local_variables_initializer()

with tf.Session(config=config) as sess:
    sess.run(init)

    saver = tf.train.Saver()
    step = 0
    start = time.clock()
    while step < 1000:# 1500 iterations
        for i in range(n_group):
        	#print train_fea[i].shape
        	#print train_label[i].shape
        	sess.run(train_op, feed_dict={
        		xjoin: train_fea[i], 
        		x1: train_fea1[i], 
        		x2: train_fea2[i], 
        		x3: train_fea3[i], 
                ys: train_label[i],
                keep_prob: 0.2
                })
        print i
		
        if step  != 0:
            hh, y_pred, soft_logits, score =sess.run([accuracy, pred_result, auc_update_op,  softmaxed_logits], feed_dict={
                xjoin: feature_testing,
        		x1: feature_testing1,
        		x2: feature_testing2, 
        		x3: feature_testing3, 
                ys: label_testing,
                keep_prob: 0.2
                })
            label_true = np.argmax(label_testing, 1)
            fpr = dict()
            tpr = dict()
            roc_auc = dict()

            print "validation accuracy:", hh
            print("The lamda is :",lamena,", Learning rate:",lr,", The step is:",step)
            print "Precision", metrics.precision_score(label_true, y_pred ,average=None)
            print "Recall", metrics.recall_score(label_true,y_pred,average=None)
            print '\n clasification report:\n', metrics.classification_report(label_true,y_pred, digits=6)
            print metrics.confusion_matrix(label_true, y_pred)
            print "f1_score", metrics.f1_score(label_true, y_pred,average=None)
            print "ROC", soft_logits
            for i in range(N_CLASSES):
            	fpr[i], tpr[i], _ = metrics.roc_curve(label_testing[:, i], score[:, i])
            	roc_auc[i] = metrics.auc(fpr[i], tpr[i])
            for i in range(N_CLASSES):
            	print "auc",(metrics.auc(fpr[i], tpr[i]))
            if hh >0.94:
            	break
            print("The cost is :",sess.run(cost, feed_dict={

                xjoin: feature_testing,
        		x1: feature_testing1,
        		x2: feature_testing2, 
        		x3: feature_testing3, 
                ys: label_testing,
                keep_prob: 0.2
            }))
        step += 1
    endtime=time.clock()

    print "run time:", endtime-start
