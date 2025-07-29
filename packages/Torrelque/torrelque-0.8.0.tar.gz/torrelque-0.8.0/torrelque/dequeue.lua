local dequeueing_key, working_key, task_key, state_key_prefix = unpack(KEYS)
local now = ARGV[1]
local working_status = ARGV[2]
local task_ids = {unpack(ARGV, 3)}

local function dequeue(
    dequeueing_key, working_key, task_key, state_key_prefix, task_id, now, working_status
)
    local removed = redis.call('LREM', dequeueing_key, 1, task_id)
    if removed == 0 then
        return {task_id, 'null'}
    end

    local task_data = redis.call('HGET', task_key, task_id)

    local state_key = state_key_prefix .. ':' .. task_id
    local task_timeout = redis.call('HGET', state_key, 'timeout')
    local stale = now + task_timeout
    redis.call('ZADD', working_key, stale, task_id)

    redis.call('HSET', state_key, 'last_dequeue_time', now)
    redis.call('HSET', state_key, 'status', working_status)
    redis.call('HINCRBY', state_key, 'dequeue_count', 1)

    return {task_id, task_data}
end

local result = {}
for i, task_id in ipairs(task_ids) do
    result[i] = dequeue(
        dequeueing_key, working_key, task_key, state_key_prefix, task_id, now, working_status
    )
end
return result
