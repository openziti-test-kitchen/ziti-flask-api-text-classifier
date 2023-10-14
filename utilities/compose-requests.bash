set -euo pipefail
declare -i OFFENSIVE=0 NOTOFFENSIVE=0
for i in {0..99}
do
  # TEXT="$(fortune -a /usr/share/games/fortunes/off | tr '\n\r\v\f' ' ')"
  TEXT="$(fortune -o | tr '\n\r\v\f' ' ')"
  REQUEST="$(
    jq  --null-input \
        --compact-output \
        --arg text "$TEXT" \
        '{"text": $text}'
  )"
  PREDICTION=$(curl -sSf \
    --request POST \
    --header 'content-type: application/json' \
    --data "$REQUEST" \
    127.0.0.1:5000/api/v1/classify \
    | jq --raw-output '.[0].label'
  )
  if [[ -z "$PREDICTION" ]]; then
    echo "ERROR: no prediction for '$TEXT'" >&2
    exit 1
  elif [[ $PREDICTION == Offensive ]]; then
    echo "$i: Offensive? $TEXT"
    OFFENSIVE+=1
  else
    # echo "$i: Not Offensive? $TEXT"
    NOTOFFENSIVE+=1
  fi
done

echo "Offensive: $OFFENSIVE"
echo "Not Offensive: $NOTOFFENSIVE"
