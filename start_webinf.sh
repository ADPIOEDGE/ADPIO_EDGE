#!/run/current-system/sw/bin/bash
LOCAL="${0%/*}/ADPIO_EDGE_WEB_INF"


echo $LOCAL
cd $LOCAL && npm install && npm run dev
