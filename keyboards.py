keyboard = {
  "one_time": False,
  "buttons":[
    [
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"2\"}",
          "label":"&#10084;"
        },
        "color":"positive"
      },
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"1\"}",
          "label":"&#128078;"
        },
        "color":"negative"
      },
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"2\"}",
          "label":"&#11088;"
        },
        "color":"primary"
      },
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"2\"}",
          "label":"Next"
        },
        "color":"secondary"
      }
    ]
  ]
}
keyboard_start = {
  "one_time": True,
  "buttons":[
    [
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"1\"}",
          "label": "Start"
        },
        "color":"primary"
      }
    ]
  ]
}