
## 0.0.10

**new features**
* use enum for command names, status and ack

## 0.0.9

**new features**
* add sample code to readme

**bug-fixes**
* remove redundant cmd field from parsed data

## 0.0.8

**new features**
* wrap parsed data in data-class with error state/str, command-name and data
* add enable-values to setting parser

## 0.0.7

**bug-fixes**
* found overflow bit hack if charging current is greater than 25.5A

## 0.0.6

**new features**
* support multiple chargers, connected to one pc
* add support for modes: discharge, parallel
* add command to receive firmware version
* add command to receive device settings

## 0.0.5

**new features**
* working interface to t1000 via USB
* supported commands
    * read values of both ports (not all values interpreted yet)
    * start program
    * stop
