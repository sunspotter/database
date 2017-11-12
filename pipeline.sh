#!/usr/bin/bash

# This script clean and ingests the data into a
# sqlite database.
# NOTE: Files are going to be replicated and depending
# of their size you may get your disk full.

function usage {
    cat << EOF
Usage: $0 <classifications.csv> <rankings.csv>
Prepares the classifications and rankings files and
includes them into a database: sunspotter.sqlite3
EOF
    exit 1
}

if [ ! $# -eq 2 ]; then
    usage;
fi

master_start=$SECONDS
DIR=$(dirname "$0")

# 0. Define variables of files
classifications=$1
classifications_noRep=classifications_noRepeated.csv
rankings_orig=$2
rankings=rankings.csv

cp ${rankings_orig} ${rankings}

########### 1. Remove repeated
start=$SECONDS
awk '!($0 in a) {a[$0];print}' ${classifications}   > ${classifications_noRep}
duration=$(( SECONDS - start ))
lines_removed=$(($(wc -l ${classifications} | cut -f1 -d' ') - $(wc -l  ${classifications_noRep} | cut -f1 -d' ')))
echo "Removing duplicates took $duration seconds"
echo "                    and removed ${lines_removed} lines."

## 1.b Headers with #  ** BETTER AT THE END **
## sed -i '1 s/^/#/' ${rankings}
## sed -i '1 s/^/#/' ${classifications_noRep}

########### 2. Remove URLs
start=$SECONDS
sed -i -e 's|http://www.sunspotter.org/subjects/standard/||g' "${classifications_noRep}"
sed -i -e 's|http://www.sunspotter.org/subjects/standard/||g' "${rankings}"
duration=$(( SECONDS - start ))
echo "Removing URLs took $duration seconds"


########### 3. Change column separator from ',' to ';' so it doesn't conflict with the position or date
start=$SECONDS
sed -i -e 's/","/";"/g' "${rankings}"
sed -i -e 's/","/";"/g' "${classifications_noRep}"
duration=$(( SECONDS - start ))
echo "Formatting with ';' took $duration seconds"

########### 4. Change true/false for 1/0
start=$SECONDS
sed -i -e 's/true/1/g' -e 's/false/0/g' "${rankings}"
sed -i -e 's/true/1/g' -e 's/false/0/g' "${classifications_noRep}"
duration=$(( SECONDS - start ))
echo "Change true/false to 1/0 took $duration seconds"

## ########### 5. Print column order and field from header # NOTE: Only to know fields for next steps
## awk 'BEGIN{ FS=";" } { for(fn=1;fn<=NF;fn++) {print fn" = "$fn;}; exit; }' "${rankings}"
## awk 'BEGIN{ FS=";" } { for(fn=1;fn<=NF;fn++) {print fn" = "$fn;}; exit; }' "${classifications_noRep}"

########### 5.a Extract fits filenames($20) and dates($17), they should be unique 1 to 1
start=$SECONDS
awk -F';' '{OFS=";"; print $17,$20}' ${rankings} | sort |  uniq | # Prints the time and filename, sort them and get unique files
    sed -e '$d' -e '=' | sed 'N;s/\n/\t/' |                       # delete last line and number them in the same line
    sed 's/;/ /g' |                                               # remove ";"
    awk '{OFS=";"; print $1,$2,$3}' > lookup_timesfits.csv        # print id, date, file and save it into lookup file.

sed -i '1i\"id_filename";"date";"filename"' lookup_timesfits.csv  # add heading to lookup file

# magic to use the lookup table and change it for the id of the filenames;
# http://www.unix.com/shell-programming-and-scripting/60653-search-replace-string-file1-string-lookup-table-file2.html
# ./understand_awk
awk -F';' 'FNR==NR{a[$3]=$1;next} {OFS=";"; $20=a[$20]; print}' lookup_timesfits.csv ${rankings} |
    cut -d";" -f-16,18- > ${rankings}_2                           # remove column 17 (ie. date)

# Rename the final file back to rankings.
mv ${rankings}_2 ${rankings}
duration=$(( SECONDS - start ))
echo "Create look up table and update rankings took $duration seconds"

########### 5.b Extract images(jpg) and properties for lookup
start=$SECONDS
cut -d";" -f-2,7- ${rankings} |                   # Extract the columns that we want (no ranking info)
    awk 'NR<2{print $0; next}{print $0|"sort"}' | # sort all lines except the first one (NR<2)
    awk 'NR<2{OFS=";"; print "\"id_image\"",$0; next}{OFS=";"; print NR-1,$0}'  > lookup_properties.csv # print the id for each file
duration=$(( SECONDS - start ))
echo "Create look up properties table took $duration seconds"

########### 5.b1 Convert rankings into [id_ranking, id_image, properties ranking]
start=$SECONDS
cut -d";" -f1,3-6 ${rankings} > ${rankings}_2
awk -F';' 'FNR==NR{a[$2]=$1;next} {OFS=";"; $1=a[$1]; print}' lookup_properties.csv ${rankings}_2 |
    awk 'NR<2{OFS=";"; print "\"id_rank\"",$0; next}{OFS=";"; print NR-1,$0}'  > ${rankings}
duration=$(( SECONDS - start ))
echo "Update rankings to use lookup table took $duration seconds"

########### 5.c Convert poss into pos_x and pos_y (for hc and px)
start=$SECONDS
sed -i '1!b;s/"\(..\)pos"/"\1pos_x";"\1pos_y"/g' lookup_properties.csv
sed -i -e 's/"\[/"/g' -e 's/,/";"/g' -e 's/\]"/"/g' -e 's/ //g' lookup_properties.csv
duration=$(( SECONDS - start ))
echo "Update positions in lookup table as two fields took $duration seconds"


########### 6 write classifications with the lookup tables
########### 6.a remove the redundant columns:
###############      filename_0 (5), sszn_0 (6), date_0 (7), filename_1 (9), sszn_1 (10), date_1 (11)
start=$SECONDS
cut -d';' -f-4,8,12- ${classifications_noRep} > ${classifications_noRep}_2
sed -i '1!b;s/image_0/image/' ${classifications_noRep}_2
awk -F';' 'FNR==NR{a[$2]=$1;next} {OFS=";"; $4=a[$4]; print}' lookup_properties.csv ${classifications_noRep}_2 > ${classifications_noRep}_3
sed -i '1!b;s/id_image/id_image_0/;s/image_1/image/' ${classifications_noRep}_3
awk -F';' 'FNR==NR{a[$2]=$1;next} {OFS=";"; $5=a[$5]; print}' lookup_properties.csv ${classifications_noRep}_3 > ${classifications_noRep}
sed -i '1!b;s/"id_image"/"id_image_1"/' ${classifications_noRep}
duration=$(( SECONDS - start ))
echo "Remove redundant columns on classification and update images to lookup took $duration seconds"

########### 6.b create user lookup table
start=$SECONDS
awk -F';' '{if (!seen[$3]++) print $3}' ${classifications_noRep} |
    awk 'NR<2{OFS=";"; print "\"id_user\"",$0; next}{OFS=";"; print NR-1,$0}' > lookup_users.csv
awk -F';' 'FNR==NR{a[$2]=$1;next} {OFS=";"; $3=a[$3]; print}' lookup_users.csv ${classifications_noRep} >  ${classifications_noRep}_2
# add integer ids to the classifications
awk 'NR<2{OFS=";"; print "\"id_classification\"",$0; next}{OFS=";"; print NR-1,$0}' ${classifications_noRep}_2  > ${classifications_noRep}
# remove spaces in names
sed -i -e 's/ /_/g' lookup_users.csv
# Change classifications language with long caracters
sed -i -e 's|./translations\(\/[a-zA-Z0-9]*-*[a-zA-Z0-9]*.json\)|--|g' ${classifications_noRep}
# echo '======== is this regex working? ========='
# grep 'trans' ${classifications_noRep} | wc -l
duration=$(( SECONDS - start ))
echo "Create user lookup table and update classifications took $duration seconds"

########### 7 deleting intermediate files
rm ${classifications_noRep}_2 ${classifications_noRep}_3 ${rankings}_2

########### 8 update tables with astropy
start=$SECONDS
echo "Updating tables - python -- This takes approx 30 min"
python ../database/update_tables.py
# echo '======== is the filling in astropy working? ========='
# grep ',,' classifications_noRepeated.csv| wc -l
duration=$(( SECONDS - start ))
echo "Create user lookup table and update classifications took $duration seconds"

########### 9 remove headers of the files otherwise sqlite3 missunderstand it
start=$SECONDS
files=( lookup_users.csv lookup_timesfits.csv lookup_properties.csv
        ${classifications_noRep} ${rankings} )
for i in ${files[@]}; do sed -i '1d' ${i}; done

# remove entries in classifications that does not contain values...
sed -i '/;;/d' ${classifications_noRep}
duration=$(( SECONDS - start ))
echo "Remove files non-classifications took $duration seconds"


########### 10 insert all into databse
start=$SECONDS
sqlite3 sunspotter.sqlite3 < ${DIR}/create_tables.sql
duration=$(( SECONDS - start ))
echo "Insert data into the sqlite database took $duration seconds"

########### 11 Create square plot
start=$SECONDS
sqlite3 sunspotter.sqlite3 <<EOF
.headers on
.mode csv
.output amount_user.csv
select u.username, count(*) as total from classification as c inner join user as u on u.id = c.user_id group by c.user_id order by total desc;
EOF
duration=$(( SECONDS - start ))
echo "Query db took $duration seconds"

python ${DIR}/square.py amount_user.csv

duration=$(( SECONDS - master_start ))
echo "The whole script took $duration seconds"
