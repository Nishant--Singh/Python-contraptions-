echo "Pushing json file to index"
epoch=`date +%Y.%m.%d-%H:%M:%S`
curl -XPOST -i localhost:9200/devops-$epoch/ -d '{
"settings" : {
    "number_of_shards" : 1
},
"mappings" : {
    "_default_":{
        "_timestamp" : {
            "enabled" : true,
            "store" : true
        }
    }
  }
}'

curl -XPOST -i localhost:9200/devops-$epoch/employee?fields=_timestamp -d  @/home/ubuntu/SQS_PULL/download.json
