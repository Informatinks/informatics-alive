return tonumber(redis.call('mget', 'submit.queue:last.put.id')[1]) -  tonumber(redis.call('mget', 'submit.queue:last.get.id')[1])
