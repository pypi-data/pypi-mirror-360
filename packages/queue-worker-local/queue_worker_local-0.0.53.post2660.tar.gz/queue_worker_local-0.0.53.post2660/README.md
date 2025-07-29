# Queue Worker

The Queue Worker is a Python script designed to execute tasks from a queue with specified parameters.  
It allows you to control the delay between task executions and choose which action IDs to process.

This README provides instructions on how to use the Queue Worker.

## Preparation Steps

- Ensure the desired action is listed in the `action_table` within the `action` database.
- If not, add `filename` (e.g., `send_message.py`), `function_module` (e.g., `SendSMS` or leave it null),
  and `function_name` (e.g., `send_sms`) to the `action_table`.
- Note that the Queue Worker currently only handles Python functions. For other languages, please create a Jira issue.

## Usage

```shell
python queue_worker.py -min_delay_after_execution_ms <min_interval> -max_delay_after_execution_ms <max_interval> -action_ids <action_ids>
```

Replace `<min_interval>, <max_interval>` with the min and time in milliseconds, and `<action_ids>` with the list of
action IDs you want to execute.

### Example:

Here's an example of how to use the Queue Worker with custom parameters:

```shell
python queue_worker.py -min_delay_after_execution_ms 0.5 -max_delay_after_execution_ms 1.2 -action_ids 1 2 4
```

This command will start the Queue Worker with a minimum delay of 0.5 milliseconds between executions, a maximum delay of
1.2 milliseconds, and it will process action IDs 1, 2, and 4.

### Default Flags

The Queue Worker has default settings for some parameters:

- `-processes 1`: By default, it runs in a single process. You can specify a different number of processes if needed.
- `-total_missions inf`: By default, it processes an infinite number of missions. You can limit the total number of
  missions if necessary.
  Feel free to adjust these flags according to your requirements when running the script.

That's it! You can now use the Queue Worker to efficiently manage and execute tasks from your queue with customized
settings.

# Permissions for Queue Worker

# Permissions for each action

TODO One of the actions need INSERT to profile_table, which?<br>
