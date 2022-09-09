#!/bin/bash

set -e

# Add all users found in user-tokens.txt
# echo "Attempting to add users from /etc/users/user-tokens.txt"
# while read -r line
# do
#     echo "Processing user line $line"
#     IFS=: read user email token <<< $line
#     echo "Parsed user=$user email=$email token=$token"
#
#     echo "Creating temp file for user $user"
#     temp_file=$(mktemp)
#
#     echo "Creating user ldif at $temp_file"
#     echo "dn: cn=$user,dc=test,dc=ldap,dc=com" >> $temp_file
#     echo "objectClass: inetOrgPerson" >> $temp_file
#     echo "cn: ${user^^}" >> $temp_file
#     echo "mail: $email" >> $temp_file
#     echo "uid: $user" >> $temp_file
#     echo "sn: $user" >> $temp_file
#
#     echo "Adding user to ldap"
#     ldapadd -c -x -H ldap://ldap:1389 -D "cn=admin,dc=test,dc=ldap,dc=com" -w admin -f $temp_file || true
#
#     mkdir -p /cache/slurmrestd
#     cache_filename="/cache/slurmrestd/$user.token"
#     echo "Creating cached user token at $cache_filename"
#     echo $token > $cache_filename
#
#     echo "Finished processing $userfile"
# done < /etc/users/user-tokens.txt
# echo "Finished processing /etc/users/user-tokens.txt"

while true
do
    echo "Executing agent in loop"
    python3 cluster_agent/main.py
    echo "Sleeping for 15 seconds"
    sleep 15
done
