def ping_google():
  import os
  param = '-c'
  hostname = "google.com" #example
  response = os.system(f"ping {param} 1 {hostname}")

  #and then check the response...
  if response == 0:
    print(f"{hostname} is up!")
  else:
    print(f"{hostname} is down!")