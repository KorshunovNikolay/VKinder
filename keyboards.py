keyboard = {
  "one_time": False,
  "buttons":[
    [
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"1\"}",
          "label":"To Ignore"
        },
        "color":"negative"
      },
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"2\"}",
          "label":"Add Favorite"
        },
        "color":"positive"
      },
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"2\"}",
          "label":"Favorites"
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