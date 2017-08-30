#!/bin/bash
set -e
echo "Taking Backup for Brainlab"
export REPLYTO=noreply@sentinelcloud.com

if mysqldump --single-transaction --triggers --routines --events --hex-blob --complete-insert -h <db_hostname> -u <username> -p'<password>' --databases <database_name> > emsent_brainlabag.sql; then
   echo "Data base dump successfully taken"
else
   echo "ERROR while taking database dump" 1>&2
   exit 1
fi

echo "Taking Checksum for the db dump here"

md5sum emsent_brainlabag.sql > emsent_brainlabag.md5
echo "CHECKSUM COMPLETED"

echo "Now Zipping the file"

DATE=`date +%Y-%m-%d`

zip_name="emsent_brainlabag-"$DATE-".zip"

zip $zip_name emsent_brainlabag.md5 emsent_brainlabag.sql || echo "Error Occurred while ZIP"

echo "Before going inside for loop"
retries=3

cmd="curl -1 --cipher ALL --connect-timeout 90 -T $zip_name ftps://ftp.box.com/GemaltoLicenseBackup/$zip_name --user <ftp_username>:<ftp_password>"
retry_times=3
retry_wait=6
c=0
while [ $c -lt $((retry_times+1)) ]; do
        c=$((c+1))
        echo "Executing \"$cmd\", try $c"
        $cmd && return $?
        if [ ! $c -eq $retry_times ]; then
                echo "Something went Wrong, will retry in $retry_wait secs"
                sleep $retry_wait
        else
                echo "This email is being sent as a notifer of Failure. The EMS databases dump couldn't be uploaded to FTP box.com Server. Please contact Gemalto Support" | sudo -u noreply mail -s "Dump failed" "nishant704@gmail.com"
        fi
done

rm -rf emsent_brainlabag*
