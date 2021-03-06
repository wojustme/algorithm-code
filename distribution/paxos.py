import time
import threading



threadLock = threading.Lock()

def singleton(cls, *args, **kw):
  instances = {}

  def _singleton():
    if cls not in instances:
      instances[cls] = cls(*args, **kw)
    return instances[cls]

  return _singleton


@singleton
class Accpetor(object):
  '''
  paxos参与者
  有两个成员变量缓存数据
  eg:
    [accepted_epoch, accepted_value]  =>  当前的epoch的序列号, 当前的值
    lastest_prepared_epoch            =>  上一次获得的epoch的序列号
  '''
  accepted_tupple = [0, None]
  lastest_prepared_epoch = 0
  def __init__(self):
    self.name = '1'
  def __str__(self):
    return 'accepted: ' + str(self.accepted_tupple[0]) + ' -> ' + str(self.accepted_tupple[1]) + '\nlastest_prepared_epoch: ' + str(self.lastest_prepared_epoch) +'\n'
  def prepareProposer(self, epoch_id, value):
    '''
    准备阶段
    :param epoch_id:
    :return:
    '''
    threadLock.acquire()
    curr_lastest_prepared_epoch = self.lastest_prepared_epoch
    curr_msg = self.accepted_tupple
    reply_msg =('', curr_msg[0] , curr_msg[1])
    if curr_lastest_prepared_epoch == 0:
      # 表示该Acceptor还没有接受任何Proposer
      if epoch_id > curr_lastest_prepared_epoch:
        print('acceptor 已经完成准备阶段, 将要变成', epoch_id, value)
        reply_msg = ('acceptor 已经完成准备阶段。。。', curr_msg[0], curr_msg[1])
        self.lastest_prepared_epoch = epoch_id
    else:
      # 表示该Acceptor已经接受过了Proposer
      if curr_msg[1] != None:
        # 表示该Acceptor已经成功设置过值了
        reply_msg = ('acceptor 已经存在值。', curr_msg[0] , curr_msg[1])
        if epoch_id >= curr_lastest_prepared_epoch:
          self.lastest_prepared_epoch = epoch_id
      else:
        # 表示该Acceptor还未设置值
        if epoch_id >= curr_lastest_prepared_epoch:
          reply_msg = ('acceptor 刚刚被设置值: ', epoch_id , value)
          print('将要变换的真实情况: ', reply_msg, '; 之前值为:', curr_msg[0] , curr_msg[1])
          self.lastest_prepared_epepoch_idoch = epoch_id
          self.accepted_tupple = [epoch_id, value]
        else:
          reply_msg = ('该epoch_id过小，设置失败。。。', curr_msg[0] , curr_msg[1])
          print('将要变换的真实情况: 此时最后一个触发的epoch_id: ', curr_lastest_prepared_epoch, ' 而此时的epoch_id: ', epoch_id)

    threadLock.release()
    return reply_msg

class Proposer(object):
  def __init__(self):
    self.acceptor = Accpetor()

  def setAcceptor(self, epoch_id):

    reply_msg = self.acceptor.prepareProposer(epoch_id, '32')
    print(reply_msg)
    while (reply_msg[0] == 'acceptor 已经完成准备阶段。。。' or reply_msg[0] == ''):
      reply_msg = self.acceptor.prepareProposer(epoch_id, '32')
    print(reply_msg)


def setAcceptor(proposer, i):
  time.sleep(1)
  proposer.setAcceptor(i)


if __name__ == '__main__':
  a = Accpetor()
  proposer_list = []
  for i in range(10):
    proposer_list.append(Proposer())
  thread_list = []
  list_len = len(proposer_list)
  for i in range(list_len):
    sthread = threading.Thread(target = setAcceptor, args = (proposer_list[i], i))
    sthread.start()
    thread_list.append(sthread)


