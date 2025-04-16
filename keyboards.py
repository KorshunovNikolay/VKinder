kb_choice = {
  "one_time": True,
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

kb_start = {
  "one_time": True,
  "buttons":[
    [
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"1\"}",
          "label": "START"
        },
        "color":"primary"
      }
    ]
  ]
}

kb_continue = {
  "one_time": True,
  "buttons":[
    [
      {
        "action":{
          "type":"text",
          "payload":"{\"button\": \"1\"}",
          "label": "CONTINUE"
        },
        "color":"positive"
      }
    ]
  ]
}