local pending_key, dequeueing_key, undequeued_key = unpack(KEYS)
local working_key, delayed_key, state_key_prefix = unpack(KEYS, 4)
local now = ARGV[1]
local pending_status = ARGV[2]

local function requeue_timed(pending_key, target_key, state_key_prefix, now, pending_status)
    local task_ids = redis.call('ZRANGEBYSCORE', target_key, 0, now)
    if #task_ids == 0 then
        return 0
    end

    redis.call('LPUSH', pending_key, unpack(task_ids))
    redis.call('ZREM', target_key, unpack(task_ids))

    local state_key
    for _, task_id in ipairs(task_ids) do
        state_key = state_key_prefix .. ':' .. task_id
        redis.call('HSET', state_key, 'last_requeue_time', now)
        redis.call('HSET', state_key, 'status', pending_status)
        redis.call('HINCRBY', state_key, 'requeue_count', 1)
    end

    return #task_ids
end

local function requeue_undequeued(dequeueing_key, undequeued_key, pending_key)
    local dequeueing_task_ids = redis.call('LRANGE', dequeueing_key, 0, -1)

    -- empty dequeueing list means that previous undequeued ids are dequeued
    if #dequeueing_task_ids == 0 then
        redis.call('DEL', undequeued_key)
        return 0
    end

    -- get and remove undequeued tasks still present from previous call, and get new ones
    local old_undequeued_task_ids = {}
    local new_undequeued_task_ids = {}
    local task_id
    for i = #dequeueing_task_ids, 1, -1 do
        task_id = dequeueing_task_ids[i]
        if redis.call('SISMEMBER', undequeued_key, task_id) == 1 then
            redis.call('LREM', dequeueing_key, 1, task_id)
            table.insert(old_undequeued_task_ids, task_id)
        else
            table.insert(new_undequeued_task_ids, task_id)
        end
    end

    -- requeue undequeued tasks from previous run
    if #old_undequeued_task_ids > 0 then
        redis.call('LPUSH', pending_key, unpack(old_undequeued_task_ids))
    end

    -- recreate undequeued list
    redis.call('DEL', undequeued_key)
    if #new_undequeued_task_ids > 0 then
        redis.call('SADD', undequeued_key, unpack(new_undequeued_task_ids))
    end

    return #old_undequeued_task_ids
end

return {
    requeue_timed(pending_key, working_key, state_key_prefix, now, pending_status),
    requeue_timed(pending_key, delayed_key, state_key_prefix, now, pending_status),
    requeue_undequeued(dequeueing_key, undequeued_key, pending_key),
}
