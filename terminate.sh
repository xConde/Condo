#!/bin/bash

kill $(ps aux | grep 'bot.py' | awk '{print $2}')
