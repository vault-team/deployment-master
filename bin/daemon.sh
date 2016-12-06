#!/usr/bin/env bash

export VAULT_DM_HOME="$(cd "`dirname "$0"`"/..; pwd)"
cd $VAULT_DM_HOME

LOG_HOME=$VAULT_DM_HOME/log
LOG_API_LOG=$LOG_HOME/api.log
LOG_SYS_LOG=$LOG_HOME/sys.log

PID_API_LOG=$LOG_HOME/api.pid
PID_SYS_LOG=$LOG_HOME/sys.pid

#set search path
export PYTHONPATH=$PYTHONPATH:$VAULT_DM_HOME

# Function to delete pid in file
kill_process_by_pid_file () {
    pid_file=$1
    target_pid="$(cat $pid_file)"
    kill "$target_pid"
    rm -f "$pid_file"
}

if [ "$1" == "start" ]
then
    # start api and system monitor and
    if [ -f $PID_API_LOG ] || [ -f $PID_SYS_LOG ] ; then
        echo "please stop vault first"
    else
        echo "starting vault....."
        nohup python $VAULT_DM_HOME/service_management_api/api.py --home_dir $VAULT_DM_HOME >> "$LOG_API_LOG" 2>&1 < /dev/null &
        echo $! > "$PID_API_LOG"
        nohup python $VAULT_DM_HOME/deployment_master/main.py --home_dir $VAULT_DM_HOME >> "$LOG_SYS_LOG" 2>&1 < /dev/null &
        echo $! > "$PID_SYS_LOG"
    fi
elif [ "$1" == "stop" ]
then
    echo "stopping vault....."
    kill_process_by_pid_file $PID_API_LOG
    kill_process_by_pid_file $PID_SYS_LOG
else
    echo "daemon.sh [start | stop]"
fi