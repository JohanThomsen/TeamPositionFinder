def convert_milliseconds(input):
    milliseconds = int((int(input)%1000))
    seconds = int((int(input)/1000)%60)
    minutes = int((int(input)/(1000*60))%60)

    seconds = '0'+str(seconds) if seconds < 10 else str(seconds)
    minutes = '0'+str(minutes) if minutes < 10 else str(minutes)

    returnstring = f'{minutes}:{seconds}.{milliseconds}' if int(minutes) > 0 else F'{seconds}.{milliseconds}'
    return returnstring